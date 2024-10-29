from django.urls import path
from . import views
urlpatterns = [
    path('getSource', views.get_source, name='get_source'),
    path('userLogin', views.userlogin, name='userlogin'),


    path('downloadPdf', views.download_pdf, name='download_pdf'),
    path('getEcharts', views.get_echarts, name='get_echarts'),
    path('getLogInfo', views.get_loginfo, name='get_loginfo'),
    path('userRegister', views.register_user, name='register_user'),
    path('downloadCsv', views.download_csv, name='download_csv'),
    path('whoisDetection', views.wb_detection, name='whois_detection')



]
