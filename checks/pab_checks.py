def check_public_access_block(pab):
    if not pab:
        return True, "Public Access Block not configured"

    if not all(pab.values()):
        return True, "Public Access Block partially disabled"

    return False, None

