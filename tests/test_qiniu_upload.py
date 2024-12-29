# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_file, etag
import qiniu.config
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

#需要填写你的 Access Key 和 Secret Key
access_key = Config.QINIU_AK
secret_key = Config.QINIU_SK

#构建鉴权对象
q = Auth(access_key, secret_key)

#要上传的空间
bucket_name = 'dreampath'

#上传后保存的文件名
key = 'avatar/my-python-logo.png'

#生成上传 Token，可以指定过期时间等
token = q.upload_token(bucket_name, key, 3600)

#要上传文件的本地路径
localfile = os.path.join(os.path.dirname(__file__), '123.png')

ret, info = put_file(token, key, localfile, version='v2')
print(info)
assert ret['key'] == key
assert ret['hash'] == etag(localfile)
