import os
import json

SERVICE_NAME = "rds-backup-compliance-coworker"

ACCOUNTS = json.loads(os.environ["ACCOUNTS_JSON"])
# Example:
# [
#   {
#     "account_id": "111111111111",
#     "role_arn": "arn:aws:iam::111111111111:role/SecurityAuditRole",
#     "regions": ["us-east-1"]
#   }
# ]

RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "30"))

REPORT_BUCKET = os.environ["REPORT_BUCKET"]
REPORT_KEY = os.environ.get("REPORT_KEY", "rds_compliance.csv")

