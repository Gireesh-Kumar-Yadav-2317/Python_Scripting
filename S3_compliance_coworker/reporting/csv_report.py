import csv
import io
from datetime import datetime

def generate_csv(findings):
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow([
        "AccountId",
        "Bucket",
        "Issue",
        "CheckedAt"
    ])

    for f in findings:
        writer.writerow([
            f["account_id"],
            f["bucket"],
            f["issue"],
            datetime.utcnow().isoformat()
        ])

    return buffer.getvalue()

