#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import request
import functools
from db_model.session import decode_access_token
from .error_response import make_error_response

# 認証関数
# 認証が必要なメソッドはこの関数を事前に呼び出すように指定する
def login_required(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization')
        _, token = header.split("=")
        token = str(token).strip("\"")
        user_id, error_message = decode_access_token(token)
        if user_id is None:
            # note:トークンの期限切れ等でエラーを返すと、クライアントが進行不能になるが、クライアント側で正しく処理すべき
            return make_error_response(400, error_message)
        return method(user_id, *args, **kwargs)
    return wrapper
