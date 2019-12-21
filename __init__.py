import asyncio
import struct
from buffer import *

__all__ = ['LiveTCP', 'LiveWS']


class Live:
    rid: int
    online = 0

    def __init__(self, rid):
        self.rid = rid  # room_id
        self.online = 0

    def send(self, data):
        pass

    async def recv(self):
        return b''

    async def open(self):
        dic = {
            "type_": "join",
            "data": {
                "uid": 0,
                "roomid": self.rid,
                "protover": 2,
                "platform": "web",
                "clientver": "1.8.5",
                "type": 2
            }
        }
        await self.send(DataPacket(**dic).encode())

    async def heartbeat(self):
        await self.send(DataPacket(type_='heartbeat').encode())

    async def keep_alive(self):
        while True:
            await self.heartbeat()
            await asyncio.sleep(30)

    async def listen(self):
        while True:
            recv_bytes = await self.recv()
            print(RawDataPacket.decode(recv_bytes))


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

    async def recv(self):
        pack = b''
        while len(pack) < 4:
            pack += await self.reader.read(4 - len(pack))
        size = struct.unpack('!i', pack)[0]
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

    async def recv(self):
        return await self.socket.recv()


async def test_main():
    aqua = LiveWS(14917277)
    await aqua.connect()
    await aqua.open()

    await asyncio.gather(
        aqua.keep_alive(),
        aqua.listen()
    )


if __name__ == '__main__':
    asyncio.run(test_main())
