import json
import struct
import zlib
import typing
from dataclasses import dataclass, astuple

__all__ = ['RawDataPacket', 'DataPacket']


@dataclass
class RawDataPacket:
    # https://github.com/lovelyyoshino/Bilibili-Live-API/blob/master/API.WebSocket.md
    Packet_Length: int = None
    Header_Length: int = 16
    Protocol_Version: int = 1
    Operation: int = None
    Sequence_Id: int = 1
    body: bytes = b''

    @staticmethod
    def split(buffer: bytes):
        raw_packs: typing.List[bytes] = []
        i = 0
        while i < len(buffer):
            size = struct.unpack(f'!i', buffer[i:i + 4])[0]
            raw_packs.append(buffer[i:i + size])
            i += size
        del i, size
        return raw_packs

    @classmethod
    def decode(cls, buffer: bytes):
        raw_packs = cls.split(buffer)
        packs = []
        for buf in raw_packs:
            pack = cls(*struct.unpack(f'!ihhii{len(buf) - 16}s', buf))
            type_ = ''
            if pack.Operation == 3:
                type_ = 'heartbeat'
            elif pack.Operation == 5:
                type_ = 'message'
            elif pack.Operation == 8:
                type_ = 'welcome'
            data = ''
            if pack.Protocol_Version == 0:
                data = json.dumps(json.loads(pack.body.decode()), ensure_ascii=False)
            elif pack.Protocol_Version == 1 and len(pack.body) == 4:
                data = struct.unpack('!i', pack.body)[0]
            elif pack.Protocol_Version == 2:
                return cls.decode(zlib.decompress(pack.body))
            packs.append(DataPacket(type_, data))
        return packs

    def encode(self):
        self.Packet_Length = 16 + len(self.body)
        return struct.pack('!ihhii', *astuple(self)[0:5]) + self.body


@dataclass
class DataPacket:
    type_: str = ''
    data: str = ''

    def __post_init__(self):
        if type(self.data) in [int, dict]:
            self.data = json.dumps(self.data, ensure_ascii=False)

    def encode(self):
        op = None
        if self.type_ == 'heartbeat':
            op = 2
        elif self.type_ == 'join':
            op = 7

        body = self.data.encode()
        return RawDataPacket(Operation=op, body=body).encode()
