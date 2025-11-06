"""
Mock SOAP Service
Simulates a legacy banking SOAP API for transaction data
"""
from flask import Flask, request, Response
from lxml import etree
import logging
from data_generator import generator

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_soap_envelope(customer_id: int) -> str:
    """Create SOAP XML response with customer transaction data"""

    data = generator.generate_customer_data(customer_id)
    customer = data["customer"]
    transactions = data["transactions"]
    summary = data["summary"]

    # Build SOAP envelope
    soap_env = """<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:bank="http://legacy-banking.example.com/transactions">
    <soap:Header>
        <bank:RequestID>REQ-{customer_id}-{timestamp}</bank:RequestID>
        <bank:ServiceVersion>1.0</bank:ServiceVersion>
    </soap:Header>
    <soap:Body>
        <bank:GetCustomerTransactionsResponse>
            <bank:Customer>
                <bank:CustomerID>{customer_id}</bank:CustomerID>
                <bank:FirstName>{first_name}</bank:FirstName>
                <bank:LastName>{last_name}</bank:LastName>
                <bank:FullName>{full_name}</bank:FullName>
                <bank:Email>{email}</bank:Email>
                <bank:Phone>{phone}</bank:Phone>
                <bank:AccountNumber>{account_number}</bank:AccountNumber>
                <bank:AccountType>{account_type}</bank:AccountType>
                <bank:MemberSince>{member_since}</bank:MemberSince>
            </bank:Customer>
            <bank:Transactions>
""".format(
        customer_id=customer["customer_id"],
        timestamp="2024-01-01T00:00:00Z",
        first_name=customer["first_name"],
        last_name=customer["last_name"],
        full_name=customer["full_name"],
        email=customer["email"],
        phone=customer["phone"],
        account_number=customer["account_number"],
        account_type=customer["account_type"],
        member_since=customer["member_since"]
    )

    # Add transactions
    for txn in transactions:
        soap_env += """                <bank:Transaction>
                    <bank:TransactionID>{transaction_id}</bank:TransactionID>
                    <bank:Date>{date}</bank:Date>
                    <bank:Time>{time}</bank:Time>
                    <bank:Merchant>{merchant}</bank:Merchant>
                    <bank:Category>{category}</bank:Category>
                    <bank:Amount>{amount}</bank:Amount>
                    <bank:Currency>{currency}</bank:Currency>
                    <bank:Status>{status}</bank:Status>
                    <bank:PaymentMethod>{payment_method}</bank:PaymentMethod>
                    <bank:Description>{description}</bank:Description>
                </bank:Transaction>
""".format(**txn)

    soap_env += """            </bank:Transactions>
            <bank:Summary>
                <bank:TotalTransactions>{total_transactions}</bank:TotalTransactions>
                <bank:TotalSpent>{total_spent}</bank:TotalSpent>
                <bank:AverageTransaction>{average_transaction}</bank:AverageTransaction>
                <bank:PendingTransactions>{pending_transactions}</bank:PendingTransactions>
            </bank:Summary>
        </bank:GetCustomerTransactionsResponse>
    </soap:Body>
</soap:Envelope>""".format(**summary)

    return soap_env


@app.route('/soap', methods=['POST'])
def soap_endpoint():
    """Handle SOAP requests"""
    try:
        # Parse incoming SOAP request
        soap_request = request.data.decode('utf-8')
        logger.info(f"Received SOAP request: {len(soap_request)} bytes")

        # Extract customer ID from SOAP request
        root = etree.fromstring(soap_request.encode('utf-8'))

        # Find CustomerID in request (namespace-aware)
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'bank': 'http://legacy-banking.example.com/transactions'
        }

        customer_id_element = root.xpath('//bank:CustomerID', namespaces=namespaces)

        if customer_id_element:
            customer_id = int(customer_id_element[0].text)
        else:
            # Fallback: try without namespace
            customer_id_element = root.xpath('//CustomerID')
            if customer_id_element:
                customer_id = int(customer_id_element[0].text)
            else:
                raise ValueError("CustomerID not found in SOAP request")

        logger.info(f"Processing request for customer ID: {customer_id}")

        # Generate SOAP response
        soap_response = create_soap_envelope(customer_id)

        return Response(soap_response, mimetype='text/xml')

    except Exception as e:
        logger.error(f"Error processing SOAP request: {str(e)}")

        # Return SOAP fault
        fault = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <soap:Fault>
            <faultcode>soap:Server</faultcode>
            <faultstring>{str(e)}</faultstring>
        </soap:Fault>
    </soap:Body>
</soap:Envelope>"""

        return Response(fault, status=500, mimetype='text/xml')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SOAP Transaction Service"}


@app.route('/', methods=['GET'])
def index():
    """Service information"""
    return {
        "service": "Legacy Banking SOAP Service",
        "version": "1.0",
        "endpoint": "/soap",
        "method": "POST",
        "description": "Mock SOAP service for transaction data"
    }


if __name__ == '__main__':
    logger.info("Starting SOAP Service on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
