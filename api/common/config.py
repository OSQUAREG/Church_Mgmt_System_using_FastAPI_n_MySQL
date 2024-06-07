from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    # Database settings
    host: str
    port: str
    password: str
    user: str
    database: str

    # Swagger/Server settings
    dev_prefix: str
    test_prefix: str
    stg_prefix: str
    prod_prefix: str

    # JWT settings
    jwt_secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Email settings
    mail_username: str
    mail_password: str
    mail_from: str
    mail_server: str
    mail_port: int
    mail_from_name: str
    mail_secret_key: str
    mail_token_expire_hours: int

    # importing the environment variables from the .env file
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
