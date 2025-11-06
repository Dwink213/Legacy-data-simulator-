"""
AI Insights Azure Function
Integrates with Claude API for transaction analysis
Demonstrates AI architecture patterns and cost tracking
"""
import azure.functions as func
import logging
import json
from datetime import datetime
import os
import sys
from anthropic import Anthropic

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Configure Application Insights
logger = logging.getLogger("azure")
logger.setLevel(logging.INFO)


class ClaudeInsightsClient:
    """Client for getting AI-powered transaction insights with Azure telemetry"""

    def __init__(self):
        # Use Managed Identity in production, API key in dev
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            logger.warning("CLAUDE_API_KEY not set. AI insights will not be available.")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)

    def analyze_transactions(self, customer_data: dict) -> dict:
        """
        Analyze customer transactions and provide insights
        Tracks AI costs and token usage for observability
        """
        if not self.client:
            return {
                "error": "Claude API not configured",
                "message": "Please set CLAUDE_API_KEY in Azure Key Vault",
                "insights": None
            }

        start_time = datetime.utcnow()

        try:
            transactions = customer_data.get("transactions", [])
            summary = customer_data.get("summary", {})

            # Create transaction summary for Claude
            transaction_summary = self._create_transaction_summary(transactions, summary)

            # Build prompt for Claude
            prompt = f"""Analyze these customer transactions and provide insights:

{transaction_summary}

Please provide:
1. Spending pattern analysis
2. Top spending categories
3. Unusual or noteworthy transactions
4. Budget recommendations
5. Saving opportunities

Format your response as clear, actionable insights."""

            # Log prompt size for cost tracking
            prompt_tokens = len(prompt.split())  # Approximate

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract token usage from response
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            total_tokens = input_tokens + output_tokens

            # Calculate cost (Claude Sonnet pricing: $3/M input, $15/M output)
            input_cost = (input_tokens / 1_000_000) * 3.00
            output_cost = (output_tokens / 1_000_000) * 15.00
            total_cost = input_cost + output_cost

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Log AI metrics to Application Insights
            logger.info('Claude API call successful', extra={
                'custom_dimensions': {
                    'function': 'ai-insights',
                    'ai_provider': 'Claude',
                    'ai_model': 'claude-3-5-sonnet-20241022',
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'total_tokens': total_tokens,
                    'input_cost_usd': round(input_cost, 6),
                    'output_cost_usd': round(output_cost, 6),
                    'total_cost_usd': round(total_cost, 6),
                    'duration_ms': duration,
                    'transaction_count': len(transactions),
                    'customer_id': customer_data.get('customer', {}).get('customer_id'),
                    'status': 'success'
                }
            })

            # Extract the response
            insights_text = message.content[0].text

            # Parse the response into structured format
            structured_insights = self._parse_insights(insights_text, transactions, summary)

            # Add cost tracking to response
            structured_insights['cost_tracking'] = {
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': total_tokens,
                'cost_usd': round(total_cost, 6),
                'model': 'claude-3-5-sonnet-20241022'
            }

            return {
                "success": True,
                "insights": structured_insights,
                "raw_analysis": insights_text,
                "metadata": {
                    "duration_ms": round(duration, 2),
                    "tokens_used": total_tokens,
                    "cost_usd": round(total_cost, 6)
                }
            }

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            logger.error(f"Error calling Claude API: {str(e)}", extra={
                'custom_dimensions': {
                    'function': 'ai-insights',
                    'ai_provider': 'Claude',
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'duration_ms': duration,
                    'status': 'error'
                }
            })

            return {
                "error": "Failed to generate insights",
                "message": str(e),
                "insights": None
            }

    def _create_transaction_summary(self, transactions: list, summary: dict) -> str:
        """Create a concise summary of transactions for Claude"""

        # Group transactions by category
        category_totals = {}
        for txn in transactions:
            if txn["status"] == "Completed":
                category = txn["category"]
                amount = txn["amount"]
                category_totals[category] = category_totals.get(category, 0) + amount

        # Build summary text
        summary_text = f"""
Transaction Summary:
- Total Transactions: {summary.get('total_transactions', 0)}
- Total Spent: ${summary.get('total_spent', 0):.2f}
- Average Transaction: ${summary.get('average_transaction', 0):.2f}
- Pending: {summary.get('pending_transactions', 0)}

Spending by Category:
"""
        for category, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            summary_text += f"- {category}: ${total:.2f}\n"

        summary_text += "\nRecent Transactions:\n"
        for txn in transactions[:5]:  # Show top 5 recent
            summary_text += f"- {txn['date']}: {txn['merchant']} - ${txn['amount']:.2f} ({txn['category']})\n"

        return summary_text

    def _parse_insights(self, insights_text: str, transactions: list, summary: dict) -> dict:
        """Parse Claude's text response into structured insights"""

        # Calculate metrics
        category_totals = {}
        for txn in transactions:
            if txn["status"] == "Completed":
                category = txn["category"]
                amount = txn["amount"]
                category_totals[category] = category_totals.get(category, 0) + amount

        top_categories = sorted(
            category_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        # Find largest transactions
        largest_txns = sorted(
            [t for t in transactions if t["status"] == "Completed"],
            key=lambda x: x["amount"],
            reverse=True
        )[:3]

        return {
            "summary": {
                "total_spent": summary.get("total_spent", 0),
                "transaction_count": summary.get("total_transactions", 0),
                "average_transaction": summary.get("average_transaction", 0)
            },
            "top_categories": [
                {"category": cat, "amount": amt, "percentage": (amt / summary.get("total_spent", 1) * 100)}
                for cat, amt in top_categories
            ],
            "largest_transactions": [
                {
                    "merchant": t["merchant"],
                    "amount": t["amount"],
                    "date": t["date"],
                    "category": t["category"]
                }
                for t in largest_txns
            ],
            "ai_analysis": insights_text,
            "recommendations": self._extract_recommendations(insights_text)
        }

    def _extract_recommendations(self, insights_text: str) -> list:
        """Extract key recommendations from Claude's response"""
        lines = insights_text.split('\n')
        recommendations = []

        for line in lines:
            line = line.strip()
            if line and any([
                line.startswith('-'),
                line.startswith('•'),
                line[0:2].replace('.', '').isdigit(),
                'recommend' in line.lower(),
                'consider' in line.lower(),
                'suggest' in line.lower()
            ]):
                clean_line = line.lstrip('-•0123456789. ').strip()
                if clean_line and len(clean_line) > 10:
                    recommendations.append(clean_line)

        return recommendations[:5]


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function entry point"""

    start_time = datetime.utcnow()

    try:
        # Get customer data from request
        req_body = req.get_json()
        customer_data = req_body.get('customer_data')

        if not customer_data:
            return func.HttpResponse(
                json.dumps({
                    'success': False,
                    'error': 'customer_data is required'
                }),
                status_code=400,
                mimetype='application/json'
            )

        customer_id = customer_data.get('customer', {}).get('customer_id')

        logger.info('AI insights request received', extra={
            'custom_dimensions': {
                'function': 'ai-insights',
                'customer_id': customer_id,
                'transaction_count': len(customer_data.get('transactions', [])),
                'timestamp': start_time.isoformat()
            }
        })

        # Initialize Claude client and get insights
        claude_client = ClaudeInsightsClient()
        insights = claude_client.analyze_transactions(customer_data)

        total_duration = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.info('AI insights generation completed', extra={
            'custom_dimensions': {
                'function': 'ai-insights',
                'customer_id': customer_id,
                'total_duration_ms': total_duration,
                'success': insights.get('success', False)
            }
        })

        return func.HttpResponse(
            json.dumps({
                'success': True,
                'insights': insights,
                'metadata': {
                    'response_time_ms': round(total_duration, 2),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }),
            mimetype='application/json',
            status_code=200
        )

    except Exception as e:
        total_duration = (datetime.utcnow() - start_time).total_seconds() * 1000

        logger.error(f'Error in AI insights function: {str(e)}', extra={
            'custom_dimensions': {
                'function': 'ai-insights',
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
