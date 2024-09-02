import io
import shutil

class StreamSlice:
	def __init__(self, stream: io.FileIO, start = 0, end = -1, pos = -1):
		self.stream = stream
		self.start = start
		if end == -1:
			stream.seek(0, io.SEEK_END)
			end = stream.tell()
		self.end = end
		self.pos = start if pos == -1 else pos

	def __repr__(self):
		args = self.stream, self.start, self.end, self.pos
		if self.pos == self.start: args = args[:-1]
		return f'StreamSlice[{self.left}]' + repr(args)

	@property
	def left(self) -> int:
		return self.end - self.pos

	def _validate_length(self, x = -1) -> int:
		assert type(x) is int and x >= -1
		if x == -1: x = self.left
		if x <= self.left: return x
		raise EOFError(f'want {x}, have {self.left}')

	def peek(self, x: int = -1) -> bytes:
		x = self._validate_length(x)
		self.stream.seek(self.pos)
		out = self.stream.read(x)
		assert len(out) == x, f'expected {x}, got {len(out)}'
		return out

	def read(self, x: int = -1) -> bytes:
		out = self.peek(x)
		self.pos += len(out)
		return out

	def slice(self, x: int = -1) -> 'StreamSlice':
		x = self._validate_length(x)
		out = type(self)(self.stream, self.pos, self.pos + x)
		self.pos += x
		return out

	def copy(self, out: io.FileIO):
		self.stream.seek(self.pos)
		shutil.copyfileobj(self.stream, out, self.left)
