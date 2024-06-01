from pathlib import Path
from typing import List, Text
import unittest
from fastapi.testclient import TestClient



PROJECT_PATH: Path = Path(__file__).parents[3]
import sys
sys.path.append(str(PROJECT_PATH))

print("PROJECT_PATH", PROJECT_PATH)

from src.start import app

class TestHealthCheck(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestHealthCheck, self).__init__(*args, **kwargs)
        self.client = TestClient(app)

    def test_liveness(self):
        response = self.client.get("/health/liveness")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "OK")

    def test_readiness(self):
        response = self.client.get("/health/readiness")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "OK")
        

if __name__ == "__main__":
    unittest.main()
