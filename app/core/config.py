from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = 'ZedProxyBot'
    env: str = 'production'
    bot_token: str = ''
    main_admin_id: int = 0
    admin_username: str = 'main_admin'
    admin_password: str = ''
    jwt_secret: str = ''
    jwt_expire_minutes: int = 120
    database_url: str
    redis_url: str
    domain: str = ''
    web_base_url: str = ''
    use_webhook: bool = False
    bot_webhook_path: str = '/bot/webhook'
    admin_path: str = '/admin'
    api_path: str = '/api'
    card_number: str = ''
    card_holder: str = ''
    k2k_enabled: bool = True
    report_group_chat_id: str = ''
    report_group_enabled: bool = False
    force_join_enabled: bool = False
    force_phone_enabled: bool = False


settings = Settings()
