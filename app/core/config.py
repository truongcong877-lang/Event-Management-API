from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Event Management API"
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/event_db"
    SECRET_KEY: str = "Xk9#mP2$vL7!qR4w"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
