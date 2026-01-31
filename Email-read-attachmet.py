import structlog
import asyncio
from azure.identity.aio import ClientSecretCredential
from msgraph.aio import GraphServiceClient, GraphClientConfig , GraphRequestAdapter , AsyncHttpProvider
from kioto_authenitication_azure_identity_authentication_provider import AzureIdentityAuthenticationProvider


AXURE_TENANT_ID = "AZURE_TENANT_ID"
AXURE_CLIENT_ID = "AZURE_CLIENT_ID"
AXURE_CLIENT_SECRET = "AZURE_CLIENT_SECRET"

MAILBOX_USER = "MAILBOX_USER_EMAIL"

logger = structlog.get_logger()

async def read_email_attachments(client):
    messages = await client.users[MAILBOX_USER].message.get(
        query_parameters={
            "$top": 10,
            "$select": "subject,hasAttachments",
            "$filter": "hasAttachments eq true"
        }

    )

    for message in messages.value:
        email_log = {
            "subject": message.subject,
            "from": message.from_.email_address.address,
            "receivedDateTime": message.received_date_time.isoformat(),
            "attachments": []
        }

        attachment = await client.users[MAILBOX_USER].messages[message.id].attachments.get()
        for att in attachment.value:
            email_log["attachments"].append({
                "id": att.id,
                "name": att.name,
                "contentType": att.content_type,
                "size": att.size
            })
        logger.info("Email with attachments", email = email_log)

async def main():
    credits = ClientSecretCredential(
        tenant_id=AXURE_TENANT_ID,
        client_id=AXURE_CLIENT_ID,
        client_secret=AXURE_CLIENT_SECRET
    )
    auth_provider = AzureIdentityAuthenticationProvider(credits, scopes=["https://graph.microsoft.com/.default"])
    adapter = GraphRequestAdapter(auth_provider)
    transport = AsyncHttpProvider()
    client = GraphServiceClient(adapter, transport = transport)
    try:
        await read_email_attachments(client)
    finally:
        await credits.close()
        await transport.close()
if __name__ == "__main__":
    asyncio.run(main())
    