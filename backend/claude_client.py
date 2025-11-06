"""
Claude API Client
Integrates with Anthropic's Claude API for transaction insights
"""
import os
import json
from typing import Dict, List
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ClaudeInsightsClient:
    """Client for getting AI-powered transaction insights"""

    def __init__(self):
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            logger.warning("CLAUDE_API_KEY not set. AI insights will not be available.")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)

    def analyze_transactions(self, customer_data: Dict) -> Dict:
        """
        Analyze customer transactions and provide insights

        Args:
            customer_data: Dictionary containing customer info and transactions

        Returns:
            Dictionary with insights and recommendations
        """
        if not self.client:
            return {
                "error": "Claude API not configured",
                "message": "Please set CLAUDE_API_KEY in .env file",
                "insights": None
            }

        try:
            # Prepare transaction summary for Claude
            transactions = customer_data.get("transactions", [])
            summary = customer_data.get("summary", {})

            # Create a concise summary for the AI
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

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract the response
            insights_text = message.content[0].text

            # Parse the response into structured format
            structured_insights = self._parse_insights(insights_text, transactions, summary)

            return {
                "success": True,
                "insights": structured_insights,
                "raw_analysis": insights_text
            }

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            return {
                "error": "Failed to generate insights",
                "message": str(e),
                "insights": None
            }

    def _create_transaction_summary(self, transactions: List[Dict], summary: Dict) -> str:
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

    def _parse_insights(self, insights_text: str, transactions: List[Dict], summary: Dict) -> Dict:
        """Parse Claude's text response into structured insights"""

        # Calculate some basic metrics
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

    def _extract_recommendations(self, insights_text: str) -> List[str]:
        """Extract key recommendations from Claude's response"""
        # Simple extraction - look for bullet points or numbered items
        lines = insights_text.split('\n')
        recommendations = []

        for line in lines:
            line = line.strip()
            # Look for lines that start with bullets, numbers, or recommendation keywords
            if line and any([
                line.startswith('-'),
                line.startswith('•'),
                line[0:2].replace('.', '').isdigit(),
                'recommend' in line.lower(),
                'consider' in line.lower(),
                'suggest' in line.lower()
            ]):
                # Clean up the line
                clean_line = line.lstrip('-•0123456789. ').strip()
                if clean_line and len(clean_line) > 10:  # Ignore very short lines
                    recommendations.append(clean_line)

        return recommendations[:5]  # Return top 5 recommendations


# Singleton instance
claude_client = ClaudeInsightsClient()


if __name__ == "__main__":
    # Test the client
    from data_generator import generator

    test_data = generator.generate_customer_data(42)

    print("Analyzing transactions...")
    result = claude_client.analyze_transactions(test_data)

    if result.get("success"):
        print("\n=== AI Insights ===")
        print(result["insights"]["ai_analysis"])
        print("\n=== Recommendations ===")
        for rec in result["insights"]["recommendations"]:
            print(f"• {rec}")
    else:
        print(f"Error: {result.get('message')}")
