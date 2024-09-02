from enum import IntEnum, unique
from io_utils import StreamSlice

# ASN.1 constants

@unique
class TagClass(IntEnum):
	UNIVERSAL = 0
	'''The type is native to ASN.1'''
	APPLICATION = 1
	'''The type is only valid for one specific application'''
	CONTEXT_SPECIFIC = 2
	'''Meaning of this type depends on the context (such as within a sequence, set or choice)'''
	PRIVATE = 3
	'''Defined in private specifications'''

@unique
class TagType(IntEnum):
	END_OF_CONTENT = 0 # Primitive
	BOOLEAN = 1 # Primitive
	INTEGER = 2 # Primitive
	BIT_STRING = 3 # Both
	OCTET_STRING = 4 # Both
	NULL = 5 # Primitive
	OBJECT_IDENTIFIER = 6 # Primitive
	Object_Descriptor = 7 # Both
	EXTERNAL = 8 # Constructed
	REAL = 9 # Primitive
	ENUMERATED = 10 # Primitive
	EMBEDDED_PDV = 11 # Constructed
	UTF8String = 12 # Both
	RELATIVE_OID = 13 # Primitive
	TIME = 14 # Primitive
	# 15 is reserved
	SEQUENCE = 16 # Constructed
	SET = 17 # Constructed
	NumericString = 18 # Both
	PrintableString = 19 # Both
	T61String = 20 # Both
	VideotexString = 21 # Both
	IA5String = 22 # Both
	UTCTime = 23 # Both
	GeneralizedTime = 24 # Both
	GraphicString = 25 # Both
	VisibleString = 26 # Both
	GeneralString = 27 # Both
	UniversalString = 28 # Both
	CHARACTER_STRING = 29 # Constructed
	BMPString = 30 # Both
	DATE = 31 # Primitive
	TIME_OF_DAY = 32 # Primitive
	DATE_TIME = 33 # Primitive
	DURATION = 34 # Primitive
	OID_IRI = 35 # Primitive
	RELATIVE_OID_IRI = 36 # Primitive

	@classmethod
	def get(cls, x: int) -> 'TagType | int':
		try:
			return cls(x)
		except ValueError:
			return x

# BER primitives

def read_type(stream: StreamSlice):
	octet = stream.read(1)[0]
	tc = octet >> 6
	pc = bool((octet >> 5) & 1)
	tt = octet & ~((~0) << 5)

	if tt == ~((~0) << 5):
		tt = 0
		while True:
			octet = stream.read(1)[0]
			tt = tt << 7 | (octet & ~((~0) << 7))
			if not (octet >> 7): break

	return TagClass(tc), pc, TagType(tt) if not tc else tt

def read_length(stream: StreamSlice):
	octet = stream.read(1)[0]
	if octet < 128:
		return octet # definite short
	if octet == 128:
		return None # indefinite
	if octet < 255:
		return int.from_bytes(stream.read(octet & 127)) # definite long
	raise AssertionError('reserved length encoding')

Tag = tuple[int, tuple[TagClass, bool, int | TagType], StreamSlice]

def read_tag(stream: StreamSlice) -> Tag:
	# indefinite length not supported yet
	return stream.pos, read_type(stream), stream.slice(read_definite_length(stream))

def read_tags(stream: StreamSlice):
	while stream.left:
		yield read_tag(stream)

def tag_to_slice(tag: Tag) -> StreamSlice:
	return StreamSlice(tag[2].stream, tag[0], tag[2].end)

# convenience

def read_definite_length(stream: StreamSlice) -> int:
	length = read_length(stream)
	assert length != None, 'expected definite length'
	return length

def read_primitive_tag(stream: StreamSlice, exp_tt: TagType | int, exp_cls = TagClass.UNIVERSAL) -> StreamSlice:
	exp_typ = exp_cls, False, exp_tt
	typ = read_type(stream)
	assert typ == exp_typ, f'expected {exp_typ}, got {typ}'
	return stream.slice(read_definite_length(stream))

def read_ia5string(stream: StreamSlice) -> str:
	return read_primitive_tag(stream, TagType.IA5String).read().decode('ascii')
def read_octet_string(stream: StreamSlice) -> StreamSlice:
	return read_primitive_tag(stream, TagType.OCTET_STRING)
def read_integer(stream: StreamSlice) -> int:
	return int.from_bytes(read_primitive_tag(stream, TagType.INTEGER).read()) # FIXME: test

