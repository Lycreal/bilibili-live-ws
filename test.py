import asyncio
from src import LiveTCP, LiveWS

if __name__ == '__main__':
    # aqua = LiveTCP(14917277)
    aqua = LiveWS(14917277)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(aqua.connect())
    loop.run_until_complete(aqua.open())
    loop.create_task(aqua.keep_alive())
    loop.create_task(aqua.listen())
    loop.run_forever()
