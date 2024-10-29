# 创建人：QI-BRO
# 开发时间：2024-04-19  23:10
#接入百度OCR获得access_token 一月一换
import requests


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    API_KEY = "os7KwO2zK0LfQAJBCDfuf8pd"
    SECRET_KEY = "oKXKsFsBXrCbVMlDyz0pmuZfgyqUAYgA"
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

back=get_access_token()
print(back)