from django.db import models


#普通用户表
class User(models.Model):
    #主键自增
    id = models.AutoField('id', primary_key=True)
    username = models.CharField('账号', max_length=255, default='',unique=True)
    password = models.CharField('密码', max_length=255, default='')
    createTime = models.DateField('创建时间',auto_now_add=True)
    class Meta:
        db_table = "user"



#用户网站检测日志
class UserPrivacyLog(models.Model):

    username = models.CharField('用户名',  max_length=255, default='')
    #检测的URL
    source_url = models.CharField('检测的路由地址',max_length=255, default='',unique=True)
    #检测数据分用户对象展示
    phonenumber= models.IntegerField('电话号码',default='0')
    email = models.IntegerField('邮箱', default='0')
    idcard = models.IntegerField('身份证号', default='0')
    bankcard = models.IntegerField('银行卡号', default='0')
    #检测的时间
    LogTime = models.DateField('检测时间',auto_now_add=True)
    class Meta:
        db_table = "UserPrivacyLog"



#对不同的检测项分别开一张表进行存储，外键是username
#电话号码检测表
class UserPhone(models.Model):

    username = models.CharField('用户名',  max_length=255, default='')
    #检测数据分用户对象展示
    source_url = models.CharField('检测的路由地址', max_length=255, default='')
    phonenumber= models.CharField('电话号码',default='未检测到相关信息',max_length=255)
    #检测的时间
    LogTime = models.DateField('检测时间',auto_now_add=True)
    class Meta:
        db_table = "UserPhone"



#邮箱检测表
class UserEmail(models.Model):

    username = models.CharField('用户名',  max_length=255, default='')
    #检测数据分用户对象展示
    source_url = models.CharField('检测的路由地址', max_length=255, default='')
    email= models.CharField('邮箱',default='未检测到相关信息',max_length=255)
    #检测的时间
    LogTime = models.DateField('检测时间',auto_now_add=True)
    class Meta:
        db_table = "UserEmail"


#身份证号检测
class UserIdCard(models.Model):

    username = models.CharField('用户名',  max_length=255, default='')
    #检测数据分用户对象展示
    source_url = models.CharField('检测的路由地址', max_length=255, default='')
    idcard= models.CharField('身份证号',default='未检测到相关信息',max_length=255)
    #检测的时间
    LogTime = models.DateField('检测时间',auto_now_add=True)
    class Meta:
        db_table = "UserIdCard"


#银行卡号检测
class UserbankCard(models.Model):
    username = models.CharField('用户名',  max_length=255, default='')
    source_url = models.CharField('检测的路由地址', max_length=255, default='')
    bankcard= models.CharField('银行卡号',default='未检测到相关信息',max_length=255)
    #检测的时间
    LogTime = models.DateField('检测时间',auto_now_add=True)
    class Meta:
        db_table = "UserbankCard"