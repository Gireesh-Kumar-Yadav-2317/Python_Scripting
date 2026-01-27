# RDS Backup & Snapshot Compliance Digital Co-Worker

## Overview
This project implements an **enterprise-grade Digital Co-Worker** to audit **RDS backup configuration and snapshot retention compliance** across **multiple AWS accounts**.

The solution is **AWS-only**, **read-only by default**, **Lambda-compatible**, and produces **encrypted audit-ready CSV reports** for security and compliance teams.

---

## Features
- Multi-account scanning via AWS STS AssumeRole
- Detects RDS instances with **backups disabled**
- Detects **old snapshots beyond retention policy**
- Structured JSON logging for CloudWatch / SIEM
- Encrypted CSV compliance reports stored in S3
- Fail-soft design for high reliability
- Easily extensible rule-based architecture

---

## Architecture


