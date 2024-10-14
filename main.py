#!/usr/bin/env python3

from io_utils import StreamSlice
import img4
from asn1 import Tag, tag_to_slice
import hashlib
import sys
import pprint
import io
import argparse
from argparse import BooleanOptionalAction
import traceback
from contextlib import contextmanager
import tables
from typing import Literal

# option parsing

parser = argparse.ArgumentParser(
	prog='img4parse',
	description='Portable IMG4 parser',
)
parser.add_argument('filename', help='input IMG4/IM4M/IM4P file to parse')
parser.add_argument('-C', '--color',
	action=BooleanOptionalAction,
	help='Colorize the output [default: only if stdout is a terminal]')
parser.add_argument('--descriptions',
	action=BooleanOptionalAction, default=True,
	help='Show meanings of recognized 4-character tags and some field values [default: yes]')
parser.add_argument('-D', '--diff',
	action=BooleanOptionalAction, default=False,
	help='Produce diff-friendly output (no offsets, no intermediate lengths or hashes, always calculate final hashes) [default: no]')
parser.add_argument('-H', '--hash-limit',
	type=int, metavar='BYTES',
	help='Maximum blob size for which we calculate and display its hash (-1 = infinity, 0 = never) [default: 50MB, or -1 with --diff]')

args = parser.parse_args()
fname = args.filename
colorize = sys.stdout.buffer.isatty() \
	if args.color == None else args.color
show_desc = args.descriptions
diff = args.diff
hash_limit = args.hash_limit
if hash_limit is None:
	hash_limit = -1 if diff else 50 * 1000000
errors_found = False

if hash_limit == -1: hash_limit = float('inf')
elif hash_limit == 0: hash_limit = -1

# general utils

def ansi_sgr(p: str, content: str):
	content = str(content)
	if not colorize: return content
	if not content.endswith('\x1b[m'):
		content += '\x1b[m'
	return f'\x1b[{p}m' + content
ansi_bold = lambda x: ansi_sgr('1', x)
ansi_dim = lambda x: ansi_sgr('2', x)
ansi_fg0 = lambda x: ansi_sgr('30', x)
ansi_fg1 = lambda x: ansi_sgr('31', x)
ansi_fg2 = lambda x: ansi_sgr('32', x)
ansi_fg3 = lambda x: ansi_sgr('33', x)
ansi_fg4 = lambda x: ansi_sgr('34', x)
ansi_fg5 = lambda x: ansi_sgr('35', x)
ansi_fg6 = lambda x: ansi_sgr('36', x)
ansi_fg7 = lambda x: ansi_sgr('37', x)
ansi_fgB0 = lambda x: ansi_sgr('90', x)
ansi_fgB1 = lambda x: ansi_sgr('91', x)
ansi_fgB2 = lambda x: ansi_sgr('92', x)
ansi_fgB3 = lambda x: ansi_sgr('93', x)
ansi_fgB4 = lambda x: ansi_sgr('94', x)
ansi_fgB5 = lambda x: ansi_sgr('95', x)
ansi_fgB6 = lambda x: ansi_sgr('96', x)
ansi_fgB7 = lambda x: ansi_sgr('97', x)
EQ = ' = '
BAR = ansi_dim(' | ')
BULLET = ' - '
STRING = ansi_fg3
DIGEST = ansi_fg5

@contextmanager
def safe_parse(prefix=''):
	try:
		yield
	except Exception as exc:
		global errors_found
		errors_found = True
		desc = ''.join(traceback.format_exception(exc)).rstrip().replace('\n', '\n' + prefix)
		print(prefix + ansi_bold(ansi_fg1('[ERROR]')) + ' ' + desc, file=sys.stderr)

# formatting

def format_hash(blob: StreamSlice):
	hl = hashlib.sha384()
	blob = StreamSlice(blob.stream, blob.start, blob.end, blob.pos)
	while blob.left:
		hl.update(blob.read(min(blob.left, 65536)))
	return f'sha384 {DIGEST(hl.digest().hex())}'

def print_blob(name: str, blob: StreamSlice, prefix='', intermediate=False):
	if intermediate and diff:
		print(prefix + ansi_bold(name) + ':')
		return
	offset = f' @ {hex(blob.start)}' if not diff else ''
	digest = f', {format_hash(blob)}' if blob.left < hash_limit else ('' if intermediate else ', hash skipped')
	desc = f'{blob.left} bytes' + offset + digest
	if intermediate:
		print(prefix + ansi_bold(name) + f' ({desc}):')
	else:
		print(prefix + name + ': ' + desc)

fourcc_tables = {
	'manb': (tables.component_names, lambda x: x),
	'manp': (tables.payload_tags, lambda x: x[1]),
	'payp': (tables.payp_tags, lambda x: x[1]),
}

