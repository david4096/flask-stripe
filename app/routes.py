import stripe
from flask import request, jsonify, render_template_string
from .services import (
    create_checkout_session,
    create_meter_event,
    retrieve_upcoming_invoice,
    handle_stripe_webhook,
)
from .utils import generate_api_key, hash_api_key, logger

customers = {}
api_keys = {}

def register_routes(app):

    @app.route('/checkout', methods=['POST'])
    def checkout():
        try:
            session = create_checkout_session(
                app.config['PRICE_ID'],
                success_url='http://localhost:8080/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='http://localhost:8080/success',
            )
            return jsonify(session)
        except Exception as e:
            return str(e), 500

    @app.route('/webhook', methods=['POST'])
    def webhook():
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')

        try:
            event = handle_stripe_webhook(payload, sig_header)
            # Process the event here (e.g., subscription created, invoice paid)
        except Exception as e:
            return str(e), 400

        return '', 200

    @app.route('/customer', methods=['GET'])
    def get_customer_info():
        api_key = request.args.get('apiKey')
        hashed_api_key = hash_api_key(api_key)
        customer_id = api_keys.get(hashed_api_key)
        customer = customers.get(customer_id)

        if customer:
            return jsonify(customer)
        else:
            return '', 404

    @app.route('/api', methods=['GET'])
    def api_access():
        api_key = request.args.get('apiKey')

        if not api_key:
            return '', 400

        hashed_api_key = hash_api_key(api_key)
        customer_id = api_keys.get(hashed_api_key)
        customer = customers.get(customer_id)

        if not customer or not customer['active']:
            return '', 403

        try:
            create_meter_event(customer_id)
            return jsonify({'data': 'You made a successful API request', 'customerId': customer_id})
        except Exception as e:
            return str(e), 500

    @app.route('/usage', methods=['GET'])
    def get_customer_usage():
        api_key = request.args.get('apiKey')
        hashed_api_key = hash_api_key(api_key)
        customer_id = api_keys.get(hashed_api_key)

        try:
            invoice = retrieve_upcoming_invoice(customer_id)
            return jsonify(invoice)
        except Exception as e:
            return str(e), 500

    @app.route('/success', methods=['GET'])
    def success():
        try:
            session = stripe.checkout.Session.retrieve(request.args.get('session_id'))
            customer = stripe.Customer.retrieve(session.customer)
            customer_id = session.customer

            api_key, hashed_api_key = generate_api_key()
            customers[customer_id] = {'apiKey': hashed_api_key, 'active': True}
            api_keys[hashed_api_key] = customer_id

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
            return str(e), 500
