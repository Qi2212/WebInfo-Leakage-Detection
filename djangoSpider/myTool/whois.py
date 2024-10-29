# 创建人：QI-BRO
# 开发时间：2024-04-22  14:20
import json
import requests

def whois_detection(domainName):
    #这是一个域名检测网站，直接向它发请求申请域名检测就行
    url = 'https://whois.xinnet.com/domainWhois/queryWhois'
    payload = {'domainName': domainName, 'refreshFlag': 'false', 'randStr': '', 'ticket': ''}
    headers = {'User-Agent': 'Mozilla/5.0'}
    cookies = {'session_id': 'abcdef123456'}

    response = requests.post(url, data=payload, headers=headers, cookies=cookies)

    print("Response status code:", response.status_code)

    #进行json解析参数
    data=json.loads(response.text)
    print("data:", data)
    #检测时间
    addTime=data['addTime']
    #域名
    domainName=data['domainName']
    #注册商
    registrar=data['registrar']
    #注册人邮箱
    registrantEmail=data['registrantEmail']
    #注册日期
    registrantDate=data['registrantDate']
    #到期时间
    expirationDate=data['expirationDate']
    #更新时间
    updatedDate=data['updatedDate']
    #域名状态
    domainStatus=data['domainStatus']

    print(f"检测时间：{addTime}\n"
          f"检测域名:{domainName}\n"
          f"注册商:{registrar}\n"
          f"注册人邮箱:{registrantEmail}\n"
          f"注册日期:{registrantDate}\n"
          f"到期时间：{expirationDate}\n"
          f"更新时间：{updatedDate}\n"
          f"域名状态：{domainStatus}")

    return {'addTime':data['addTime'],
    'domainName':data['domainName'],
    'registrar':data['registrar'],
    'registrantEmail':data['registrantEmail'],
    'registrantDate':data['registrantDate'],
    'expirationDate':data['expirationDate'],
    'updatedDate':data['updatedDate'],
    'domainStatus':data['domainStatus']}

# whois_detection("baidu.com")