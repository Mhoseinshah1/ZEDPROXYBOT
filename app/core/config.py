from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ZedProxyBot"
    env: str = "production"
    secret_key: str
    admin_jwt_exp_minutes: int = 1440

    bot_token: str
    admin_telegram_id: int
    use_webhook: bool = False
    webhook_url: str | None = None
    webhook_path: str = "/bot/webhook"

    database_url: str
    redis_url: str

    admin_path: str = "/admin"
    api_path: str = "/api"
    report_chat_id: str | None = None
    report_enabled: bool = False


settings = Settings()