def format_4cc(name: str, parent: Literal['manb', 'manp', 'payp', None] = None) -> str:
	if len(name) == 4 and name.isascii() and name.isalnum():
		desc = name
	else:
		desc = repr(name)
	desc = ansi_fgB6(desc)
	if show_desc and parent \
		and (info := fourcc_tables[parent][0].get(name)) \
		and (label := fourcc_tables[parent][1](info)):
		desc += ansi_fg6(f' ({label})')
	return desc

def handle_payp(stream: StreamSlice, prefix=''):
	payp = img4.read_payp(stream)
	for key, value in payp.items():
		print(prefix + BULLET + format_4cc(key, 'payp') + EQ + format_im4m_value(key, value))

def handle_payload(stream: StreamSlice, prefix=''):
	name, desc, payload, kbag, compression, payp = img4.read_im4p(stream)
	print(prefix + 'Name: ' + format_4cc(name, 'manb'))
	print(prefix + 'Description: ' + STRING(repr(desc)))
	print_blob('Payload', payload, prefix)
	if kbag:
		print_blob('KBAG (encryption parameters)', kbag, prefix)
	if compression:
		print_blob('Compression', compression, prefix)
	if payp:
		print(prefix)
		print_blob('PAYP (metadata)', payp, prefix, intermediate=True)
		with safe_parse(prefix + BAR):
			handle_payp(payp, prefix + BAR)

def format_component_tag(key: str, value) -> str:
	if key == 'DGST':
		assert type(value) is bytes
		return DIGEST(value.hex())
	if value is True:
		return format_4cc(key)
	return f'{format_4cc(key)}({format_im4m_value(key, value)})'

def format_im4m_value(key: str, value):
	if type(value) is bytes:
		if value.isascii():
			return STRING(repr(value.decode('ascii')))
		else:
			return DIGEST(f'(hex) {value.hex()}')
	if type(value) is int:
		return ansi_fg2(hex(value) if value >= 100 else value)
	if type(value) is bool:
		return ansi_fg4(value)
	return repr(value)

def handle_manifest_body(body: Tag, prefix=''):
	payload, components = img4.parse_im4m_body(body)
	print(prefix + ansi_bold('Manifest payload:'))
	with safe_parse(prefix + BAR):
		for key, value in payload.items():
			print(prefix + BULLET + format_4cc(key, 'manp') + EQ + format_im4m_value(key, value))
	print(prefix)
	print(prefix + ansi_bold('Manifest components:'))
	with safe_parse(prefix + BAR):
		for key, component in components.items():
			desc = ansi_dim(', ').join(format_component_tag(k, v) for k, v in component.items())
			print(prefix + BULLET + format_4cc(key, 'manb') + EQ + desc)

def handle_manifest(stream: StreamSlice, prefix=''):
	body, signature, certs = img4.read_im4m(stream)
	print_blob('Manifest body', tag_to_slice(body), prefix, intermediate=True)
	handle_manifest_body(body, prefix + '  ')
	print(prefix)
	print(prefix + f'Signature ({len(signature)} bytes): {DIGEST(signature.hex())}')
	print(prefix)
	if not certs:
		print(prefix + f'No certificates.')
	for i, cert in enumerate(certs):
		print_blob(f'Certificate {i+1}', cert, prefix)

def handle_image(stream: StreamSlice):
	payload, manifest = img4.read_img4(stream)
	print_blob('Payload', payload, intermediate=True)
	with safe_parse(BAR):
		handle_payload(payload, BAR)
	print()
	if not manifest:
		print('No manifest present.')
		return
	print_blob('Manifest', manifest, intermediate=True)
	with safe_parse(BAR):
		handle_manifest(manifest, BAR)

# main

def __main__():
	# open input
	stream = sys.stdin.buffer if fname == '-' or fname is None else open(fname, 'rb')
	if not stream.seekable():
		stream = io.BytesIO(stream.read())
	stream = StreamSlice(stream)

	# probe header and invoke appropriate handler

	hdr = img4.read_hdr(stream)[1]
	stream.pos = stream.start

	objs = {
		'IMG4': (handle_image, 'image'),
		'IM4P': (handle_payload, 'payload'),
		'IM4M': (handle_manifest, 'manifest'),
	}
	if hdr not in objs:
		raise AssertionError(f'header {repr(hdr)} unknown')
	fn, label = objs[hdr]
	print(f'Input is an {hdr} ({label}).\n')
	fn(stream)

	# if inner errors were found, communicate that in exit code
	if errors_found:
		print(ansi_fg1('There were parsing errors in subsections.'), file=sys.stderr)
		exit(1)

if __name__ == '__main__':
	__main__()
