from flask import Response
from flask_api import status
import json

def make_error_response(code, message):
        print ("[error]" + str(message))
        id = 0 # TODO:不明
        result = {
            "id" : id
            , "message" : message
        }
        return Response(
            json.dumps(result)
            , status.HTTP_400_BAD_REQUEST # note:クライアント側は400系のエラーのみメッセージを出すため、codeにかかわらず400とする
        )
