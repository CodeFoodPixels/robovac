"""Original Work from here: Andre Borie https://gitlab.com/Rjevski/eufy-device-id-and-local-key-grabber"""

from hashlib import md5, sha256
import hmac
import json
import math
import random
import string
import time
import uuid

from cryptography.hazmat.backends.openssl import backend as openssl_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import requests

TUYA_INITIAL_BASE_URL = "https://a1.tuyaeu.com"

EUFY_HMAC_KEY = (
    "A_cepev5pfnhua4dkqkdpmnrdxx378mpjr_s8x78u7xwymasd9kqa7a73pjhxqsedaj".encode()
)


def unpadded_rsa(key_exponent: int, key_n: int, plaintext: bytes) -> bytes:
    keylength = math.ceil(key_n.bit_length() / 8)
    input_nr = int.from_bytes(plaintext, byteorder="big")
    crypted_nr = pow(input_nr, key_exponent, key_n)
    return crypted_nr.to_bytes(keylength, byteorder="big")


def shuffled_md5(value: str) -> str:
    _hash = md5(value.encode("utf-8")).hexdigest()
    return _hash[8:16] + _hash[0:8] + _hash[24:32] + _hash[16:24]


TUYA_PASSWORD_INNER_CIPHER = Cipher(
    algorithms.AES(
        bytearray(
            [36, 78, 109, 138, 86, 172, 135, 145, 36, 67, 45, 139, 108, 188, 162, 196]
        )
    ),
    modes.CBC(
        bytearray(
            [119, 36, 86, 242, 167, 102, 76, 243, 57, 44, 53, 151, 233, 62, 87, 71]
        )
    ),
    backend=openssl_backend,
)

DEFAULT_TUYA_HEADERS = {"User-Agent": "TY-UA=APP/Android/2.4.0/SDK/null"}

SIGNATURE_RELEVANT_PARAMETERS = {
    "a",
    "v",
    "lat",
    "lon",
    "lang",
    "deviceId",
    "appVersion",
    "ttid",
    "isH5",
    "h5Token",
    "os",
    "clientId",
    "postData",
    "time",
    "requestId",
    "et",
    "n4h5",
    "sid",
    "sp",
}

DEFAULT_TUYA_QUERY_PARAMS = {
    "appVersion": "2.4.0",
    "deviceId": "",
    "platform": "sdk_gphone64_arm64",
    "clientId": "yx5v9uc3ef9wg3v9atje",
    "lang": "en",
    "osSystem": "12",
    "os": "Android",
    "timeZoneId": "",
    "ttid": "android",
    "et": "0.0.1",
    "sdkVersion": "3.0.8cAnker",
}


