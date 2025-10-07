from src.config.settings import DigiposConfig
from src.custom.exceptions import AuthenticationError


class DigiposAuthService:
    def __init__(self, setting: DigiposConfig):
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
