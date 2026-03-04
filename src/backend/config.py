from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours
    FRONTEND_URL: str = "http://localhost:5173"
    DATABASE_URL: str = "sqlite:///./workmate.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
