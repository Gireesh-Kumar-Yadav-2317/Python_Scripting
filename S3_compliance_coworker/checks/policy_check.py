import json

def check_policy(policy_str):
    policy = json.loads(policy_str)

    for stmt in policy.get("Statement", []):
        if stmt.get("Effect") == "Allow":
            principal = stmt.get("Principal")
            if principal == "*" or principal == {"AWS" : "*"}
            return True , "Bucket policy allows public principal"
    return False , None

