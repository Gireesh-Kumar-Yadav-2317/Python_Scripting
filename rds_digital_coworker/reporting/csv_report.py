import csv
import io
from datetime import datetime

def generate_csv(findings):
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow([
        "AccountId",
        "Region",
        "DBInstance",
        "Issue",
        "CheckedAt"
    ])

    for f in findings:
        writer.writerow([
            f["account_id"],
            f["region"],
            f["db_instance"],
            f["issue"],
            datetime.utcnow().isoformat()
        ])

    return buffer.getvalue()

