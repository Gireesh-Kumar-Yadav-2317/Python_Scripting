import os

import json

SERVICE_NAME = "S3-public-access-coworker"

ACCOUNTS = json.loads(os.environ["ACCOUNTS_JSON"])

# Example env value:
# [
#   {
#     "account_id": "111111111111",
#     "role_arn": "arn:aws:iam::111111111111:role/SecurityAuditRole"
#   }
# ]

REPORT_BUCKET = os.environ["REPORT_BUDCKET"]
REPORT_KEY = os.environ.get("REPORT_KEY", "s3_public_audit.csv")


