def check_acl(acl):
    for grant in acl.get("Grants" , []):
        grantee = grant.get("Grantee" , {})
        uri = grantee.get("URI", "")
        if AllUsers in uri or "AuthenticatedUsers" in uri:
            return True , "ACL allow public access"
    return false , None
