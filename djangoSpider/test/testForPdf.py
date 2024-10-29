# 创建人：QI-BRO
# 开发时间：2024-04-20  14:13
import PyPDF2

def extract_text_from_pdf(pdf_path):
    text_content = ''
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text_content += page.extract_text() + ''
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    #返回读取出来的PDF 文本内容
    return text_content

text_content=extract_text_from_pdf(r'./media/PDF/qi/0/report_user_qi.pdf')
print(text_content)