import time

from botocore.exceptions import ClientError

def aws_retry(callable_fn , retries =3 base_delay = 2):
    for attempt in range(1, retries +1):
        try:
            return callable_fn()
        except ClientError as e:
            if attempt == retries:
                raise
            time.sleep(base_delay * attempt)
