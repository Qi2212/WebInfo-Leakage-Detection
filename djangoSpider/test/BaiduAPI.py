# 创建人：QI-BRO
# 开发时间：2024-04-20  0:28
import base64
import re
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoSpider.settings')
django.setup()
import requests
from urllib.parse import quote
from privacyApp.models import UserPhone, UserIdCard, UserbankCard, UserEmail, User


def match_pattern(text):
    phone_pattern = re.compile(r'\b\d{3,4}[-.]?\d{7,8}\b')
    email_pattern = re.compile(r'\b[\w.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
    id_card_pattern = re.compile(r'\b\d{17}[\dXx]\b')
    bank_card_pattern = re.compile(r'\b\d{16,19}\b')
    is_phone_number = bool(re.search(phone_pattern, text))
    is_email = bool(re.search(email_pattern, text))
    is_id_card = bool(re.search(id_card_pattern, text))
    is_bank_card = bool(re.search(bank_card_pattern, text))
    return is_phone_number, is_email, is_id_card, is_bank_card

#调用ocr进行图像识别，接入百度OCR识别，不需要下载本地图片，直接传入图片的有效连接地址即可
def ocr_image(username,source_url,image_url):
    try:
        #鉴定为有效的图片url以后就接入百度的OCR 文字识别进行内容检测
        #add/replace your access_token -> run test/baidu_token.py to access token
        access_token=""
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={access_token}"
        payload = f'url={image_url}&detect_direction=false&paragraph=false&probability=false'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        #获取返回的文字识别数据
        data = response.json()
        for res in data['words_result']:
            is_phone_number, is_email, is_id_card, is_bank_card=match_pattern(res['words'])
            if not (is_phone_number or is_email or is_id_card or is_bank_card):
                continue
            else:
                user_instance, created = User.objects.get_or_create(username=username)
                if is_phone_number:
                    new_user_phone = UserPhone.objects.create(username=user_instance,source_url=source_url,phonenumber=res['words'])
                    new_user_phone.save()

                if is_email:
                    new_user_email = UserEmail.objects.create(username=user_instance,source_url=source_url,email=res['words'])
                    new_user_email.save()

                if is_id_card:
                    new_id_card = UserIdCard.objects.create(username=user_instance, source_url=source_url,idcard=res['words'])
                    new_id_card.save()
                if is_bank_card:
                    new_bank_card = UserbankCard.objects.create(username=user_instance, source_url=source_url,bankcard=res['words'])
                    new_bank_card.save()

    except Exception as e:
        print(e)


def get_base64(path, urlencoded=True):
    import urllib
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
        print(content)
    return content

def pdf_detection(username,source_url,file_path):
    #接入百度的PDF文本识别就好，将本地下载好的PDF进行bs64编码，传入百度识别

    try:
        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token="
        content=get_base64(file_path)
        # pdf_file 可以通过 get_file_content_as_base64("C:\fakepath\这是一次PDF检测.pdf",True) 方法获取
        payload = f'pdf_file={content}&detect_direction=false&paragraph=false&probability=false'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)
        # 获取返回的文字识别数据
        data = response.json()
        for res in data['words_result']:
            print(f"这是百度的识别结果:{res['words']}\n")
            # 接下来是对文字识别的结果进行 电话号码，邮箱，身份证号，银行卡号的识别 识别以后响应的存入数据库中
            is_phone_number, is_email, is_id_card, is_bank_card = match_pattern(res['words'])
            if not (is_phone_number or is_email or is_id_card or is_bank_card):
                print(f"{res['words']} 这条文字识别中没有匹配到个人信息！\n ")
                continue
            else:
                if is_phone_number:
                    print(f"{res['words']} 当前信息检测到电话号码")
                    new_user_phone = UserPhone.objects.create(username=username, source_url=source_url,
                                                              phonenumber=res['words'])
                    new_user_phone.save()

                if is_email:
                    print(f"{res['words']} 当前信息检测到邮箱")
                    new_user_email = UserEmail.objects.create(username=username, source_url=source_url,
                                                              email=res['words'])
                    new_user_email.save()
                if is_id_card:
                    print(f"{res['words']} 当前信息检测到身份证号码")
                    new_id_card = UserIdCard.objects.create(username=username, source_url=source_url,
                                                            idcard=res['words'])
                    new_id_card.save()
                if is_bank_card:
                    print(f"{res['words']} 当前信息检测到银行卡号")
                    new_bank_card = UserbankCard.objects.create(username=username, source_url=source_url,
                                                                bankcard=res['words'])
                    new_bank_card.save()
    except Exception as e:
        print(f"PDF 检测遇到错误 {file_path}: {e}\n")

#test example
"""
    image_url="https://img0.baidu.com/it/u=908750362,715080928&fm=253&fmt=auto?w=500&h=345"
    encoded_url = quote(image_url)
    username='qi'
    source_url='https://img1.baidu.com/it/u=4106003546,4225998900&fm=253&fmt=auto&app=138&f=JPEG?w=409&h=277'
    ocr_image(username,source_url,encoded_url)
"""

