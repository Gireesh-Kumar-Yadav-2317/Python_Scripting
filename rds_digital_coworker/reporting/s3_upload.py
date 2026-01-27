import boto3

def upload_report(bucket, key, content):
    s3 = boto3.client("s3")

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=content,
        ServerSideEncryption="aws:kms"
    )

