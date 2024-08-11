from flask import Flask, request, jsonify, render_template_string
import stripe
import hashlib
import os
import logging
import json

app = Flask(__name__)

# Set your secret key. Replace with your actual secret key.
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
PRICE_ID = os.getenv('PRICE_ID')

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Fake database for demonstration
customers = {
    'stripeCustomerId': {'apiKey': '123xyz', 'active': False, 'itemId': 'stripeSubscriptionItemId'}
}

api_keys = {
    'hashedApiKey': 'stripeCustomerId'
}

def generate_api_key():
    """
    Generate a unique API key and its hashed version.

    This function creates a new API key using random bytes, hashes it with SHA-256,
    and checks for any potential collision in the existing API keys.

    Returns:
        tuple: A tuple containing the generated API key and its hashed version.
    """
    logger.info("Generating new API key")
    api_key = os.urandom(16).hex()
    hashed_api_key = hash_api_key(api_key)

    if hashed_api_key in api_keys:
        logger.warning(f"Collision detected for API key hash: {hashed_api_key}. Regenerating...")
        return generate_api_key()
    else:
        logger.info(f"Generated API key: {api_key} with hash: {hashed_api_key}")
        return api_key, hashed_api_key

def hash_api_key(api_key):
    """
    Hash an API key using SHA-256.

    Args:
        api_key (str): The API key to hash.

    Returns:
        str: The hashed API key.
    """
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    logger.debug(f"Hashed API key: {hashed_key}")
    return hashed_key

@app.route('/checkout', methods=['POST'])
def create_checkout_session():
    """
    Create a Stripe checkout session.

    This endpoint initiates a checkout session for a subscription using Stripe's API.

    Returns:
        Response: A JSON response containing the checkout session details, or an error message.
    """
    try:
        session = stripe.checkout.Session.create(
            mode='subscription',
            payment_method_types=['card'],
            line_items=[{
                'price': PRICE_ID,
            }],
            success_url='http://localhost:8080/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:8080/success',
        )
        logger.info(f"Checkout session created: {session['id']}")
        return jsonify(session)
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        return str(e), 500

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events.

    This endpoint processes webhook events sent by Stripe, such as subscription creation
    or invoice payment status updates.

    Returns:
        Response: An empty 200 response if the event is handled successfully, or a 400 error response.
    """
    payload = json.loads(request.get_data())
    logger.info(f"Webhook payload: {payload}")
    sig_header = request.headers.get('Stripe-Signature')
    logger.info(f"Signature header: {sig_header}")
    event = None

    try:
        event = stripe.Event.construct_from(
            payload, stripe.api_key)
        logger.info(f"Webhook event received: {event['type']}")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        return 'Webhook signature verification failed.', 400

    # Handle the event
    event_type = event['type']
    data = event['data']

    if event_type == 'customer.subscription.created':
        logger.info(f"Customer subscription created")
        logger.info(f"Customer subscription: {data}")
        customer_id = data['object']['customer']
        print(request.headers)

        #subscription = stripe.Subscription.retrieve(subscription_id)
        item_id = data['object']['items']['data'][0]['id']

    elif event_type == 'invoice.paid':
        logger.info(f"Invoice paid event received for customer {data['object']['customer']}")
        # Handle successful invoice payment

    elif event_type == 'invoice.payment_failed':
        logger.warning(f"Invoice payment failed for customer {data['object']['customer']}")
        # Handle failed invoice payment

    return '', 200

@app.route('/customer', methods=['GET'])
def get_customer_info():
    """
    Retrieve customer information based on API key.

    This endpoint retrieves customer information from the fake database using
    the provided API key.

    Returns:
        Response: A JSON response containing the customer information, or a 404 error if not found.
    """
    api_key = request.args.get('apiKey')
    hashed_api_key = hash_api_key(api_key)
    customer_id = api_keys.get(hashed_api_key)
    customer = customers.get(customer_id)
    if customer:
        logger.info(f"Retrieved customer info for {customer_id}")
        return jsonify(customer)
    else:
        logger.warning(f"Customer {customer_id} not found")
        return '', 404

@app.route('/api', methods=['GET'])
def api_access():
    """
    Provide API access to authenticated customers.

    This endpoint checks the validity of the provided API key and returns
    a JSON response with data if the customer is active.

    Returns:
        Response: A JSON response containing data if the API key is valid, or an error response.
    """
    api_key = request.args.get('apiKey')

    if not api_key:
        logger.error("API key not provided in request")
        return '', 400

    hashed_api_key = hash_api_key(api_key)
    customer_id = api_keys.get(hashed_api_key)
    customer = customers.get(customer_id)

    if not customer or not customer['active']:
        logger.warning(f"Access denied for API key: {api_key}")
        return '', 403
    else:
        try:
            # this is blocking and kind of slow
            stripe.billing.MeterEvent.create(
                event_name="api_requests",
                payload={"value": "1", "stripe_customer_id": customer_id},
            )
            return jsonify({'data': 'You made a successful API request', 'customerId': customer_id})
        except Exception as e:
            logger.error(f"Failed to respond: {e}")
            return str(e), 500

@app.route('/usage', methods=['GET'])
def get_customer_usage():
    """
    Retrieve customer's usage data.

    This endpoint retrieves the upcoming Stripe invoice for the customer
    based on the provided API key.

    Returns:
        Response: A JSON response containing the upcoming invoice details, or an error response.
    """
    api_key = request.args.get('apiKey')
    hashed_api_key = hash_api_key(api_key)
    customer_id = api_keys.get(hashed_api_key)
    try:
        invoice = stripe.Invoice.upcoming(customer=customer_id)
        logger.info(f"Retrieved upcoming invoice for customer {customer_id}")
        return jsonify(invoice)
    except Exception as e:
        logger.error(f"Failed to retrieve usage for customer {customer_id}: {e}")
        return str(e), 500

@app.route('/success', methods=['GET'])
def success():
    """
    Handle the success page after checkout.

    This endpoint serves a static HTML page to the customer after a successful
    checkout session, displaying their API key.

    Returns:
        Response: A rendered HTML page or an error message if an exception occurs.
    """
    try:
        logger.info("Serving static HTML page")
        session = stripe.checkout.Session.retrieve(request.args.get('session_id'))
        customer = stripe.Customer.retrieve(session.customer)
        customer_id = session.customer

        # Generate API key
        api_key, hashed_api_key = generate_api_key()
        customers[customer_id] = {
            'apiKey': hashed_api_key,
            'active': True
        }
        api_keys[hashed_api_key] = customer_id

        logger.info(f"Customer {customer_id} subscribed to plan")
        logger.info(f"User's API Key: {api_key} | Hashed API Key: {hashed_api_key}")

        return render_template_string("""
            <html>
            <body>
            <h1>Thanks for your order, {{customer.name}}!</h1>
            <h3>Your API key is: <pre>{{api_key}}</pre></h3>
            </body>
            </html>""",
            customer=customer,
            api_key=api_key)

    except Exception as e:
        logger.error(f"Failed to serve static page: {e}")
        return str(e), 500

if __name__ == '__main__':
    logger.info("Starting Flask server on port 8080")
    app.run(port=8080, debug=True)
