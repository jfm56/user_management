from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    smtp_server: str = "localhost"
    smtp_port: int = 25
    smtp_username: str = ""
    smtp_password: str = ""
    server_base_url: str = "http://localhost"
    debug: bool = False
    send_real_mail: str = "false"
    max_login_attempts: int = 5
    access_token_expire_minutes: int = 30
    jwt_secret_key: str = "changeme"
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_resolved_database_url(self) -> str:
        # Ensure asyncpg driver is used
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        return self.database_url

# Shared settings instance
settings = Settings()