import csv
import json
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from myTool.whois import whois_detection
from privacyApp.models import User, UserPrivacyLog
from privacyApp.spiders import *
from django.http import JsonResponse, HttpResponse
from myTool.pdf_info import Ppdf2
def get_source(request):
    if request.method=="GET":
        url = request.GET.get('url')
        username = request.GET.get('username')
        if not url:
            return JsonResponse({'error': 'URL参数不能为空'})
        print(f"这是前端传递过来的{url}")

        crawl_website(username,url)
        total_count = []
        # 遍历每个表进行查询和统计
        for i,Table in enumerate([UserPhone,UserEmail,UserIdCard,UserbankCard]):
            # 查询符合条件的记录数量
            matches = Table.objects.filter(username=username, source_url=url)
            count = matches.count()
            # 打印每个表的统计结果
            print(f"在 {Table.__name__} 中，符合条件的数量为: {count}")
            #每个类别的检测信息最终存储到数组中返回 total_count[0]:电话 total_count[1]:邮箱 total_count[2]:身份证号 total_count[3]:银行卡号
            total_count.append(count)

        #UserPrivacyLog进行检测记录
        log = UserPrivacyLog.objects.filter(username=username, source_url=url)
        if len(log) == 1:
            log[0].phonenumber = total_count[0]
            log[0].email = total_count[1]
            log[0].idcard = total_count[2]
            log[0].bankcard = total_count[3]
        elif len(log)==0:
            new_log=UserPrivacyLog.objects.create(username=username,source_url=url,phonenumber=total_count[0],
                                       email=total_count[1],idcard=total_count[2],bankcard=total_count[3])
            new_log.save()
        else:
            return JsonResponse({'code':204,'msg':'数据库信息出错！请联系管理员进行检查'})

        if total_count[0]==total_count[1]==total_count[2]==total_count[3]==0:
            return JsonResponse({'code':200,'source_url':url,
                                 'is_info':0,
                                 'msg':'页面不存在隐私信息泄露'})
        else:
            return JsonResponse({'code': 200,'source_url':url,
                                 'is_info':1,
                                 'phone':total_count[0],
                                 'email':total_count[1],
                                 'idcard':total_count[2],
                                 'bankcard':total_count[3]})

    return JsonResponse({'code':203,'msg':'请求方式错误！'})

def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            username = data.get('username', '')
            password = data.get('password', '')

            if User.objects.filter(username=username).exists():
                return JsonResponse({'code':201,'msg':'当前用户名已存在！'})

            user = User(username=username, password=password)
            user.save()

            return JsonResponse({'code':200,'msg':'创建成功！请重新登录'})
        except Exception as e:
            return JsonResponse({'code':202,'msg':f"遇到错误: {e}"})

    return JsonResponse({'code':203,'msg':'请求方式错误！'})






@csrf_exempt
def userlogin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            username = data.get('username')
            pwd = data.get('password')
            print(username, pwd)
            try:
                user = User.objects.get(username=username, password=pwd)

                return JsonResponse({
                        'code':200,
                        'username':username,
                        'msg':'success'
                })
            except:
                print("当前接收到普通用户的登录的请求，用户名或密码错误")
                return JsonResponse({
                    'code':201,
                    'msg': '用户名或密码错误'
                })
        except Exception as e:
            print(e)
            return JsonResponse({
                'code': 202,
                'msg': '遇到错误'
            })

    return JsonResponse({'code':201,'msg':'请求方式错误！'})




#下载PDF
def download_pdf(request):
    if request.method == "GET":
        print("ok")
        username=request.GET.get('username','')
        source_url = request.GET.get('source_url','')
        try:
            data=UserPrivacyLog.objects.get(username=username,source_url=source_url)
            Ppdf2(data.username,data.LogTime,data.phonenumber,data.email,data.idcard,data.bankcard,data.source_url)

            root_path = f"./media/PDF/{username}/"

            directories = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
            directories.sort(key=int)
            latest_directory = directories[-1]
            latest_directory_path = os.path.join(root_path, latest_directory)

            file_path = latest_directory_path+f"/report_user_{username}.pdf"
            if os.path.exists(file_path):
                with open(file_path, 'rb') as pdf_file:
                    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="report_user_{username}.pdf"'
                    print("ok156")
                    return response


        except Exception as e:
            print(e)
            return JsonResponse({'code':201,'msg':'当前数据库不存在检测记录，请先进行检测！'})




