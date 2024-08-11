import stripe
from .utils import logger
from .config import Config

stripe.api_key = Config.STRIPE_SECRET_KEY

def create_checkout_session(price_id, success_url, cancel_url):
    try:
        session = stripe.checkout.Session.create(
            mode='subscription',
            payment_method_types=['card'],
            line_items=[{'price': price_id}],
            success_url=success_url,
            cancel_url=cancel_url,
        )
        logger.info(f"Checkout session created: {session['id']}")
        return session
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise e

def create_meter_event(customer_id):
    try:
        stripe.billing.MeterEvent.create(
            event_name="api_requests",
            payload={"value": "1", "stripe_customer_id": customer_id},
        )
    except Exception as e:
        logger.error(f"Failed to create meter event: {e}")
        raise e

def retrieve_upcoming_invoice(customer_id):
    try:
        invoice = stripe.Invoice.upcoming(customer=customer_id)
        logger.info(f"Retrieved upcoming invoice for customer {customer_id}")
        return invoice
    except Exception as e:
        logger.error(f"Failed to retrieve usage for customer {customer_id}: {e}")
        raise e

def handle_stripe_webhook(payload, sig_header):
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
        logger.info(f"Webhook event received: {event['type']}")
        return event
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise e
