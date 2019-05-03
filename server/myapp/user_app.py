#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import Blueprint, request
import json

from db_model.user import create_user, login_user
from db_model.session import create_session, get_session, disable_session
from .utility.login_required import login_required
from .utility.error_response import make_error_response

user_app = Blueprint('user_app', __name__)

# ユーザー新規登録
@user_app.route('/api/users', methods=['POST'])
def signup():
    dic = request.json
    name = dic[u"name"]
    password = dic[u"password"]
    user = create_user(name, password)

    if user is None:
        # 既に作成済みのユーザー名
        return make_error_response(400, "Existed UserName")

    result = {
                "user_id" : user.id,
                "name" : user.name
            }
    return json.dumps(result)
    # return '''{
    #             , "user_id":33
    #             , "user_name":"hogehoge"
    #        }'''

# ログイン
@user_app.route('/api/user_sessions', methods=['POST'])
def login():
    dic = request.json
    name = dic[u"name"]
    password = dic[u"password"]
    user = login_user(name, password)
    if user is None:
        return make_error_response(400, "Login Failure")

    session, token = create_session(user.id)
    if session is None or token is None:
        print("[error]Create Session Failure")
        return make_error_response(500, "Create Session Failure")

    result = {
                "user_session_id": session.id,
                "access_token": token,
                "user_id" : user.id
            }
    return json.dumps(result)
    # return '''{
    #             "user_session_id":3
    #             , "access_token":""
    #             , "user_id":33
    #        }'''

# ログアウト
@user_app.route('/api/user_sessions/<int:session_id>', methods=['DELETE'])
@login_required
def logout(user_id, session_id):
    print("[info]disable session_id:" + str(session_id))
    disable_session(session_id)
    return ""
