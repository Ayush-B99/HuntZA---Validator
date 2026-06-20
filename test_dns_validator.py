import unittest
# Assuming your main script is named 'email_validator.py'
from main import has_valid_dns 

class TestDNSValidation(unittest.TestCase):

    def test_valid_routing_domains(self):
        """Should return True for major live domains with valid MX records."""
        self.assertTrue(has_valid_dns("gmail.com"))
        self.assertTrue(has_valid_dns("microsoft.com"))
        self.assertTrue(has_valid_dns("apple.com"))

    def test_non_existent_domains(self):
        """Should return False for domains that do not exist anywhere."""
        self.assertFalse(has_valid_dns("this-is-a-completely-fake-domain-123456.xyz"))
        self.assertFalse(has_valid_dns("invalid-domain-name-testing-123.co"))

    def test_empty_or_malformed_domains(self):
        """Should return False for structural domain inputs that fail lookup."""
        self.assertFalse(has_valid_dns(""))
        self.assertFalse(has_valid_dns("..."))

if __name__ == "__main__":
    unittest.main()