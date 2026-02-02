import asyncio
import json
from datetime import datetime, timezone
import random
import sys
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

log = structlog.get_logger()


def list_dummy_files():
    log.info("list_files_called", source="dummy")
    now = datetime.now(timezone.utc)
    return [
        {"id": "1", "name": "invoice1.pdf", "path": "/Finance/invoice1.pdf", "last_modified": now},
        {"id": "2", "name": "invoice2.pdf", "path": "/Finance/invoice2.pdf", "last_modified": now},
        {"id": "3", "name": "report.docx", "path": "/Reports/report.docx", "last_modified": now},
    ]

async def simulate_multiple_dcws(files, delay=120):
    log.info("dcw_simulation_started", dcw_count=3, delay_seconds=delay)
    await asyncio.sleep(delay)

    dcw_names = ["DCW-Finance", "DCW-Reports", "DCW-Archiver"]

    for f in files:
        if random.choice([True, False]):
            f["last_modified"] = datetime.now(timezone.utc)
            f["dcw"] = random.choice(dcw_names)

    log.info("dcw_simulation_completed")


async def verify_multiple_dcws(wait_seconds=120):
    log.info("dcw_verification_started", mode="MULTI_DCW")

    files = list_dummy_files()

    snapshot = {
        f["id"]: f["last_modified"] for f in files
    }

    await simulate_multiple_dcws(files, wait_seconds)

    # Compare results
    dcw_hits = 0
    for f in files:
        before = snapshot[f["id"]]
        after = f["last_modified"]

        dcw_ran = after > before
        if dcw_ran:
            dcw_hits += 1

        log.info(
            "dcw_check_result",
            file_name=f["name"],
            file_path=f["path"],
            before_modified=before.isoformat(),
            after_modified=after.isoformat(),
            dcw_ran=dcw_ran,
            dcw_name=f.get("dcw", "unknown")
        )

    log.info(
        "dcw_verification_completed",
        total_files=len(files),
        dcw_triggered_files=dcw_hits
    )

async def main():
    log.info("application_started", mode="DUMMY")
    await verify_multiple_dcws()
    log.info("application_completed")

if __name__ == "__main__":
    asyncio.run(main())