import unittest
import json

from hbnb import create_app


class AuthIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        # Enable auth and provide a test secret via config
        # use a >=32-byte secret for HMAC safety
        long_secret = "A" * 40
        self.app = create_app(
            {
                "TESTING": True,
                "ENABLE_AUTH": True,
                "JWT_SECRET_KEY": long_secret,
            }
        )
        self.client = self.app.test_client()

    def post_json(self, path, payload, headers=None):
        return self.client.post(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            headers=headers,
        )

    def test_login_and_create_place_as_owner(self):
        # create user
        r = self.post_json(
            "/api/v1/users", {"email": "u1@example.com", "password": "pw"}
        )
        self.assertEqual(r.status_code, 201)
        u = r.get_json()
        uid = u["id"]
        # login
        r = self.post_json(
            "/api/v1/auth/login", {"email": "u1@example.com", "password": "pw"}
        )
        self.assertEqual(r.status_code, 200)
        token = r.get_json().get("access_token")
        self.assertTrue(token)
        headers = {"Authorization": f"Bearer {token}"}
        # create place as owner -> allowed
        payload = {"name": "Owned", "user_id": uid}
        r = self.post_json("/api/v1/places", payload, headers=headers)
        self.assertEqual(r.status_code, 201)

    def test_forbidden_create_place_for_other_user(self):
        # create two users
        self.post_json("/api/v1/users", {"email": "a@example.com", "password": "pw"})
        r2 = self.post_json(
            "/api/v1/users", {"email": "b@example.com", "password": "pw"}
        )
        b_id = r2.get_json()["id"]
        # login as user A
        r = self.post_json(
            "/api/v1/auth/login", {"email": "a@example.com", "password": "pw"}
        )
        token = r.get_json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        # attempt to create place claiming to be user B -> forbidden
        payload = {"name": "BadClaim", "user_id": b_id}
        r = self.post_json("/api/v1/places", payload, headers=headers)
        self.assertEqual(r.status_code, 403)


if __name__ == "__main__":
    unittest.main()
