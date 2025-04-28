import os
from builtins import bool, int, str
from pathlib import Path
from pydantic import Field, AnyUrl, DirectoryPath
from pydantic_settings import BaseSettings

# Determine database URL based on environment (CI vs. local)
if os.getenv("CI") == "true":
    DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
else:
    DEFAULT_DATABASE_URL = "postgresql+asyncpg://user:password@postgres/myappdb"

class Settings(BaseSettings):
    max_login_attempts: int = Field(default=3, description="Max login attempts before lockout")

    # Server configuration
    server_base_url: AnyUrl = Field(default='http://localhost', description="Base URL of the server")
    server_download_folder: str = Field(default='downloads', description="Folder for storing downloaded files")

    # Security and authentication configuration
    secret_key: str = Field(default="secret-key", description="Secret key for encryption")
    algorithm: str = Field(default="HS256", description="Algorithm used for encryption")
    access_token_expire_minutes: int = Field(default=30, description="Expiration time for access tokens in minutes")
    admin_user: str = Field(default='admin', description="Default admin username")
    admin_password: str = Field(default='secret', description="Default admin password")
    debug: bool = Field(default=False, description="Debug mode outputs errors and sqlalchemy queries")
    jwt_secret_key: str = "a_very_secret_key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15  # 15 minutes for access token
    refresh_token_expire_minutes: int = 1440  # 24 hours for refresh token

    # Database configuration
    database_url: str = Field(default=DEFAULT_DATABASE_URL, description="URL for connecting to the database")

    # Optional: Construct the SQLAlchemy database URL from components
    postgres_user: str = Field(default='user', description="PostgreSQL username")
    postgres_password: str = Field(default='password', description="PostgreSQL password")
    postgres_server: str = Field(default='localhost', description="PostgreSQL server address")
    postgres_port: str = Field(default='5432', description="PostgreSQL port")
    postgres_db: str = Field(default='myappdb', description="PostgreSQL database name")

    # Discord configuration
    discord_bot_token: str = Field(default='NONE', description="Discord bot token")
    discord_channel_id: int = Field(default=1234567890, description="Default Discord channel ID")

    # Open AI Key
    openai_api_key: str = Field(default='NONE', description="OpenAI API Key")

    # Email settings
    send_real_mail: bool = Field(default=False, description="Use real email service or mock email service")
    smtp_server: str = Field(default='smtp.mailtrap.io', description="SMTP server for sending emails")
    smtp_port: int = Field(default=2525, description="SMTP port")
    smtp_username: str = Field(default='your-mailtrap-username', description="SMTP username")
    smtp_password: str = Field(default='your-mailtrap-password', description="SMTP password")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Instantiate settings to be imported throughout the app
settings = Settings()
