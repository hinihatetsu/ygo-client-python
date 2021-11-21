import asyncio
import asyncio.streams
import logging

from .packet import Packet


HEADER_SIZE: int = 2

logger = logging.getLogger(__name__)

class YGOConnection:
    _reader: asyncio.StreamReader
    _writer: asyncio.StreamWriter

        
    def is_connected(self) -> bool:
        if not getattr(self, '_reader', None):
            return False

        if not getattr(self, '_writer', None):
            return False

        return not self._writer.is_closing()
        
   

    async def connect(self, host: str, port: int) -> None:
        self._reader, self._writer = await asyncio.streams.open_connection(host, port)


    async def receive(self) -> Packet:
        if not self.is_connected():
            raise ConnectionError('No connection')

        try:
            header: bytes = await self._reader.readexactly(HEADER_SIZE)
            data_size: int = int.from_bytes(header, byteorder='little')
            if data_size == 0:
                self._writer.close()
                raise ConnectionResetError('Connection has been closed.')
            
            data: bytes = await self._reader.readexactly(data_size)
            packet: Packet = Packet(int.from_bytes(data[0:1], 'little'))
            packet.write_bytes(data[1:])
            return packet
        except ConnectionAbortedError as e:
            self._writer.close()
            raise e



    async def send(self, packet: Packet) -> None:
        if not self.is_connected():
            raise ConnectionError('No connection.')
        
        header: bytes = packet.size.to_bytes(HEADER_SIZE, byteorder='little')
        self._writer.write(header + packet.data)
        await self._writer.drain()
            

    def close(self) -> None:
        if self.is_connected():
            self._writer.close()



if __name__ == '__main__':
    pass
