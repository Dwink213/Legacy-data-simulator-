"""
REST Gateway Azure Function
Transforms SOAP service to REST API with PII masking
"""
import azure.functions as func
import logging
import json
from datetime import datetime
from lxml import etree
import requests
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
from pii_masker import masker

# Configure Application Insights
logger = logging.getLogger("azure")
logger.setLevel(logging.INFO)

# Get SOAP service URL (local dev or Azure Function)
SOAP_SERVICE_URL = os.getenv('SOAP_SERVICE_URL', 'http://localhost:7071/api/soap')


def call_soap_service(customer_id: int) -> str:
    """Call the SOAP simulator function"""
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
            timeout=30
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


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function entry point"""

    start_time = datetime.utcnow()

    try:
        # Get customer ID from route
        customer_id = int(req.route_params.get('customer_id'))
        mode = req.route_params.get('mode', '')

        logger.info('REST Gateway request received', extra={
            'custom_dimensions': {
                'function': 'rest-gateway',
                'customer_id': customer_id,
                'mode': mode if mode else 'masked',
                'timestamp': start_time.isoformat()
            }
        })

        # Call SOAP service
        soap_start = datetime.utcnow()
        soap_response = call_soap_service(customer_id)
        soap_duration = (datetime.utcnow() - soap_start).total_seconds() * 1000

        # Parse SOAP XML to JSON
        parse_start = datetime.utcnow()
        json_data = parse_soap_response(soap_response)
        parse_duration = (datetime.utcnow() - parse_start).total_seconds() * 1000

        # Log SOAP transformation metrics
        logger.info('SOAP to JSON transformation completed', extra={
            'custom_dimensions': {
                'function': 'rest-gateway',
                'customer_id': customer_id,
                'soap_call_duration_ms': soap_duration,
                'parse_duration_ms': parse_duration,
                'xml_size_bytes': len(soap_response),
                'transaction_count': len(json_data.get('transactions', []))
            }
        })

        # Return raw data if requested
        if mode == 'raw':
            total_duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            logger.info('Raw data returned', extra={
                'custom_dimensions': {
                    'function': 'rest-gateway',
                    'customer_id': customer_id,
                    'total_duration_ms': total_duration,
                    'mode': 'raw'
                }
            })

            return func.HttpResponse(
                json.dumps({
                    'success': True,
                    'soap_xml': soap_response,
                    'json_data': json_data,
                    'metadata': {
                        'response_time_ms': round(total_duration, 2),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }),
                mimetype='application/json',
                status_code=200
            )

        # Apply PII masking
        mask_start = datetime.utcnow()
        masked_data = masker.mask_customer_data(json_data)
        mask_duration = (datetime.utcnow() - mask_start).total_seconds() * 1000

        total_duration = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Log PII masking metrics
        logger.info('PII masking completed', extra={
            'custom_dimensions': {
                'function': 'rest-gateway',
                'customer_id': customer_id,
                'mask_duration_ms': mask_duration,
                'total_duration_ms': total_duration,
                'pii_fields_masked': 4,  # name, account, email, phone
                'mode': 'masked'
            }
        })

        return func.HttpResponse(
            json.dumps({
                'success': True,
                'data': masked_data,
                'metadata': {
                    'response_time_ms': round(total_duration, 2),
                    'timestamp': datetime.utcnow().isoformat(),
                    'soap_duration_ms': round(soap_duration, 2),
                    'parse_duration_ms': round(parse_duration, 2),
                    'mask_duration_ms': round(mask_duration, 2)
                }
            }),
            mimetype='application/json',
            status_code=200
        )

    except Exception as e:
        total_duration = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.error(f'Error in REST gateway: {str(e)}', extra={
            'custom_dimensions': {
                'function': 'rest-gateway',
                'error_type': type(e).__name__,
                'error_message': str(e),
                'duration_ms': total_duration,
                'status': 'error'
            }
        })

        return func.HttpResponse(
            json.dumps({
                'success': False,
                'error': str(e)
            }),
            status_code=500,
            mimetype='application/json'
        )
