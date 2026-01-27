from core.aws_session import assume_s3_client
from core.retry import aws_retry
from core.logger import get_logger
from checks.acl_check import check_acl
from checks.policy_check import check_policy
from checks.pab_check import check_public_access_block
from reporting.csv_report import generate_csv
from reporting.s3_upload import upload_report
from config import *

log = get_logger()

def run():
    findings =[] 

    for acc in ACCOUNTS:
        s3 =assume_s3_client(acc["role_arn"])

        buckets = aws_retry(lamdbda: s3.list_buckets()["Buckets"])

        for bucket in buckets:
            name = bucket["Name"]

            try:
                acl = aws_retry(lambda:s3.get_bucket_acl(Bucket = name))
                acl_hit, acl_msg = check_acl(acl)
                try:
                    pab = aws_retry(lambda:s3.get_public_access_block(Bucket = name)["PublicAccessBlockConfiguration"])
                except s3.exceptions.NoSuchPublicAccessBlockConfiguration:
                    pab : {}

                    pab_hit , pab_msg = check_public_access_block(pab)

                try:
                    policy = aws_retry(
                        lambda: s3.get_bucket_policy(Bucket=name)["Policy"]
                    )
                    pol_hit, pol_msg = check_policy(policy)
                except s3.exceptions.NoSuchBucketPolicy:
                    pol_hit, pol_msg = False, None

                for hit, msg in [
                    (acl_hit, acl_msg),
                    (pab_hit, pab_msg),
                    (pol_hit, pol_msg)
                ]:
                    if hit:
                        findings.append({
                            "account_id": acc["account_id"],
                            "bucket": name,
                            "issue": msg
                        })

            except Exception as e:
                log(40, {
                    "bucket": name,
                    "error": str(e)
                })
    csv_data = generate_csv(findings)
    upload_report(REPORT_BUCKET, REPORT_KEY, csv_data)

    return findings
