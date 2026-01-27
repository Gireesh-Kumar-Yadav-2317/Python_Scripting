import boto3

def assume_s3_client(role_arn):
    sts = boto3.client("s3")

    creds = sts.assume_role(
            RoleArn = role_arn,
            RoleSessionName = "S3ComplianceAudit")["Credentials"]
    return boto3.cleint(
            "s3"
            aws_access_key_id = creds["AccessKeyID"]
            aws_secert_access_key = creds["SecretAccessKey"]
            aws_session_token = creds["SessionToken"]
            )
