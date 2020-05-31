import asyncio
from abc import abstractmethod
from buffer import DataPacket, Operation

__all__ = ['LiveTCP', 'LiveWS']


class Live:
    def __init__(self, rid):
        self.rid = rid  # room_id
        self.online = 0

    @abstractmethod
    async def send(self, data: bytes):
        raise NotImplementedError

    @abstractmethod
    async def recv(self) -> bytes:
        raise NotImplementedError

    async def open(self):
        await self.send(DataPacket.join(self.rid).encode())

    async def keep_alive(self):
        while True:
            await self.send(DataPacket(operation=Operation.HEARTBEAT).encode())
            await asyncio.sleep(30)

    async def listen(self):
        while True:
            recv_bytes: bytes = await self.recv()
            for pack in DataPacket.decode(recv_bytes):
                print(pack.decode_body())


class LiveTCP(Live):
    writer: asyncio.StreamWriter
    reader: asyncio.StreamReader

    async def connect(self, host='broadcastlv.chat.bilibili.com', port=2243):
        self.reader, self.writer = await asyncio.open_connection(host, port)

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def send(self, data: bytes):
        self.writer.write(data)

    async def recv(self) -> bytes:
        pack = b''
        while len(pack) < 4:
            pack += await self.reader.read(4 - len(pack))
        size = int.from_bytes(pack, 'big')
        while len(pack) < size:
            pack += await self.reader.read(size - len(pack))
        return pack


class LiveWS(Live):
    import websockets
    socket: websockets.WebSocketClientProtocol

    async def connect(self, address='wss://broadcastlv.chat.bilibili.com:2245/sub'):
        self.socket = await self.websockets.connect(address)

    async def close(self):
        await self.socket.close()

    async def send(self, *args):
        await self.socket.send(*args)

    async def recv(self) -> bytes:
        data = await self.socket.recv()
        return data.encode() if isinstance(data, str) else data
