# S3 Public Access Compliance Digital Co-Worker

## Overview
This project is an **enterprise-grade, cloud-native Digital Co-Worker** designed to **audit public access exposure of S3 buckets** across **multiple AWS accounts**.  
It is **read-only by default**, **Lambda-compatible**, and produces **audit-ready, encrypted CSV reports** for security and compliance teams.

---

## Features
- **Multi-account support** via AWS STS AssumeRole
- **Multi-region support** (per account configuration)
- **Public access detection**:
  - Bucket ACLs (AllUsers / AuthenticatedUsers)
  - Bucket Policies (`Principal: *`)
  - Public Access Block misconfiguration
- **Structured JSON logging** for SIEM and CloudWatch
- **Audit report generation** as encrypted CSV in S3
- **Fail-soft design**: continues scanning even if a bucket fails
- **Extensible rule engine**: easy to add new checks
- **AWS-only implementation** (no local OS dependencies)
- **Lambda-compatible execution** (can run on EventBridge schedule)

---

---

## Configuration

All configuration is **environment variable-driven** for Lambda / CI/CD compatibility.

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `ACCOUNTS_JSON` | JSON array of accounts with `account_id` and `role_arn`. Example: `[{"account_id":"111111111111","role_arn":"arn:aws:iam::111111111111:role/SecurityAuditRole"}]` |
| `REPORT_BUCKET` | S3 bucket where audit CSV report will be stored (encrypted with SSE-KMS) |
| `REPORT_KEY` (optional) | Key name of the CSV report, default: `s3_public_audit.csv` |

---

## Usage

### Lambda Deployment

1. Package all files and dependencies into a **Lambda deployment package**.
2. Assign Lambda **IAM role** with:
   - `sts:AssumeRole` for target accounts
   - `s3:PutObject` for REPORT_BUCKET
   - `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`
3. Set **environment variables** (`ACCOUNTS_JSON`, `REPORT_BUCKET`, `REPORT_KEY`).
4. Configure **EventBridge rule** to trigger Lambda daily (or as required).

### Local Testing

```bash
export ACCOUNTS_JSON='[{"account_id":"111111111111","role_arn":"arn:aws:iam::111111111111:role/SecurityAuditRole"}]'
export REPORT_BUCKET='central-security-reports'

python main.py





Logging

Structured JSON logs with fields:

bucket

account_id

issue

correlation_id (unique per log)

Logs go to CloudWatch (or SIEM via subscription).

Example log entry:

{
  "bucket": "my-public-bucket",
  "account_id": "111111111111",
  "issue": "Bucket policy allows public principal",
  "correlation_id": "5b1c3f90-6f9b-4f23-b1f2-8cfa7e2d8f32"
}

Reporting

Audit CSV report stored in S3 with SSE-KMS encryption

Columns:

AccountId

Bucket

Issue

CheckedAt

Example CSV row:

111111111111,my-public-bucket,Bucket policy allows public principal,2026-01-27T09:30:00Z
