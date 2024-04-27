from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    host: str
    port: str
    password: str
    user: str
    database: str
    jwt_secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # importing the environment variables from the .env file
    class Config:
        env_file = ".env"


settings = Settings()
