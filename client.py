import requests

# Replace with the URL where your Flask app is running
BASE_URL = 'http://localhost:8080'

# 1. Create a checkout session
def create_checkout_session():
    url = f"{BASE_URL}/checkout"
    response = requests.post(url)
    if response.status_code == 200:
        session = response.json()
        print(f"Checkout session created: {session['id']}")
        print(session)
        return session
    else:
        print(f"Failed to create checkout session: {response.status_code}, {response.text}")

# 2. Simulate API call with API key
def call_api(api_key):
    url = f"{BASE_URL}/api?apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"API Call Success: {data}")
        return data
    else:
        print(f"API Call Failed: {response.status_code}, {response.text}")
        return response.text

# 3. Retrieve customer information
def get_customer_info(api_key):
    url = f"{BASE_URL}/customer?apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        customer_info = response.json()
        print(f"Customer Info: {customer_info}")
    else:
        print(f"Failed to retrieve customer info: {response.status_code}, {response.text}")

# 4. Retrieve usage data for a specific customer
def get_customer_usage(api_key):
    url = f"{BASE_URL}/usage?apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        usage_info = response.json()
        print(f"Customer Usage Info: {usage_info}")
        return usage_info
    else:
        print(f"Failed to retrieve usage info: {response.status_code}, {response.text}")

if __name__ == '__main__':
    # Step 1: Create a checkout session
    print('Checking out')
    checkout = create_checkout_session()
    print(checkout)
    # Example API key to simulate the API call
    # In a real case, this would be retrieved from the Stripe webhook handling
    print('enter API key')
    api_key = input()

    # Step 2: Call the API with the provided API key
    print('calling API')
    api_call = call_api(api_key)

    # Example customer ID for retrieving customer info
    # In a real case, this would be retrieved from your Stripe customer data
    print('customer id')
    customer_id = api_call['customerId']
    print(customer_id)

    # Step 3: Get customer information
    print('customer info')
    get_customer_info(api_key)

    # Step 4: Get customer usage data
    print('customer usage')
    usage_info = get_customer_usage(api_key)
    print(usage_info['total'])

    # Step 5: Repeatedly call API
    [call_api(api_key) for x in range(100)]
    usage_info = get_customer_usage(api_key)
    print(usage_info['total'])
