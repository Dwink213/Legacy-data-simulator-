"""
REST API Gateway
Transforms SOAP service to REST API with PII masking and logging
Simulates Azure APIM functionality
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from lxml import etree
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

from data_generator import generator
from pii_masker import masker
from claude_client import claude_client

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configure logging
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gateway.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
SOAP_SERVICE_URL = os.getenv('SOAP_SERVICE_URL', 'http://localhost:5000/soap')


def log_request(customer_id, endpoint, response_time):
    """Log API request (simulates APIM logging)"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "customer_id": customer_id,
        "response_time_ms": response_time,
        "service": "REST Gateway"
    }
    logger.info(f"API Request: {log_entry}")


def call_soap_service(customer_id: int) -> str:
    """Call the backend SOAP service"""
    soap_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:bank="http://legacy-banking.example.com/transactions">
    <soap:Body>
        <bank:GetCustomerTransactionsRequest>
            <bank:CustomerID>{customer_id}</bank:CustomerID>
        </bank:GetCustomerTransactionsRequest>
    </soap:Body>
</soap:Envelope>"""

    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'GetCustomerTransactions'
    }

    try:
        response = requests.post(
            SOAP_SERVICE_URL,
            data=soap_request,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error calling SOAP service: {str(e)}")
        raise


def parse_soap_response(soap_xml: str) -> dict:
    """Parse SOAP XML response and convert to JSON"""
    try:
        root = etree.fromstring(soap_xml.encode('utf-8'))

        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'bank': 'http://legacy-banking.example.com/transactions'
        }

        # Extract customer info
        customer = {
            'customer_id': int(root.xpath('//bank:CustomerID', namespaces=namespaces)[0].text),
            'first_name': root.xpath('//bank:FirstName', namespaces=namespaces)[0].text,
            'last_name': root.xpath('//bank:LastName', namespaces=namespaces)[0].text,
            'full_name': root.xpath('//bank:FullName', namespaces=namespaces)[0].text,
            'email': root.xpath('//bank:Email', namespaces=namespaces)[0].text,
            'phone': root.xpath('//bank:Phone', namespaces=namespaces)[0].text,
            'account_number': root.xpath('//bank:AccountNumber', namespaces=namespaces)[0].text,
            'account_type': root.xpath('//bank:AccountType', namespaces=namespaces)[0].text,
            'member_since': root.xpath('//bank:MemberSince', namespaces=namespaces)[0].text
        }

        # Extract transactions
        transactions = []
        for txn_elem in root.xpath('//bank:Transaction', namespaces=namespaces):
            transaction = {
                'transaction_id': txn_elem.xpath('bank:TransactionID', namespaces=namespaces)[0].text,
                'date': txn_elem.xpath('bank:Date', namespaces=namespaces)[0].text,
                'time': txn_elem.xpath('bank:Time', namespaces=namespaces)[0].text,
                'merchant': txn_elem.xpath('bank:Merchant', namespaces=namespaces)[0].text,
                'category': txn_elem.xpath('bank:Category', namespaces=namespaces)[0].text,
                'amount': float(txn_elem.xpath('bank:Amount', namespaces=namespaces)[0].text),
                'currency': txn_elem.xpath('bank:Currency', namespaces=namespaces)[0].text,
                'status': txn_elem.xpath('bank:Status', namespaces=namespaces)[0].text,
                'payment_method': txn_elem.xpath('bank:PaymentMethod', namespaces=namespaces)[0].text,
                'description': txn_elem.xpath('bank:Description', namespaces=namespaces)[0].text
            }
            transactions.append(transaction)

        # Extract summary
        summary = {
            'total_transactions': int(root.xpath('//bank:TotalTransactions', namespaces=namespaces)[0].text),
            'total_spent': float(root.xpath('//bank:TotalSpent', namespaces=namespaces)[0].text),
            'average_transaction': float(root.xpath('//bank:AverageTransaction', namespaces=namespaces)[0].text),
            'pending_transactions': int(root.xpath('//bank:PendingTransactions', namespaces=namespaces)[0].text)
        }

        return {
            'customer': customer,
            'transactions': transactions,
            'summary': summary
        }

    except Exception as e:
        logger.error(f"Error parsing SOAP response: {str(e)}")
        raise


@app.route('/api/transactions/<int:customer_id>', methods=['GET'])
def get_transactions(customer_id):
    """
    Get customer transactions (masked)
    This is the main REST endpoint that transforms SOAP to JSON
    """
    start_time = datetime.now()

    try:
        logger.info(f"Processing request for customer {customer_id}")

        # Call SOAP service
        soap_response = call_soap_service(customer_id)

        # Parse SOAP XML to JSON
        json_data = parse_soap_response(soap_response)

        # Apply PII masking
        masked_data = masker.mask_customer_data(json_data)

        # Log request
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        log_request(customer_id, '/api/transactions', response_time)

        return jsonify({
            'success': True,
            'data': masked_data,
            'metadata': {
                'response_time_ms': round(response_time, 2),
                'timestamp': datetime.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/transactions/<int:customer_id>/raw', methods=['GET'])
def get_transactions_raw(customer_id):
    """Get raw SOAP XML response (for debugging/comparison)"""
    start_time = datetime.now()

    try:
        logger.info(f"Processing raw request for customer {customer_id}")

        # Call SOAP service
        soap_response = call_soap_service(customer_id)

        # Parse to JSON (unmasked)
        json_data = parse_soap_response(soap_response)

        # Log request
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        log_request(customer_id, '/api/transactions/raw', response_time)

        return jsonify({
            'success': True,
            'soap_xml': soap_response,
            'json_data': json_data,
            'metadata': {
                'response_time_ms': round(response_time, 2),
                'timestamp': datetime.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error processing raw request: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/insights', methods=['POST'])
def get_insights():
    """Get AI-powered insights for transaction data"""
    start_time = datetime.now()

    try:
        # Get customer data from request
        data = request.json
        customer_data = data.get('customer_data')

        if not customer_data:
            return jsonify({
                'success': False,
                'error': 'customer_data is required'
            }), 400

        logger.info(f"Generating insights for customer {customer_data.get('customer', {}).get('customer_id')}")

        # Call Claude API
        insights = claude_client.analyze_transactions(customer_data)

        # Log request
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        log_request(
            customer_data.get('customer', {}).get('customer_id'),
            '/api/insights',
            response_time
        )

        return jsonify({
            'success': True,
            'insights': insights,
            'metadata': {
                'response_time_ms': round(response_time, 2),
                'timestamp': datetime.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'REST Gateway',
        'version': '1.0',
        'soap_backend': SOAP_SERVICE_URL
    })


@app.route('/api', methods=['GET'])
def index():
    """API information"""
    return jsonify({
        'service': 'SOAP-to-REST Transaction Gateway',
        'version': '1.0',
        'description': 'Transforms legacy SOAP API to modern REST with PII masking',
        'endpoints': {
            '/api/transactions/<customer_id>': 'Get customer transactions (masked)',
            '/api/transactions/<customer_id>/raw': 'Get raw SOAP response with JSON conversion',
            '/api/insights': 'Get AI-powered transaction insights (POST)',
            '/api/health': 'Health check'
        }
    })


if __name__ == '__main__':
    logger.info("Starting REST Gateway on port 5001...")
    logger.info(f"SOAP backend: {SOAP_SERVICE_URL}")
    app.run(host='0.0.0.0', port=5001, debug=True)
