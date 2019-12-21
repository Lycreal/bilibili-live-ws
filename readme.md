# bilibili-live-ws 

Bilibili 直播 WebSocket/TCP API

[simon300000/bilibili-live-ws](https://github.com/simon300000/bilibili-live-ws)的python3实现

## Class: LiveWS / LiveTCP

### LiveWS(roomid [, address])

### LiveTCP(roomid [, host, port])

- `roomid` 房间号

  比如 https://live.bilibili.com/14327465 中的 `14327465`
  
- `address` 可选, WebSocket连接的地址

  默认 `wss://broadcastlv.chat.bilibili.com/sub`

- `host` 可选, TCP连接的地址

  默认 `broadcastlv.chat.bilibili.com`

- `port` 可选, TCP连接的端口

  默认 `2243`

<hr>

参考资料: <https://github.com/lovelyyoshino/Bilibili-Live-API/blob/master/API.WebSocket.md>
