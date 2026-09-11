from typing import Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(
        "postgresql+psycopg://neondb_owner:npg_lDH63iUvdtoW@ep-still-silence-aeq8f3le.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require",
        env="DATABASE_URL"
    )
    secret_key: str = Field("devsecretkey_production_expertverse_ai", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    google_api_key: str | None = Field(None, env="GOOGLE_API_KEY")
    supabase_url: str | None = Field(None, env="SUPABASE_URL")
    supabase_service_role_key: str | None = Field(None, env="SUPABASE_SERVICE_ROLE_KEY")
    groq_api_key: str | None = Field(None, env="GROQ_API_KEY")
    groq_model: str = Field("llama-3.3-70b-versatile", env="GROQ_MODEL")
    groq_api_url: str | None = Field(None, env="GROQ_API_URL")
    groq_ca_bundle: str | None = Field(None, env="GROQ_CA_BUNDLE")
    groq_verify_ssl: bool = Field(True, env="GROQ_VERIFY_SSL")
    ollama_url: str | None = Field("http://localhost:11434", env="OLLAMA_URL")
    ollama_enabled: bool = Field(False, env="OLLAMA_ENABLED")
    razorpay_key_id: str | None = Field("rzp_test_TaPqq4oI6xrr7h", env="RAZORPAY_KEY_ID")
    razorpay_key_secret: str | None = Field("ZYvJ629F6NwaGt0hrU6IItrI", env="RAZORPAY_KEY_SECRET")
    razorpay_webhook_secret: str | None = Field(None, env="RAZORPAY_WEBHOOK_SECRET")
    merchant_upi_id: str | None = Field("pranathitarigonda@razorpay", env="MERCHANT_UPI_ID")
    merchant_payment_url: str | None = Field("https://razorpay.me/@pranathitarigonda", env="MERCHANT_PAYMENT_URL")

    @field_validator("access_token_expire_minutes", mode="before")
    @classmethod
    def parse_expire_minutes(cls, v: Any) -> int:
        if v is None or v == "":
            return 60
        try:
            return int(v)
        except Exception:
            return 60

    @field_validator("groq_verify_ssl", mode="before")
    @classmethod
    def parse_groq_verify_ssl(cls, v: Any) -> bool:
        if v is None or v == "":
            return True
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "t")
        return bool(v)

    @field_validator("ollama_enabled", mode="before")
    @classmethod
    def parse_ollama_enabled(cls, v: Any) -> bool:
        if v is None or v == "":
            return False
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "t")
        return bool(v)

    @field_validator("database_url", "secret_key", "groq_model", "razorpay_key_id", "razorpay_key_secret", "merchant_upi_id", "merchant_payment_url", mode="before")
    @classmethod
    def parse_str_fallbacks(cls, v: Any, info) -> Any:
        if v is None or (isinstance(v, str) and not v.strip()):
            field_name = info.field_name
            defaults = {
                "database_url": "postgresql+psycopg://neondb_owner:npg_lDH63iUvdtoW@ep-still-silence-aeq8f3le.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require",
                "secret_key": "devsecretkey_production_expertverse_ai",
                "groq_model": "llama-3.3-70b-versatile",
                "razorpay_key_id": "rzp_test_TaPqq4oI6xrr7h",
                "razorpay_key_secret": "ZYvJ629F6NwaGt0hrU6IItrI",
                "merchant_upi_id": "pranathitarigonda@razorpay",
                "merchant_payment_url": "https://razorpay.me/@pranathitarigonda",
            }
            return defaults.get(field_name, v)
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
