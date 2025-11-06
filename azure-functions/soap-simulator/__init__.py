"""
SOAP Simulator Azure Function
Simulates legacy SOAP service for transaction data
"""
import azure.functions as func
import logging
import json
from datetime import datetime
from lxml import etree
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
from data_generator import generator

# Configure Application Insights
logger = logging.getLogger("azure")
logger.setLevel(logging.INFO)


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
        timestamp=datetime.utcnow().isoformat() + "Z",
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


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function entry point"""

    start_time = datetime.utcnow()

    try:
        # Parse incoming SOAP request
        soap_request = req.get_body().decode('utf-8')

        logger.info('SOAP request received', extra={
            'custom_dimensions': {
                'function': 'soap-simulator',
                'request_size_bytes': len(soap_request),
                'timestamp': start_time.isoformat()
            }
        })

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

        # Generate SOAP response
        soap_response = create_soap_envelope(customer_id)

        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Log success with custom metrics
        logger.info('SOAP response generated successfully', extra={
            'custom_dimensions': {
                'function': 'soap-simulator',
                'customer_id': customer_id,
                'response_size_bytes': len(soap_response),
                'duration_ms': duration,
                'status': 'success'
            }
        })

        return func.HttpResponse(
            soap_response,
            mimetype='text/xml',
            status_code=200
        )

    except Exception as e:
        logger.error(f'Error in SOAP simulator: {str(e)}', extra={
            'custom_dimensions': {
                'function': 'soap-simulator',
                'error_type': type(e).__name__,
                'error_message': str(e),
                'status': 'error'
            }
        })

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

        return func.HttpResponse(
            fault,
            status_code=500,
            mimetype='text/xml'
        )
