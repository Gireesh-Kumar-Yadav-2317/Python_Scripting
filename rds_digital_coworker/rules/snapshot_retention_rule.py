from datetime import datetime, timezone

def evaluate(snapshots, retention_days):
    violations = []
    now = datetime.now(timezone.utc)

    for snap in snapshots:
        age = (now - snap["SnapshotCreateTime"]).days
        if age > retention_days:
            violations.append(
                f"Snapshot older than {retention_days} days (age={age})"
            )

    return violations

