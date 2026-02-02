import os
import asyncio
from dotenv import load_dotenv
import structlog
from azure.identity.aio import ClientSecretCredential
from msgraph.core import GraphServiceClient, GraphRequestAdapter
from kioto_authentication_azure.azure_identity_authentication_provider import AzureIdentityAuthenticationProvider

# Load Environment
load_dotenv()

AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
SITE_URL = os.getenv("SHAREPOINT_SITE_URL")
WAIT_SECONDS = int(os.getenv("WAIT_SECONDS", "65"))
HTTPS_PROXY = os.getenv("HTTPS_PROXY", None)  # Add proxy support

# Validate essential env variables
if not all([AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, SITE_URL]):
    raise EnvironmentError("Missing required Azure or SharePoint environment variables.")


# Logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
log = structlog.get_logger()


# Custom Exceptions
class DriveNotFoundError(Exception):
    pass


# Graph Client Factory
class GraphClientFactory:

    @staticmethod
    async def create() -> tuple[GraphServiceClient, ClientSecretCredential]:
        credential = ClientSecretCredential(
            tenant_id=AZURE_TENANT_ID,
            client_id=AZURE_CLIENT_ID,
            client_secret=AZURE_CLIENT_SECRET
        )

        auth_provider = AzureIdentityAuthenticationProvider(
            credentials=credential,
            scopes=["https://graph.microsoft.com/.default"]
        )

        # Create adapter with proxy if available
        adapter = GraphRequestAdapter(auth_provider)
        if HTTPS_PROXY:
            adapter._http_client.proxies = {"https://": HTTPS_PROXY}
            log.info("proxy_configured", proxy=HTTPS_PROXY)

        client = GraphServiceClient(request_adapter=adapter)
        return client, credential


# Get SharePoint Drive
async def get_drive(graph_client: GraphServiceClient, library_name: str = "Documents"):
    # Fetch site object
    site = await graph_client.sites.by_url(SITE_URL).get()
    site_id = site.id

    # Fetch drives
    drives_response = await graph_client.sites.by_id(site_id).drives.get()
    drives = drives_response.value or []

    # Find library
    drive = next((d for d in drives if d.name == library_name), None)
    if not drive:
        raise DriveNotFoundError(f"Library '{library_name}' not found in site {SITE_URL}")

    log.info("drive_found", drive_id=drive.id, drive_name=drive.name)
    return drive


# Recursively list all files
async def list_all_files(graph_client, drive_id):
    async def _list_items(parent_item, parent_path=""):
        files = []
        items = await parent_item.children.get()
        for item in items.value or []:
            current_path = f"{parent_path}/{item.name}" if parent_path else item.name
            if getattr(item, "folder", None):
                files.extend(await _list_items(graph_client.drives.by_id(drive_id).items.by_id(item.id), current_path))
            else:
                files.append({
                    "id": item.id,
                    "name": item.name,
                    "path": current_path,
                    "last_modified": item.lastModifiedDateTime
                })
        return files
    
    root_item = graph_client.drives.by_id(drive_id).root
    return await _list_items(root_item, "")


# Verify DCW Execution on all files
async def verify_dcw(graph_client, drive_id):
    """Verify DCW execution by checking if files are modified in the drive"""
    
    # Get all files from SharePoint
    files = await list_all_files(graph_client, drive_id)
    
    if not files:
        log.warning("dcw_verification_no_files", drive_id=drive_id)
        print("No files found in the SharePoint library.")
        return
    
    log.info("dcw_verification_started", total_files=len(files))
    
    # Capture original metadata
    original_metadata = {}
    for f in files:
        original_metadata[f["id"]] = await graph_client.drives.by_id(drive_id).items.by_id(f["id"]).get()
    
    log.info("dcw_initial_scan_complete", files_scanned=len(original_metadata))
    print(f"Initial scan complete. Waiting {WAIT_SECONDS} seconds before checking for changes...")
    
    # Wait for DCW to potentially modify files
    await asyncio.sleep(WAIT_SECONDS)
    
    # Check for modifications
    dcw_results = []
    for f in files:
        updated = await graph_client.drives.by_id(drive_id).items.by_id(f["id"]).get()
        original = original_metadata[f["id"]]
        dcw_ran = original.lastModifiedDateTime != updated.lastModifiedDateTime
        
        result = {
            "file_name": updated.name,
            "file_path": updated.webUrl,
            "before_modified": str(original.lastModifiedDateTime),
            "after_modified": str(updated.lastModifiedDateTime),
            "dcw_ran": dcw_ran
        }
        dcw_results.append(result)
        
        log.info(
            "dcw_check_result",
            file_name=updated.name,
            file_path=updated.webUrl,
            before_modified=str(original.lastModifiedDateTime),
            after_modified=str(updated.lastModifiedDateTime),
            dcw_ran=dcw_ran
        )
        
        status = 'Successful' if dcw_ran else 'Failed'
        print(
            f"{status} DCW | {updated.name} | "
            f"{original.lastModifiedDateTime} → {updated.lastModifiedDateTime}"
        )
    
    # Summary
    successful_count = sum(1 for r in dcw_results if r["dcw_ran"])
    log.info("dcw_verification_complete", total_files=len(files), modified_files=successful_count)
    print(f"\n--- Summary ---")
    print(f"Total files checked: {len(files)}")
    print(f"Files modified by DCW: {successful_count}")


async def main():
    log.info("application_started", mode="SHAREPOINT_DCW")
    graph_client, credential = await GraphClientFactory.create()
    try:
        drive = await get_drive(graph_client)
        await verify_dcw(graph_client, drive.id)
    finally:
        await credential.close()
    log.info("application_completed")


if __name__ == "__main__":
    asyncio.run(main())