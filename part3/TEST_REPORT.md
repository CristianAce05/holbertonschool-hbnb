# HBnB Part2 — Testing Report

Date: 2026-02-13

Summary
- Unit tests: 4 tests ran — OK (see `/tmp/unit_test_results.txt`)
- Black-box cURL tests: executed a series of success and failure cases against the running dev server on port 5001. Outputs captured in this report.

How tests were run
- Server: `python3 run_foreground.py --port 5001` (binds to `0.0.0.0:5001`)
- Unit tests: `python3 -m unittest discover -v tests` (output saved to `/tmp/unit_test_results.txt`)
- cURL tests: `/tmp/curl_tests.sh` (outputs saved to `/tmp/curl_tests_captured.txt` and `/tmp/curl_tests.log`)

Unit test results (excerpt)
```
$(cat /tmp/unit_test_results.txt 2>/dev/null || echo 'unit test output not found')
```

cURL test cases and results (key cases)

1) Health endpoint
```
$(sed -n '1,5p' /tmp/curl_tests_captured.txt 2>/dev/null || true)
```

2) Create user (valid)
```
$(sed -n '/== POST user (valid) ==/,/--status:/{/== POST user (valid) ==/d;p}' /tmp/curl_tests_captured.txt 2>/dev/null || true)
```

3) Create user (missing password) — expected failure (400)
```
$(sed -n '/== POST user (missing password) ==/,/--status:/{/== POST user (missing password) ==/d;p}' /tmp/curl_tests_captured.txt 2>/dev/null || true)
```

4) Create amenity (valid)
```
$(sed -n '/== POST amenity ==/,/--status:/{/== POST amenity ==/d;p}' /tmp/curl_tests_captured.txt 2>/dev/null || true)
```

5) Create place (missing `user_id`) — note: current implementation accepted and returned 201 with `owner: null`.
```
$(sed -n '/== POST place (missing user_id) ==/,/--status:/{/== POST place (missing user_id) ==/d;p}' /tmp/curl_tests_captured.txt 2>/dev/null || true)
```

6) Create place (valid) with user and amenities
```
$(sed -n '/== POST place (valid) ==/,/--status:/{/== POST place (valid) ==/d;p}' /tmp/curl_tests_captured.txt 2>/dev/null || true)
```

7) Create review (missing fields) — expected failure (400)
```
$(sed -n '/== POST review (missing fields) ==/,/--status:/{/== POST review (missing fields) ==/d;p}' /tmp/curl_tests_captured.txt 2>/dev/null || true)
```

8) Create review (valid)
```
$(sed -n '/== POST review (valid) ==/,/--status:/{/== POST review (valid) ==/d;p}' /tmp/curl_tests_captured.txt 2>/dev/null || true)
```

9) GET place includes reviews (verified)
```
$(sed -n '/== GET place (should include reviews) ==/,/--status:/{/== GET place (should include reviews) ==/d;p}' /tmp/curl_tests_captured.txt 2>/dev/null || true)
```

Full raw cURL output
```
$(cat /tmp/curl_tests_captured.txt 2>/dev/null || echo 'curl output not found')
```

Observations and validation notes
- The API already enforces several validation checks and returns HTTP 400 with a JSON error for missing required fields (e.g., missing `password` when creating a user, missing `user_id` when creating a review).
- The `POST /api/v1/places` endpoint currently accepts creation without `user_id` and returns 201 with `owner: null` — this may be acceptable or may need stricter validation depending on requirements (I recommend enforcing `user_id` presence and existence to mirror production constraints).
- Timestamps are naive UTC strings; there are DeprecationWarnings about `datetime.utcnow()` (non-timezone-aware). Consider switching to timezone-aware datetimes in future parts.

Next steps / recommendations
- Enforce `user_id` requirement and existence for `Place` creation if business rules require an owner.
- Add more unit tests to cover validation edge cases (bad types, missing arrays, invalid IDs).
- Integrate the test runs into CI (GitHub Actions) to ensure tests run on PRs.
