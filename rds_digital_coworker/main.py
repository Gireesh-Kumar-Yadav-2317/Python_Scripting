from core.aws_session import assume_rds_client
from core.retry import aws_retry
from core.logger import get_logger
from rules.backup_enabled_rule import evaluate as backup_rule
from rules.snapshot_retention_rule import evaluate as snapshot_rule
from reporting.csv_report import generate_csv
from reporting.s3_upload import upload_report
from config import *

log = get_logger()

def run():
    findings = []

    for acc in ACCOUNTS:
        for region in acc["regions"]:
            try:
                rds = assume_rds_client(acc["role_arn"], region)

                instances = aws_retry(
                    lambda: rds.describe_db_instances()["DBInstances"]
                )

                for db in instances:
                    db_id = db["DBInstanceIdentifier"]

                    backup_hit, backup_msg = backup_rule(db)
                    if backup_hit:
                        findings.append({
                            "account_id": acc["account_id"],
                            "region": region,
                            "db_instance": db_id,
                            "issue": backup_msg
                        })

                    snapshots = aws_retry(
                        lambda: rds.describe_db_snapshots(
                            DBInstanceIdentifier=db_id,
                            SnapshotType="automated"
                        )["DBSnapshots"]
                    )

                    for msg in snapshot_rule(snapshots, RETENTION_DAYS):
                        findings.append({
                            "account_id": acc["account_id"],
                            "region": region,
                            "db_instance": db_id,
                            "issue": msg
                        })

            except Exception as e:
                log(40, {
                    "account_id": acc["account_id"],
                    "region": region,
                    "error": str(e)
                })

    csv_data = generate_csv(findings)
    upload_report(REPORT_BUCKET, REPORT_KEY, csv_data)

    return findings

