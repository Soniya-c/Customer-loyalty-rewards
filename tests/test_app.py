import os, tempfile, unittest
import app as rewards

class RewardsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        rewards.DB_PATH = os.path.join(self.tmp.name, "test.sqlite")
        rewards.ADMIN_PASSWORD = "test-admin"
        rewards.app.config.update(TESTING=True, SECRET_KEY="test-secret")
        rewards.init_db()
        self.client = rewards.app.test_client()
        self.code = "ABCD-EFGH-JKLM"
        with rewards.db() as con:
            con.execute("INSERT INTO codes(code_hash,points) VALUES (?,?)",
                        (rewards.hash_code(self.code), 10))

    def tearDown(self):
        self.tmp.cleanup()

    def test_valid_redemption_awards_points(self):
        response = self.client.post("/redeem", data={"email":"buyer@example.com","code":self.code})
        self.assertEqual(response.status_code, 302)
        with rewards.db() as con:
            customer = con.execute("SELECT points,boxes FROM customers WHERE email=?",
                                   ("buyer@example.com",)).fetchone()
            self.assertEqual((customer["points"], customer["boxes"]), (10, 1))

    def test_code_cannot_be_redeemed_twice(self):
        self.client.post("/redeem", data={"email":"buyer@example.com","code":self.code})
        self.client.post("/redeem", data={"email":"other@example.com","code":self.code})
        with rewards.db() as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM redemptions").fetchone()[0], 1)
            self.assertIsNone(con.execute("SELECT email FROM customers WHERE email=?",
                                          ("other@example.com",)).fetchone())

    def test_unknown_code_does_not_create_customer(self):
        self.client.post("/redeem", data={"email":"buyer@example.com","code":"ZZZZ-ZZZZ-ZZZZ"})
        with rewards.db() as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM customers").fetchone()[0], 0)

    def test_admin_dashboard_requires_login(self):
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 302)
        self.client.post("/admin/login", data={"password":"test-admin"})
        self.assertEqual(self.client.get("/admin").status_code, 200)

if __name__ == "__main__":
    unittest.main()
