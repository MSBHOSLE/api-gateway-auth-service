import unittest
from datetime import timedelta
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password


class TestSecurity(unittest.TestCase):
    def test_password_hashing_and_verification(self):
        pw = "SuperSecurePassword123!"
        hashed = hash_password(pw)
        self.assertNotEqual(pw, hashed)
        self.assertTrue(verify_password(pw, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_jwt_access_and_refresh_token(self):
        token = create_access_token("testuser", role="admin")
        payload = decode_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], "testuser")
        self.assertEqual(payload["role"], "admin")
        self.assertEqual(payload["type"], "access")

        refresh = create_refresh_token("testuser")
        r_payload = decode_token(refresh)
        self.assertIsNotNone(r_payload)
        self.assertEqual(r_payload["sub"], "testuser")
        self.assertEqual(r_payload["type"], "refresh")

    def test_expired_token(self):
        token = create_access_token("testuser", expires_delta=timedelta(seconds=-10))
        payload = decode_token(token)
        self.assertIsNone(payload)


if __name__ == "__main__":
    unittest.main()
