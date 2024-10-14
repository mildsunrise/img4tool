from io_utils import StreamSlice
from asn1 import *

# IMG4 parsing

def read_hdr(stream: StreamSlice) -> tuple[StreamSlice, str]:
	root, = read_tags(stream)
	assert root[1][2] is TagType.SEQUENCE
	stream = root[2]
	hdr = read_ia5string(stream)
	return stream, hdr

def read_img4(stream: StreamSlice) -> tuple[StreamSlice, StreamSlice | None]:
	stream, hdr = read_hdr(stream)
	assert hdr == 'IMG4', f'unexpected {repr(hdr)} header'
	payload = tag_to_slice(read_tag(stream))
	manifest = None
	if stream.left:
		manifest_cont, = read_tags(stream)
		assert manifest_cont[1] == (TagClass.CONTEXT_SPECIFIC, True, 0)
		manifest = manifest_cont[2]
	return payload, manifest

def read_im4p(stream: StreamSlice) -> tuple[str, str, StreamSlice, StreamSlice | None, StreamSlice | None, StreamSlice | None]:
	stream, hdr = read_hdr(stream)
	assert hdr == 'IM4P', f'unexpected {repr(hdr)} header'
	name, desc, payload = read_ia5string(stream), read_ia5string(stream), read_octet_string(stream)
	rest = list(read_tags(stream))
	kbag = None
	if rest and rest[0][1] == (TagClass.UNIVERSAL, False, TagType.OCTET_STRING):
		kbag = rest.pop(0)[2]
	compression = None
	if rest and rest[0][1] == (TagClass.UNIVERSAL, True, TagType.SEQUENCE):
		compression = rest.pop(0)[2]
	payp = None
	if rest and rest[0][1] == (TagClass.CONTEXT_SPECIFIC, True, 0):
		payp = rest.pop(0)[2]
	assert not rest, f'leftover tags in payload: {rest}'
	return name, desc, payload, kbag, compression, payp

def read_payp(stream: StreamSlice) -> dict:
	stream, hdr = read_hdr(stream)
	assert hdr == 'PAYP', f'unexpected {repr(hdr)} header'
	body, = read_tags(stream)
	body = decode_im4m_value(body)
	assert type(body) is dict
	return body

def read_im4m(stream: StreamSlice) -> tuple[Tag, bytes, list[StreamSlice]]:
	stream, hdr = read_hdr(stream)
	assert hdr == 'IM4M', f'unexpected {repr(hdr)} header'
	version = read_integer(stream)
	assert version == 0, f'unknown version {version}'
	body = read_tag(stream)
	signature = read_octet_string(stream).read()
	certs, = read_tags(stream)
	assert certs[1] == (TagClass.UNIVERSAL, True, TagType.SEQUENCE)
	certs = list(map(tag_to_slice, read_tags(certs[2])))
	return body, signature, certs

def read_im4m_tag(stream: StreamSlice) -> tuple[str, Tag]:
	priv = read_tag(stream)
	assert priv[1][0] == TagClass.PRIVATE
	assert priv[1][1]
	tname = priv[1][2].to_bytes(4)

	seq, = read_tags(priv[2])
	assert seq[1] == (TagClass.UNIVERSAL, True, TagType.SEQUENCE)
	stream = seq[2]

	name = read_ia5string(stream)
	assert tname == name.encode('ascii')
	payload, = read_tags(stream)
	return name, payload

def decode_im4m_value(tag: Tag):
	if tag[1] == (TagClass.UNIVERSAL, True, TagType.SET):
		entries = []
		while tag[2].left:
			name, subtag = read_im4m_tag(tag[2])
			entries.append((name, decode_im4m_value(subtag)))
		value = dict(entries)
		assert len(entries) == len(value), f'duplicate entries!'
		return value
	elif tag[1] == (TagClass.UNIVERSAL, False, TagType.BOOLEAN):
		return { b'\x00': False, b'\xFF': True }[tag[2].read()]
	elif tag[1] == (TagClass.UNIVERSAL, False, TagType.INTEGER):
		return int.from_bytes(tag[2].read())
	elif tag[1] == (TagClass.UNIVERSAL, False, TagType.OCTET_STRING):
		return tag[2].read()
	# elif tag[1] == (TagClass.UNIVERSAL, False, TagType.IA5String):
	# 	return tag[2].read().decode('ascii')
	else:
		raise AssertionError(f'unexpected type {tag[1]}')
		# return tag

def parse_im4m_body(tag: Tag) -> tuple[dict, dict]:
	body = decode_im4m_value(tag)
	assert type(body) is dict and body.keys() == {'MANB'}
	body = body['MANB']
	assert type(body) is dict
	assert next(iter(body)) == 'MANP'
	payload = body.pop('MANP')
	return payload, body
