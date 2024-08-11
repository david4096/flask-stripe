# Flask Stripe API

This Flask application provides a simple API for handling Stripe subscriptions, customer management, and API key generation. The application uses Flask as the web framework and Stripe for managing payments and subscriptions.

## Features

- **Checkout Session**: Create a Stripe checkout session for subscriptions.
- **Stripe Webhook**: Handle Stripe webhook events, including subscription creation, invoice payment, and payment failure.
- **Customer Management**: Retrieve customer information and manage API keys.
- **API Access**: Secure API access using customer-specific API keys.
- **Customer Usage**: Retrieve upcoming invoice information for customers.
- **Success Page**: Serve a success page displaying the customer's API key after subscription.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/flask-stripe-api.git
    cd flask-stripe-api
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up environment variables:**
    Create a `.env` file in the project root and add your Stripe secret key and webhook secret key:
    ```
    STRIPE_SECRET_KEY=your_stripe_secret_key
    WEBHOOK_KEY=your_webhook_secret_key
    ```

4. **Run the Flask application:**
    ```bash
    python app.py
    ```

## API Endpoints

### 1. Create Checkout Session

**Endpoint:** `/checkout`  
**Method:** `POST`

- Initiates a Stripe checkout session for a subscription.

**Response:**
- JSON object containing the Stripe checkout session details.

### 2. Stripe Webhook

**Endpoint:** `/webhook`  
**Method:** `POST`

- Receives and handles Stripe webhook events.

### 3. Get Customer Information

**Endpoint:** `/customer`  
**Method:** `GET`

- Retrieves customer information using the provided API key.

**Parameters:**
- `apiKey`: The API key for accessing customer information.

### 4. API Access

**Endpoint:** `/api`  
**Method:** `GET`

- Secures API access using customer-specific API keys.

**Parameters:**
- `apiKey`: The API key for accessing the API.

**Response:**
- JSON object containing data if the API key is valid and active.

### 5. Get Customer Usage

**Endpoint:** `/usage`  
**Method:** `GET`

- Retrieves upcoming invoice information for a customer.

**Parameters:**
- `apiKey`: The API key for accessing customer usage.

**Response:**
- JSON object containing the upcoming invoice details.

### 6. Success Page

**Endpoint:** `/success`  
**Method:** `GET`

- Displays a success page after a customer completes their subscription.

**Parameters:**
- `session_id`: The Stripe session ID retrieved from the checkout session.

**Response:**
- HTML page displaying the customer's name and generated API key.

## Logging

- The application logs events, errors, and warnings using Python's `logging` library.
- Logs are displayed in the console with timestamps, log levels, and messages.

## Notes

- The application uses a simple in-memory database (`customers` and `api_keys` dictionaries) to store customer information and API keys for demonstration purposes. In a production environment, this should be replaced with a persistent database.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
