
from ygo_core.enums import Phase
from ygo_core.card import Location, Position

MAX_PACKET_SIZE: int = 0xffff

class Packet:
    _msg_id: int
    _content: bytes = b''
    _position: int = 0

    def __init__(self, msg_id: int):
        self._msg_id = msg_id

    
    @property
    def msg_id(self) -> int:
        return self._msg_id


    @property
    def content(self) -> bytes:
        return self._content


    @property
    def data(self) -> bytes:
        _msg_id_bytes: bytes = self.msg_id.to_bytes(1, byteorder='little')
        return _msg_id_bytes + self.content


    @property
    def size(self) -> int:
        return len(self.data)

    
    def write_bytes(self, content: bytes) -> None:
        if self.size + len(content) > MAX_PACKET_SIZE:
            raise ValueError(f"""
                Cannot write content because becoming too large packet. 
                Current Size: {self.size}. 
                Content Size: {len(content)}.
                Max Packet Size: {MAX_PACKET_SIZE}.
                """
            )
        self._content += content


    def write_bytearray(self, content: bytearray) -> None:
        self.write_bytes(bytes(content))

    
    def write_str(self, content: str, byte_size: int=4) -> None:
        encoded: bytes = content.encode(encoding='utf-16-le')
        if len(encoded) <= byte_size:
            self.write_bytes(encoded + bytes(byte_size-len(encoded)))
        else:
            self.write_bytes(encoded[:byte_size])


    def write_int(self, content: int, byte_size: int=4) -> None:
        if content < 0:
            content += 1 << (byte_size * 8)
        self.write_bytes(content.to_bytes(byte_size, byteorder='little'))

        
    def write_bool(self, content: bool) -> None:
        self.write_bytes(int(content).to_bytes(1, byteorder='little'))
    

    def read_bytes(self, n: int) -> bytes:
        res: bytes = self._content[self._position:self._position+n]
        self._position += n
        return res


    def read_int(self, n: int) -> int:
        return int.from_bytes(self.read_bytes(n), byteorder='little')


    def read_bool(self) -> bool:
        return bool(self.read_int(1))


    def read_str(self, n: int) -> str:
        try:
            return self.read_bytes(n).decode(encoding='utf-16-le')
        except UnicodeDecodeError:
            return ''


    def read_id(self) -> int:
        return self.read_int(4)


    def read_location(self) -> Location:
        return Location(self.read_int(1))


    def read_position(self) -> Position:
        return Position(self.read_int(4))


    def read_phase(self) -> Phase:
        return Phase(self.read_int(4))


    def __repr__(self) -> str:
        return f'<msg_id: {self.msg_id}>' + self._content.hex(' ')


    
