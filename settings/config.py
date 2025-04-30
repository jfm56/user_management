import os
from builtins import bool, int, str
from pathlib import Path
from pydantic import Field, AnyUrl, DirectoryPath
from pydantic_settings import BaseSettings

DEFAULT_DATABASE_URL = "postgresql+asyncpg://user:password@postgres/myappdb"

class Settings(BaseSettings):
    ci: bool = Field(default=False, description="Running in CI environment")
    database_url: str = Field(default="", description="Database URL")

    def get_resolved_database_url(self) -> str:
        if self.ci:
            return "sqlite+aiosqlite:///:memory:"
        if self.database_url:
            return self.database_url
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"

    max_login_attempts: int = Field(default=3, description="Max login attempts before lockout")

    server_base_url: str = Field(default="http://localhost:8000", description="Base URL of the server")
    server_download_folder: str = Field(default='downloads', description="Folder for storing downloaded files")

    secret_key: str = Field(default="secret-key", description="Secret key for encryption")
    algorithm: str = Field(default="HS256", description="Algorithm used for encryption")
    access_token_expire_minutes: int = Field(default=15, description="Access token expiry")
    refresh_token_expire_minutes: int = Field(default=1440, description="Refresh token expiry")
    admin_user: str = Field(default='admin', description="Default admin username")
    admin_password: str = Field(default='secret', description="Default admin password")
    debug: bool = Field(default=False, description="Debug mode outputs errors and SQL logs")
    jwt_secret_key: str = "a_very_secret_key"
    jwt_algorithm: str = "HS256"

    postgres_user: str = Field(default='user', description="PostgreSQL username")
    postgres_password: str = Field(default='password', description="PostgreSQL password")
    postgres_server: str = Field(default='localhost', description="PostgreSQL server address")
    postgres_port: str = Field(default='5432', description="PostgreSQL port")
    postgres_db: str = Field(default='myappdb', description="PostgreSQL database name")

    discord_bot_token: str = Field(default='NONE', description="Discord bot token")
    discord_channel_id: int = Field(default=1234567890, description="Discord channel ID")

    openai_api_key: str = Field(default='NONE', description="OpenAI API Key")

    send_real_mail: bool = Field(default=False, description="Use real email service or mock email service")
    smtp_server: str = Field(default='smtp.mailtrap.io', description="SMTP server for sending emails")
    smtp_port: int = Field(default=2525, description="SMTP port")
    smtp_username: str = Field(default='your-mailtrap-username', description="SMTP username")
    smtp_password: str = Field(default='your-mailtrap-password', description="SMTP password")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# ✅ Instantiate settings before usage
settings = Settings()

# ✅ Now safe to print
print("Connecting to DB:", settings.get_resolved_database_url())
