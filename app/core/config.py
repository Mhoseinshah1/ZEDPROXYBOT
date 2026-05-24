from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ZedProxyBot"
    env: str = "production"
    bot_token: str = ""
    main_admin_id: int = 0
    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_expire_minutes: int = 120
    web_base_url: str = ""
    admin_path: str = "/admin"
    api_path: str = "/api"
    bot_webhook_path: str = "/bot/webhook"
    domain: str = ""
    ssl_enabled: bool = False
    card_number: str = ""
    card_holder_name: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
