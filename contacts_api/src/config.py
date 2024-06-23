from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os


load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = os.getenv('DATABASE_URL')
    SECRET_KEY: Optional[str] = os.getenv('SECRET_KEY')
    CLOUDINARY_CLOUD_NAME: Optional[str] = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY: Optional[str] = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET: Optional[str] = os.getenv('CLOUDINARY_API_SECRET')
    MAIL_USERNAME: Optional[str] = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD: Optional[str] = os.getenv('MAIL_PASSWORD')
    MAIL_FROM: Optional[str] = os.getenv('MAIL_FROM')
    MAIL_PORT: Optional[str] = os.getenv('MAIL_PORT')
    MAIL_SERVER: Optional[str] = os.getenv('MAIL_SERVER')
    POSTGRES_USER: Optional[str] = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: Optional[str] = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DB: Optional[str] = os.getenv('POSTGRES_DB')
    REDIS_URL: Optional[str] = os.getenv('REDIS_URL')
    REDIS_HOST: Optional[str] = os.getenv('REDIS_HOST')
    REDIS_PORT: Optional[str] = os.getenv('REDIS_PORT')
    ALGORITHM: Optional[str] = os.getenv('ALGORITHM')


    class Config:
        env_file = ".env"

settings = Settings()

from cloudinary import config as cloudinary_config
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)
