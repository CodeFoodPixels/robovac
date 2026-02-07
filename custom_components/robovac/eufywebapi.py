"""Original Work from here: Andre Borie https://gitlab.com/Rjevski/eufy-device-id-and-local-key-grabber"""

import requests

eufyheaders = {
    "User-Agent": "EufyHome-Android-2.4.0",
    "timezone": "Europe/London",
    "category": "Home",
    "token": "",
    "uid": "",
    "openudid": "sdk_gphone64_arm64",
    "clientType": "2",
    "language": "en",
    "country": "US",
    "Accept-Encoding": "gzip",
}


class EufyLogon:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_user_info(self):
        login_url = "https://home-api.eufylife.com/v1/user/email/login"
        login_auth = {
            "client_Secret": "GQCpr9dSp3uQpsOMgJ4xQ",
            "client_id": "eufyhome-app",
            "email": self.username,
            "password": self.password,
        }

        return requests.post(login_url, json=login_auth, headers=eufyheaders)

    def get_user_settings(self, url, userid, token):
        setting_url = url + "/v1/user/setting"
        eufyheaders["token"] = token
        eufyheaders["id"] = userid
        return requests.request("GET", setting_url, headers=eufyheaders, timeout=1.5)

    def get_device_info(self, url, userid, token):
        device_url = url + "/v1/device/v2"
        eufyheaders["token"] = token
        eufyheaders["id"] = userid
        return requests.request("GET", device_url, headers=eufyheaders)
