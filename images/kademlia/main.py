import sys
import logging
import random
import string
import asyncio
import time
from kademlia.network import Server


def random_string(N):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))


handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)

loop = asyncio.get_event_loop()
loop.set_debug(True)

if len(sys.argv) != 2:

    server = Server()
    loop.run_until_complete(server.listen(7077))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()

else:
    async def run():
        server = Server()
        await server.listen(7077)
        bootstrap_node = (sys.argv[1], 7077)
        await server.bootstrap([bootstrap_node])

        while True:
            time.sleep(3)

            key = random_string(8)

            await server.set(key, random_string(64))
            await server.get(key)
    asyncio.run(run())
