"""
PII Masking Module
Masks personally identifiable information in transaction data
"""
import re
from typing import Dict, List, Any


class PIIMasker:
    """Handles PII masking for sensitive customer data"""

    @staticmethod
    def mask_name(name: str) -> str:
        """
        Mask customer name showing only initials
        Example: "John Smith" -> "J*** S***"
        """
        if not name:
            return ""

        parts = name.split()
        masked_parts = []

        for part in parts:
            if len(part) > 0:
                masked = part[0] + "*" * min(3, len(part) - 1)
                masked_parts.append(masked)

        return " ".join(masked_parts)

    @staticmethod
    def mask_account_number(account_number: str) -> str:
        """
        Mask account number showing only last 4 digits
        Example: "123456789012" -> "****9012"
        """
        if not account_number:
            return ""

        account_str = str(account_number)
        if len(account_str) <= 4:
            return "*" * len(account_str)

        return "*" * (len(account_str) - 4) + account_str[-4:]

    @staticmethod
    def mask_email(email: str) -> str:
        """
        Mask email address partially
        Example: "john.smith@email.com" -> "j***@email.com"
        """
        if not email or "@" not in email:
            return email

        local, domain = email.split("@", 1)

        if len(local) > 0:
            masked_local = local[0] + "***"
        else:
            masked_local = "***"

        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """
        Mask phone number showing only last 4 digits
        Example: "+1-555-123-4567" -> "***-***-4567"
        """
        if not phone:
            return ""

        # Extract digits
        digits = re.sub(r'\D', '', phone)

        if len(digits) <= 4:
            return "*" * len(digits)

        # Show last 4 digits
        return "***-***-" + digits[-4:]

    def mask_customer(self, customer: Dict) -> Dict:
        """Mask all PII fields in customer object"""
        masked = customer.copy()

        if "first_name" in masked:
            masked["first_name"] = self.mask_name(masked["first_name"])

        if "last_name" in masked:
            masked["last_name"] = self.mask_name(masked["last_name"])

        if "full_name" in masked:
            masked["full_name"] = self.mask_name(masked["full_name"])

        if "email" in masked:
            masked["email"] = self.mask_email(masked["email"])

        if "phone" in masked:
            masked["phone"] = self.mask_phone(masked["phone"])

        if "account_number" in masked:
            masked["account_number"] = self.mask_account_number(masked["account_number"])

        return masked

    def mask_transaction(self, transaction: Dict) -> Dict:
        """Mask PII in transaction (currently minimal PII in transactions)"""
        # Transactions generally don't contain PII, but we keep this for extensibility
        return transaction.copy()

    def mask_customer_data(self, data: Dict) -> Dict:
        """Mask all PII in complete customer data structure"""
        masked_data = {
            "customer": self.mask_customer(data.get("customer", {})),
            "transactions": [
                self.mask_transaction(t) for t in data.get("transactions", [])
            ],
            "summary": data.get("summary", {}).copy()
        }

        return masked_data


# Singleton instance
masker = PIIMasker()


if __name__ == "__main__":
    # Test the masker
    test_customer = {
        "customer_id": 1,
        "first_name": "John",
        "last_name": "Smith",
        "full_name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-123-4567",
        "account_number": "123456789012"
    }

    masked = masker.mask_customer(test_customer)

    print("Original:")
    for key, value in test_customer.items():
        print(f"  {key}: {value}")

    print("\nMasked:")
    for key, value in masked.items():
        print(f"  {key}: {value}")
