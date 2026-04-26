import app
import json

app.is_busy = False

with app.app.test_request_context(
    '/process', 
    method='POST',
    json={
        "username": "user",
        "password": "bitnami",
        "grade": "0",
        "testname": ["後期中間までの課題1（U.3の復習）"]
    }
):
    print("Simulating Flask request...")
    res = app.process()
    print("Response:", res.get_json())

import time
time.sleep(3)
print("Result dictionary:", app.results)
