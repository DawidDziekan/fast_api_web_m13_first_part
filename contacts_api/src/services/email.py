from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from src.config import settings
from src.services.auth import auth_service

# Configuration for the FastMail connection
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

async def send_email(email: EmailStr, username: str, host: str):
    """
    Send an email to the user for email verification.

    - **email**: The recipient's email address.
    - **username**: The username of the recipient.
    - **host**: The host address to be included in the email for verification.

    This function generates an email verification token and sends an email to the user with a link to verify their email address.
    It uses the FastMail library to send the email with the specified template.

    Raises:
    - **ConnectionErrors**: If there are issues connecting to the email server.
    """
    try:
        # Create an email verification token
        token_verification = auth_service.create_email_token({"sub": email})
        
        # Define the email message
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        # Initialize FastMail with the configuration
        fm = FastMail(conf)
        
        # Send the email using the specified template
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)

