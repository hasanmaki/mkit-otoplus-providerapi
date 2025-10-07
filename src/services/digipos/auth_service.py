from src.custom.exceptions import AuthenticationError
from src.deps import DepDigiposSettings


class DigiposAuthService:
    def __init__(self, setting: DepDigiposSettings):
        self.setting = setting

    def validate_username(self, username: str):
        if username != self.setting.username:
            raise AuthenticationError("Username tidak sesuai")

    def validate_password(self, password: str):
        if password != self.setting.password:
            raise AuthenticationError("Password tidak sesuai")

    def validate_usnpass(self, username: str, password: str):
        self.validate_username(username)
        self.validate_password(password)
