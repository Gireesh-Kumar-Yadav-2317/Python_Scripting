import boto3

def assume_rds_client(role_arn, region):
    sts = boto3.client("sts")

    creds = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="RDSComplianceAudit"
    )["Credentials"]

    return boto3.client(
        "rds",
        region_name=region,
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"]
    )

