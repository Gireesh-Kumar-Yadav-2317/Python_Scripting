import time
import copy
from datetime import datetime
import structlog


structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
log = structlog.get_logger()

# Abstract SharePoint Interface (Production Pattern)
class SharePointProvider:
    """
    Interface for SharePoint operations.
    In production → GraphProvider
    In dummy mode → DummyProvider
    """
    def list_files(self):
        raise NotImplementedError

    def get_file_metadata(self, file_id):
        raise NotImplementedError


# Dummy SharePoint Provider (NO credentials needed)

class DummySharePointProvider(SharePointProvider):

    def __init__(self):
        now = datetime.utcnow()
        self.files = {
            "file-1": {
                "id": "file-1",
                "name": "invoice1.pdf",
                "path": "/Finance/invoice1.pdf",
                "last_modified": now
            },
            "file-2": {
                "id": "file-2",
                "name": "invoice2.pdf",
                "path": "/Finance/invoice2.pdf",
                "last_modified": now
            },
            "file-3": {
                "id": "file-3",
                "name": "report.docx",
                "path": "/Reports/report.docx",
                "last_modified": now
            }
        }

    def list_files(self):
        log.info("list_files_called", source="dummy")
        return list(self.files.values())

    def get_file_metadata(self, file_id):
        return copy.deepcopy(self.files[file_id])

    def simulate_dcw(self, delay_seconds=3):
        """
        Simulates Digital Co-Worker execution.
        """
        log.info("dcw_simulation_started", delay_seconds=delay_seconds)
        time.sleep(delay_seconds)
        dcw_time = datetime.utcnow()

        for file in self.files.values():
            file["last_modified"] = dcw_time

        log.info("dcw_simulation_completed", modified_files=len(self.files))


# DCW Verification Logic (PRODUCTION LOGIC)
def verify_dcw(provider, single_file_id=None, wait_seconds=3):
    """
    Detect DCW execution by comparing last_modified timestamps
    """

    log.info("dcw_verification_started", single_file=bool(single_file_id))

    files = provider.list_files()

    if single_file_id:
        files = [f for f in files if f["id"] == single_file_id]

 
    before_state = {
        f["id"]: provider.get_file_metadata(f["id"])
        for f in files
    }


    provider.simulate_dcw(wait_seconds)


    for file in files:
        before = before_state[file["id"]]
        after = provider.get_file_metadata(file["id"])

        dcw_ran = before["last_modified"] != after["last_modified"]

        log.info(
            "dcw_check_result",
            file_name=after["name"],
            file_path=after["path"],
            before_modified=str(before["last_modified"]),
            after_modified=str(after["last_modified"]),
            dcw_ran=dcw_ran
        )

        print(
            f"{ 'Successful' if dcw_ran else 'Failed' } DCW "
            f"{after['path']} | "
            f"{before['last_modified']} → {after['last_modified']}"
        )

    log.info("dcw_verification_completed")


# =====================================================
# MAIN (Production Entry Point)
# =====================================================
def main():
    """
    Production-style entrypoint
    """
    log.info("application_started", mode="DUMMY")

    provider = DummySharePointProvider()

    verify_dcw(provider, single_file_id="file-3")

    verify_dcw(provider)

    log.info("application_completed")


if __name__ == "__main__":
    main()
