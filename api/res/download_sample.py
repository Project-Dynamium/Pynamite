from __init__ import *

# Take aliyun oss as example
import oss2

auth = oss2.Auth('', '')
bucket = oss2.Bucket(auth, '', '')

def get_download_link(path):
    path = "your_path/" + path

    if not bucket.object_exists(path):
        return {"status":404}

    url = bucket.sign_url('GET', path, 2, slash_safe=True)

    return {"status":200,"result":url}