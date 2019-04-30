#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import Blueprint, request
import json

from geister.user.user import create_user, login_user
from geister.session.session import create_session, get_session, disable_session
from .utility.login_required import login_required

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
        abort(400, "Existed UserName")

    print ("username:" + str(user.name))
    print ("userid:" + str(user.id))
    result = {
                "user_id" : user.id,
                "name" : user.name
            }
    print (json.dumps(result))

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
        abort(400, "Login Failure")

    session, token = create_session(user.id)
    if session is None or token is None:
        print("Create Session Failure")
        abort(500, "Create Session Failure")
    print ("token:" + str(token))

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
# TODO:ログアウト時はセッションの期限切れでも通してもよいかも？
@user_app.route('/api/user_sessions/<int:session_id>', methods=['DELETE'])
@login_required
def logout(user_id, session_id):
    print("disable session_id:" + str(session_id))
    disable_session(session_id)
    return ""
