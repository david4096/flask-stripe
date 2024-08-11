import os

class Config:
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    PRICE_ID = os.getenv('PRICE_ID')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
