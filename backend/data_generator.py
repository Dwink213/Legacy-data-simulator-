"""
Transaction Data Generator
Generates realistic fake transaction data for demo purposes
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict

class TransactionGenerator:
    """Generates fake transaction data"""

    MERCHANTS = [
        "Amazon.com", "Walmart", "Target", "Starbucks", "McDonald's",
        "Shell Gas Station", "Whole Foods", "Best Buy", "Home Depot",
        "CVS Pharmacy", "Costco", "Apple Store", "Netflix", "Spotify",
        "Uber", "Lyft", "Delta Airlines", "Marriott Hotels", "AMC Theatres"
    ]

    CATEGORIES = [
        "Shopping", "Groceries", "Restaurants", "Gas & Fuel", "Entertainment",
        "Healthcare", "Travel", "Utilities", "Subscriptions", "Transportation"
    ]

    FIRST_NAMES = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
        "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan",
        "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"
    ]

    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
    ]

    def __init__(self):
        self.customer_cache = {}

    def generate_customer_info(self, customer_id: int) -> Dict:
        """Generate or retrieve cached customer information"""
        if customer_id in self.customer_cache:
            return self.customer_cache[customer_id]

        random.seed(customer_id)  # Consistent data for same customer ID

        first_name = random.choice(self.FIRST_NAMES)
        last_name = random.choice(self.LAST_NAMES)

        customer = {
            "customer_id": customer_id,
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@email.com",
            "phone": f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
            "account_number": f"{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}",
            "account_type": random.choice(["Checking", "Savings", "Credit Card"]),
            "member_since": (datetime.now() - timedelta(days=random.randint(365, 3650))).strftime("%Y-%m-%d")
        }

        self.customer_cache[customer_id] = customer
        return customer

    def generate_transactions(self, customer_id: int, num_transactions: int = 10) -> List[Dict]:
        """Generate transaction history for a customer"""
        random.seed(customer_id + 1000)  # Different seed for transactions

        transactions = []
        current_date = datetime.now()

        for i in range(num_transactions):
            days_ago = random.randint(1, 90)
            transaction_date = current_date - timedelta(days=days_ago)

            merchant = random.choice(self.MERCHANTS)
            category = random.choice(self.CATEGORIES)
            amount = round(random.uniform(5.99, 599.99), 2)

            transaction = {
                "transaction_id": f"TXN{customer_id:04d}{i:04d}{random.randint(1000, 9999)}",
                "date": transaction_date.strftime("%Y-%m-%d"),
                "time": transaction_date.strftime("%H:%M:%S"),
                "merchant": merchant,
                "category": category,
                "amount": amount,
                "currency": "USD",
                "status": random.choice(["Completed", "Completed", "Completed", "Pending"]),
                "payment_method": random.choice(["Credit Card", "Debit Card", "ACH Transfer"]),
                "description": f"Purchase at {merchant}"
            }

            transactions.append(transaction)

        # Sort by date descending (newest first)
        transactions.sort(key=lambda x: x["date"], reverse=True)

        return transactions

    def generate_customer_data(self, customer_id: int) -> Dict:
        """Generate complete customer data with transactions"""
        customer = self.generate_customer_info(customer_id)
        transactions = self.generate_transactions(customer_id)

        # Calculate summary statistics
        total_spent = sum(t["amount"] for t in transactions if t["status"] == "Completed")
        avg_transaction = total_spent / len([t for t in transactions if t["status"] == "Completed"]) if transactions else 0

        return {
            "customer": customer,
            "transactions": transactions,
            "summary": {
                "total_transactions": len(transactions),
                "total_spent": round(total_spent, 2),
                "average_transaction": round(avg_transaction, 2),
                "pending_transactions": len([t for t in transactions if t["status"] == "Pending"])
            }
        }


# Singleton instance
generator = TransactionGenerator()

if __name__ == "__main__":
    # Test the generator
    data = generator.generate_customer_data(42)
    print(f"Customer: {data['customer']['full_name']}")
    print(f"Account: {data['customer']['account_number']}")
    print(f"Total Transactions: {data['summary']['total_transactions']}")
    print(f"Total Spent: ${data['summary']['total_spent']}")
    print("\nSample Transaction:")
    print(data['transactions'][0])
