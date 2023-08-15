import os

from dotenv import load_dotenv


class Settings:
    url = "https://en.wikipedia.org/wiki/Deaths_in_2023#August"

    load_dotenv()

    sender = os.getenv('SENDER')
    recipient = os.getenv('RECIPIENT')
    smtp_url = os.getenv('SMTP_URL')
    smtp_port = os.getenv('SMTP_PORT')
    login = os.getenv('LOGIN')
    password = os.getenv('PASSWORD')


settings = Settings()
