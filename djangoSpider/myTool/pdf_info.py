import os
def Ppdf2(username,LogTime,phonenumber,email,idcard,bankcard,source_url):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch


    pdfmetrics.registerFont(TTFont('msyh', 'msyh.ttc'))
    elements = []

    img = Image(r'D:/Users/Administrator/Desktop/logo.png')
    img.drawHeight = 0.5 * inch
    img.drawWidth = 2.31 * inch
    elements.append(img)

    # 读取reportlab定义好的样式表
    style = getSampleStyleSheet()
    # 可以用两个问号，查看有多少种现成的样式
    title = """ <para> <font face="msyh"> 检测报告 </font> </para>"""
    elements.append(Paragraph(title, style['Title']))
    elements.append(Spacer(1, 0.2 * inch))


    ### 3. 添加正文文字
    description = """
            <para>
                <font face="msyh">
                    -----------------------------------------------------------------------------------------------------
                    用户名：{}     &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
                    检测时间：{}   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    电话号码：{}   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br/>
                    邮箱：{}      &nbsp;<br/>
                    身份证号：{}   &nbsp;<br/>
                    银行卡号：{}   &nbsp<br/>
                    检测URL：{}   
                    -----------------------------------------------------------------------------------------------------
                </font>
            </para>
            """.format(username,LogTime,phonenumber,email,idcard,bankcard,source_url)
    elements.append(Paragraph(description, style["BodyText"]))


    elements.append(Paragraph("""<para><font face="msyh">检测建议：</font></para>""", style["h3"]))
    str1 = "当前来源URL检测到的个人消息泄露，主要以图片的形式泄露，在浏览该URL的时候注意保护个人消息！"
    str2 = "当前平台未检测到相关的个人信息泄露，为了避免潜在的个人信息安全隐患，浏览该URL时注意个人信息的保护！"

    if phonenumber==email==idcard==bankcard==0:
        content=str2
    else:
        content=str1

    description = """
              <para>
                  <font face="msyh">
                     &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;""" + content + """
                  </font>
              </para>
              """

    elements.append(Paragraph(description, style["BodyText"]))

    import time
    description = """
            <para>
                <font face="msyh">
                    -----------------------------------------------------------------------------------------------------
                    报告生成时间：{}
                </font>
            </para>
            """.format(time.strftime('%Y.%m.%d %H:%M:%S ', time.localtime(time.time())))
    elements.append(Paragraph(description, style["BodyText"]))
    elements.append(Spacer(1, 0.2 * inch))

    style.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    ptext = """<para><font face="msyh"><ent>本报告仅供参考</font></para>"""
    elements.append(Paragraph(ptext, style["Center"]))



    if not os.path.exists('media/PDF/' + str(username)):
        os.makedirs('media/PDF/' + str(username) )

    time=len(os.listdir('media/PDF/' + str(username)))
    pdf_dir = 'media/PDF/' + str(username) +"/" + str(time)
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    doc = SimpleDocTemplate(
        pdf_dir + '/'+'report_user_'+str(username) + '.pdf',
        pagesize=(A4[0], A4[1]),
        topMargin=30,
        bottomMargin=30)
    doc.build(elements)



from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
def create_watermark(f_jpg):
    f_pdf = 'mark.pdf'
    w_pdf = 20 * cm
    h_pdf = 20 * cm

    c = canvas.Canvas(f_pdf, pagesize=(w_pdf, h_pdf))
    c.setFillAlpha(0.3)  # 设置透明度
    # print
    c.drawImage(f_jpg, 7 * cm, 7 * cm, 6 * cm, 6 * cm)  # 这里的单位是物理尺寸


# username="qi"
# source_url="https://www.openvsm.com/recommend/article/784181.html"
# LogTime="2024-04-20"
# phonenumber="0"
# email="2"
# idcard="0"
# bankcard="0"
#
# Ppdf2(username,LogTime,phonenumber,email,idcard,bankcard,source_url)