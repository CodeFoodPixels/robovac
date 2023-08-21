import asyncio
import json
import logging
from hashlib import md5

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_LOGGER = logging.getLogger(__name__)

UDP_KEY = md5(b"yGAdlopoPVldABfn").digest()


class TuyaLocalDiscovery(asyncio.DatagramProtocol):
    def __init__(self, callback):
        self.devices = {}
        self._listeners = []
        self.discovered_callback = callback

    async def start(self):
        loop = asyncio.get_running_loop()
        listener = loop.create_datagram_endpoint(
            lambda: self, local_addr=("0.0.0.0", 6666)
        )
        encrypted_listener = loop.create_datagram_endpoint(
            lambda: self, local_addr=("0.0.0.0", 6667)
        )

        self._listeners = await asyncio.gather(listener, encrypted_listener)
        _LOGGER.debug("Listening to broadcasts on UDP port 6666 and 6667")

    def close(self, *args, **kwargs):
        for transport, _ in self._listeners:
            transport.close()

    def datagram_received(self, data, addr):
        data = data[20:-8]
        try:
            cipher = Cipher(algorithms.AES(UDP_KEY), modes.ECB(), default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(data) + decryptor.finalize()
            data = padded_data[: -ord(padded_data[len(padded_data) - 1 :])]

        except Exception:
            data = data.decode()

        decoded = json.loads(data)
        asyncio.ensure_future(self.discovered_callback(decoded))