def get_echarts(request):
    if request.method == "GET":
        username=request.GET.get('username')
        if not UserPrivacyLog.objects.filter(username=username):
            return JsonResponse({'code':201,'msg':'数据库中暂无该账号的检测记录'})
        sum_phone=0
        sum_email=0
        sum_idcard=0
        sum_bankcard=0
        echats_array1=[]
        echats_array2 = []

        try:
            logs=UserPrivacyLog.objects.filter(username=username)
            for log in logs:
                sum_phone+=int(log.phonenumber)
                sum_email+=int(log.email)
                sum_idcard += int(log.idcard)
                sum_bankcard += int(log.bankcard)
                #单条记录
                log_num=[int(log.phonenumber),int(log.email),int(log.idcard),int(log.bankcard)]
                echats_array1.append(log_num)
                print(echats_array1)
            #检测到的泄露总数
            sum_type=[sum_phone,sum_email,sum_idcard,sum_bankcard]
            sum_all=sum_phone+sum_email+sum_idcard+sum_bankcard
            if sum_all==0:
                return JsonResponse({'code':205,'msg':'该账号的检测记录中未发现泄露信息','sum_type':sum_type,'echarts1':[],'echarts2':[]})

            if len(echats_array1)>3:
                #图表只展示3条记录
                echats_array1=echats_array1[0:3]
            for item in echats_array1:
                #保留两位小数
                per_phone=round(item[0]/sum_all*100,2)
                per_email = round(item[1]/sum_all*100,2)
                per_idcard = round(item[2]/sum_all*100,2)
                per_bankcard = round(item[3]/sum_all*100,2)
                per_num=[per_phone,per_email,per_idcard,per_bankcard]
                echats_array2.append(per_num)

            return JsonResponse({'code':200,'sum_type':sum_type,'echarts1':echats_array1,'echarts2':echats_array2})

        except Exception as e:
            print(e)
            return JsonResponse({'code':202,'msg':f'遇到错误: {e}'})

    return JsonResponse({'code': 203, 'msg': '请求方式错误！'})




#获取用户检测的日志接口
def get_loginfo(request):
    if request.method == "GET":
        username=request.GET.get('username','')

        try:
            logs=UserPrivacyLog.objects.filter(username=username)

            if len(logs)==0:
                return JsonResponse({'code':201,'msg':'当前账号暂无任务检测记录'})

            else:
                logs_data = [{
                    'id': log.id,
                    'source_url':log.source_url,
                    'logtime':log.LogTime
                } for log in logs]

                return JsonResponse({'code':200,'msg':'success','data':logs_data},safe=False)
        except Exception as e:
            print(e)
            return JsonResponse({'code':202,'msg':f'遇到错误: {e}'})

    return JsonResponse({'code': 203, 'msg': '请求方式错误！'})






#导出CSV日志接口
def download_csv(request):
    if request.method == "GET":
        username=request.GET.get('username','')
        try:
            if not UserPrivacyLog.objects.filter(username=username):
                return JsonResponse({'code':201,'msg':'当前账号暂无任何的检测记录！'})
            logs = UserPrivacyLog.objects.filter(username=username).values_list(*['id','username','LogTime',
                                                                                  'source_url','phonenumber','email','idcard','bankcard'])
            # 创建一个HttpResponse对象，并设置content_type为text/csv
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="user_privacy_logs.csv"'
            writer = csv.writer(response)

            fields = ['id','用户名','检测时间','来源 URL','检测到的电话号码数量','检测到的邮箱数量','检测到的身份证号数量','检测到的银行卡号数量']  # 替换为你的模型字段名
            writer.writerow(fields)


            for log in logs:
                row_data = [smart_str(value) for value in log]
                writer.writerow(row_data)

            return response

        except Exception as e:
            print(e)
            return JsonResponse({'code':202,'msg':f'遇到错误: {e}'})

    return JsonResponse({'code': 203, 'msg': '请求方式错误！'})





#网站信息检测接口
def wb_detection(request):
    print(request.method)
    if request.method=='POST':
        try:
            print("ok1")
            #post提交参数,domainName
            #这个网站的域名信息检测，就只是一个信息查询的功能，就不存入数据库中了
            json_data=json.loads(request.body)
            domainName=json_data['domainName'].strip()
            print("ok2")
            print("domainName:",domainName)
            #调用myTool里的函数，向指定的检测网站发去 域名 检测请求
            back_data=whois_detection(domainName)
            return JsonResponse(back_data)
        except Exception as e:
            print(e)
            return JsonResponse({'code':202,'msg':f'遇到错误: {e}'})

    else:
        return JsonResponse({'code': 203, 'msg': '请求方式错误！'})



