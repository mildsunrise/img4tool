#!/usr/bin/env python3

from io_utils import StreamSlice
import img4
import hashlib
import sys
import pprint
import io

def format_4cc(name: str) -> str:
	if len(name) == 4 and name.isascii() and name.isalnum():
		return name
	return repr(name)

def handle_payload(stream: StreamSlice, prefix=''):
	name, desc, payload, rest = img4.read_im4p(stream)
	print(prefix + f'name = {format_4cc(name)}')
	print(prefix + f'desc = {repr(desc)}')
	print(prefix + f'payload = {repr(payload)}')
	# TODO: rest

def format_component_tag(key: str, value) -> str:
	if key == 'DGST':
		assert type(value) is bytes
		return repr(value.hex())
	if value is True:
		return format_4cc(key)
	return f'{format_4cc(key)}({format_im4m_value(key, value)})'

def format_im4m_value(key: str, value):
	if type(value) is bytes:
		if value.isascii():
			return repr(value.decode('ascii'))
		else:
			return f'(hex) {value.hex()}'
	if type(value) is int and value >= 100:
		return hex(value)
	return repr(value)

def handle_manifest(stream: StreamSlice, prefix=''):
	body, signature, certs = img4.read_im4m(stream)
	payload, components = img4.parse_im4m_body(body)
	print(prefix + 'Manifest payload:')
	for key, value in payload.items():
		print(prefix + f' - {format_4cc(key)} = {format_im4m_value(key, value)}')
	print(prefix)
	print(prefix + 'Manifest components:')
	for key, component in components.items():
		desc = ', '.join(format_component_tag(k, v) for k, v in component.items())
		print(prefix + f' - {format_4cc(key)} = {desc}')
	print(prefix)
	print(prefix + f'Signature ({len(signature)*8} bits): {signature.hex()}')
	print(prefix)
	print(prefix + f'{len(certs)} certificates: {[ (st.start, st.left) for st in certs ]}')

def handle_image(stream: StreamSlice):
	payload, manifest = img4.read_img4(stream)
	print('Payload:')
	handle_payload(payload, ' | ')
	print()
	if manifest:
		print('Manifest present:')
		handle_manifest(manifest, ' | ')
	else:
		print('No manifest present.')

def __main__():
	# open input
	stream = sys.stdin.buffer
	if not stream.seekable():
		stream = io.BytesIO(stream.read())
	stream = StreamSlice(stream)

	# probe header and invoke appropriate handler

	hdr = img4.read_hdr(stream)[1]
	stream.pos = stream.start

	objs = {
		'IMG4': handle_image,
		'IM4P': handle_payload,
		'IM4M': handle_manifest,
	}
	if hdr not in objs:
		raise AssertionError(f'header {repr(hdr)} unknown')
	print(f'Input is an {hdr}.\n')
	objs[hdr](stream)

if __name__ == '__main__':
	__main__()
