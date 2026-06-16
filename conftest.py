import os

# Set global mock environment variable for GHA/PR testing if real API test is not requested.
if os.environ.get("ABIPY_REAL_API_TEST") is None:
    os.environ["ABIPY_MOCK_API"] = "true"