class TuyaAPISession:
    username = None
    country_code = None
    session_id = None

    def __init__(self, username, region, timezone):
        self.session = requests.session()
        self.session.headers = DEFAULT_TUYA_HEADERS.copy()
        self.default_query_params = DEFAULT_TUYA_QUERY_PARAMS.copy()
        self.default_query_params["deviceId"] = self.generate_new_device_id()
        self.username = username
        self.country_code = self.getCountryCode(region)
        self.base_url = {
            "EU": "https://a1.tuyaeu.com",
            "AY": "https://a1.tuyacn.com",
        }.get(region, "https://a1.tuyaus.com")
        DEFAULT_TUYA_QUERY_PARAMS["timeZoneId"] = timezone

    @staticmethod
    def generate_new_device_id():
        expected_length = 44
        base64_characters = string.ascii_letters + string.digits
        device_id_dependent_part = "8534c8ec0ed0"
        return device_id_dependent_part + "".join(
            random.choice(base64_characters)
            for _ in range(expected_length - len(device_id_dependent_part))
        )

    @staticmethod
    def get_signature(query_params: dict, encoded_post_data: str):
        query_params = query_params.copy()
        if encoded_post_data:
            query_params["postData"] = encoded_post_data
        sorted_pairs = sorted(query_params.items())
        filtered_pairs = filter(
            lambda p: p[0] and p[0] in SIGNATURE_RELEVANT_PARAMETERS, sorted_pairs
        )
        mapped_pairs = map(
            # postData is pre-emptively hashed (for performance reasons?), everything else is included as-is
            lambda p: p[0] + "=" + (shuffled_md5(p[1]) if p[0] == "postData" else p[1]),
            filtered_pairs,
        )
        message = "||".join(mapped_pairs)
        return hmac.HMAC(
            key=EUFY_HMAC_KEY, msg=message.encode("utf-8"), digestmod=sha256
        ).hexdigest()

    def _request(
        self,
        action: str,
        version="1.0",
        data: dict = None,
        query_params: dict = None,
        _requires_session=True,
    ):
        if not self.session_id and _requires_session:
            self.acquire_session()

        current_time = time.time()
        request_id = uuid.uuid4()
        extra_query_params = {
            "time": str(int(current_time)),
            "requestId": str(request_id),
            "a": action,
            "v": version,
            **(query_params or {}),
        }
        query_params = {**self.default_query_params, **extra_query_params}
        encoded_post_data = json.dumps(data, separators=(",", ":")) if data else ""
        resp = self.session.post(
            self.base_url + "/api.json",
            params={
                **query_params,
                "sign": self.get_signature(query_params, encoded_post_data),
            },
            data={"postData": encoded_post_data} if encoded_post_data else None,
        )
        resp.raise_for_status()
        data = resp.json()
        if "result" not in data:
            raise Exception(
                f"No 'result' key in the response - the entire response is {data}."
            )
        return data["result"]

    def request_token(self, username, country_code):
        return self._request(
            action="tuya.m.user.uid.token.create",
            data={"uid": username, "countryCode": country_code},
            _requires_session=False,
        )

    def determine_password(self, username: str):
        new_uid = username
        padded_size = 16 * math.ceil(len(new_uid) / 16)
        password_uid = new_uid.zfill(padded_size)
        encryptor = TUYA_PASSWORD_INNER_CIPHER.encryptor()
        encrypted_uid = encryptor.update(password_uid.encode("utf8"))
        encrypted_uid += encryptor.finalize()
        return md5(encrypted_uid.hex().upper().encode("utf-8")).hexdigest()

    def request_session(self, username, password, country_code):
        token_response = self.request_token(username, country_code)
        encrypted_password = unpadded_rsa(
            key_exponent=int(token_response["exponent"]),
            key_n=int(token_response["publicKey"]),
            plaintext=password.encode("utf-8"),
        )
        data = {
            "uid": username,
            "createGroup": True,
            "ifencrypt": 1,
            "passwd": encrypted_password.hex(),
            "countryCode": country_code,
            "options": '{"group": 1}',
            "token": token_response["token"],
        }

        try:
            return self._request(
                action="tuya.m.user.uid.password.login.reg",
                data=data,
                _requires_session=False,
            )
        except Exception as e:
            error_password = md5("12345678".encode("utf8")).hexdigest()

            if password != error_password:
                return self.request_session(username, error_password, country_code)
            else:
                raise e

    def acquire_session(self):
        password = self.determine_password(self.username)
        session_response = self.request_session(
            self.username, password, self.country_code
        )
        self.session_id = self.default_query_params["sid"] = session_response["sid"]
        self.base_url = session_response["domain"]["mobileApiUrl"]
        self.country_code = (
            session_response["phoneCode"]
            if session_response["phoneCode"]
            else self.getCountryCode(session_response["domain"]["regionCode"])
        )

    def list_homes(self):
        return self._request(action="tuya.m.location.list", version="2.1")

    def list_devices(self, home_id: str):
        return self._request(
            action="tuya.m.my.group.device.list",
            version="1.0",
            query_params={"gid": home_id},
        )

    def getCountryCode(self, region_code):
        return {"EU": "44", "AY": "86"}.get(region_code, "1")
