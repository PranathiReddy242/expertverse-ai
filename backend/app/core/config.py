from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")
    secret_key: str = Field(..., env="SECRET_KEY")
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
    ollama_enabled: bool = Field(True, env="OLLAMA_ENABLED")
    razorpay_key_id: str | None = Field(None, env="RAZORPAY_KEY_ID")
    razorpay_key_secret: str | None = Field(None, env="RAZORPAY_KEY_SECRET")
    razorpay_webhook_secret: str | None = Field(None, env="RAZORPAY_WEBHOOK_SECRET")
    merchant_upi_id: str | None = Field(None, env="MERCHANT_UPI_ID")
    merchant_payment_url: str | None = Field(None, env="MERCHANT_PAYMENT_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
