def evaluate(db_instance):
    if db_instance.get("BackupRetentionPeriod", 0) == 0:
        return True, "Automated backups are disabled"
    return False, None

