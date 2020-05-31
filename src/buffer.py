import json
import struct
import zlib
import typing
from enum import IntEnum
from dataclasses import dataclass, astuple

__all__ = ['Operation', 'DataPacket']


class Operation(IntEnum):
    HEARTBEAT = 2
    HEARTBEAT_RESPONSE = 3
    NOTIFY = 5
    JOIN = 7
    JOIN_RESPONSE = 8


@dataclass
class DataPacket:
    # https://github.com/lovelyyoshino/Bilibili-Live-API/blob/master/API.WebSocket.md
    packet_length: int = None
    header_length: int = 16
    protocol_version: int = None
    operation: Operation = None
    sequence_id: int = 1
    body: bytes = b''

    def __post_init__(self):
        self.packet_length = 16 + len(self.body)
        if self.operation in [2, 3, 5, 7, 8]:
            self.operation = Operation(self.operation)
        if self.protocol_version is None and self.operation in [Operation.JOIN, Operation.HEARTBEAT]:
            self.protocol_version = 1
        if None in astuple(self):
            raise ValueError(self)

    @classmethod
    def join(cls, room_id) -> "DataPacket":
        return cls(operation=Operation.JOIN, body=json.dumps({
            "uid": 0,
            "roomid": room_id,
            "protover": 2,
            "platform": "web",
            "clientver": "1.8.5",
            "type": 2
        }).encode('utf8'))

    @classmethod
    def decode(cls, buffer: bytes) -> typing.List["DataPacket"]:
        i = 0
        packs: typing.List[DataPacket] = []
        while i < len(buffer):
            size = struct.unpack(f'!i', buffer[i:i + 4])[0]
            pack = cls(*struct.unpack(f'!ihhii{size - 16}s', buffer[i:i + size]))
            i += size
            if pack.protocol_version == 2:
                packs.extend(cls.decode(zlib.decompress(pack.body)))
            else:
                packs.append(pack)
        return packs

    def decode_body(self) -> dict:
        if self.operation == Operation.HEARTBEAT_RESPONSE:
            return {"online": int.from_bytes(self.body, 'big')}
        else:
            return json.loads(self.body.decode())

    def encode(self) -> bytes:
        return struct.pack('!ihhii', *astuple(self)[0:5]) + self.body
