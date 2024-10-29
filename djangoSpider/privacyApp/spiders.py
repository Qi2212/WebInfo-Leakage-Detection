import base64
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from privacyApp.models import UserPhone, UserEmail, UserIdCard, UserbankCard


def crawl_website(username,url):
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    links = [a['href'] for a in soup.find_all('a') if 'href' in a.attrs]
    links.append(url)
    for link in links:
        detail_url = urljoin(response.url, link)
        if detail_url.endswith('.pdf'):
            file_path = download_file(detail_url)
            if file_path:
                print("开始检测PDF")
                pdf_detection(username,url,file_path)
        else:
            print("开始检测图片")
            print(detail_url)
            image_detection(username,url,detail_url)





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
    try:
        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token=24.90698092ececec4e335e07e262140415.2592000.1716131547.282335-62291300"
        content=get_base64(file_path)
        payload = f'pdf_file={content}&detect_direction=false&paragraph=false&probability=false'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)
        data = response.json()
        print(
            f"================================本次PDF进行百度文字识别一共识别到 {data['words_result_num']} 条数据=================================")
        for res in data['words_result']:
            print(f"这是百度的识别结果:{res['words']}\n")
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


#匹配文字识别中的个人信息
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


#图片个人信息检测，包括OCR接入，检测结果存入数据库
def image_detection(username,suorce_url,detail_url):
    headers = {
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36 Edg/123.0.0.0"
    }
    response = requests.get(detail_url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    images = [img['src'] for img in soup.find_all('img', src=True)]
    print("这是images的长度:",len(images))
    for image_url in images:
        image_url = urljoin(response.url, image_url)
        image_url = image_url.replace('\\', '/')
        try:
            ocr_image(username,suorce_url,image_url)
        except Exception as e:
            print(f"{image_url}  这张图片的检测过程中遇到了问题 ： {e}")
            continue
    if len(images)==0:
        try:
            ocr_image(username,suorce_url,suorce_url)
        except Exception as e:
            print("检测遇到错误：",e)





#调用ocr进行图像识别，接入百度OCR识别，不需要下载本地图片，直接传入图片的有效连接地址即可
def ocr_image(username,source_url,image_url):
    try:
        #鉴定为有效的图片url以后就接入百度的OCR 文字识别进行内容检测
        #百度接口的图片地址需要进行转码为百分比制
        image_url= quote(image_url)
        print("这是转换以后的imageurl:",image_url)
        access_token="24.90698092ececec4e335e07e262140415.2592000.1716131547.282335-62291300"
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={access_token}"

        payload = f'url={image_url}&detect_direction=false&paragraph=false&probability=false'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        data = response.json()
        print(f"================================本次图片进行百度文字识别一共识别到 {data['words_result_num']} 条数据=================================")
        for res in data['words_result']:
            print(f"这是百度的识别结果:{res['words']}\n")
            is_phone_number, is_email, is_id_card, is_bank_card=match_pattern(res['words'])

            if not (is_phone_number or is_email or is_id_card or is_bank_card):
                print(f"{res['words']} 这条文字识别中没有匹配到个人信息！\n ")
                continue
            else:
                if is_phone_number:
                    print(f"{res['words']} 当前信息检测到电话号码")
                    new_user_phone = UserPhone.objects.create(username=username,source_url=source_url,phonenumber=res['words'])
                    new_user_phone.save()

                if is_email:
                    print(f"{res['words']} 当前信息检测到邮箱")
                    new_user_email = UserEmail.objects.create(username=username,source_url=source_url,email=res['words'])
                    new_user_email.save()
                if is_id_card:
                    print(f"{res['words']} 当前信息检测到身份证号码")
                    new_id_card = UserIdCard.objects.create(username=username, source_url=source_url,idcard=res['words'])
                    new_id_card.save()
                if is_bank_card:
                    print(f"{res['words']} 当前信息检测到银行卡号")
                    new_bank_card = UserbankCard.objects.create(username=username, source_url=source_url,bankcard=res['words'])
                    new_bank_card.save()

    except Exception as e:
        print(f"图片检测失败 {image_url}: {e}\n")



#下载pdf的算法
def download_file(detail_url, directory="./downloads"):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    local_filename = os.path.basename(detail_url)
    local_filepath = os.path.join(directory, local_filename)
    try:
        with requests.get(detail_url, stream=True) as r:
            with open(local_filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("PDF 文件下载成功！")
        return local_filepath
    except Exception as e:
        print(f"下载PDF文件出错！ {detail_url}: {e}")
        return None
