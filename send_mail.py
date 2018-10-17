import smtplib 
import shutil
import os
import random
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

from string import ascii_letters

from credentials import gmail_password
# make a file named `credentials.py` and add a line as:
# gmail_password = "GMAIL_PASSWORD"

try:
    os.mkdir('nalida')
except Exception:
    pass

def random_string(n):
    return ''.join(random.choice(ascii_letters) for _ in range(n))


def send_namecard(user_mail, file_path):
    send_as = 'nalida/' + random_string(5) + '.png'
    try:
        fromaddr = 'nalidaofficial@gmail.com'
        toaddr = user_mail
        msg = MIMEMultipart() 
        msg['From'] = fromaddr 
        msg['To'] = toaddr 
        msg['Subject'] = "[날리다] 명함 제작 이미지 파일 전송"
        body = "자기이해 워크샵 날리다에 관심을 가져주셔서 감사합니다. \n\n답변해 주신 내용을 바탕으로 제작된 명함을 보내드립니다. \n\n감사합니다. \n \n \n \n 날리다 : 나를알리다 드림"
        msg.attach(MIMEText(body, 'plain')) 
        shutil.copyfile(file_path, send_as)
        filename = send_as
        attachment = open(file_path, "rb") 
        p = MIMEBase('application', 'octet-stream') 
        p.set_payload((attachment).read()) 
        encoders.encode_base64(p) 
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
        msg.attach(p) 
        s = smtplib.SMTP('smtp.gmail.com', 587) 
        s.starttls() 
        s.login(fromaddr,gmail_password) 
        text = msg.as_string() 
        s.sendmail(fromaddr, toaddr, text) 
        s.quit() 
    except Exception:
        pass

def send_auth(user_mail, auth_key):
    try:
        fromaddr = 'nalidaofficial@gmail.com'
        toaddr = user_mail
        msg = MIMEMultipart() 
        msg['From'] = fromaddr 
        msg['To'] = toaddr 
        msg['Subject'] = "[날리다] 명함 제작 사용자 인증"
        body = "안녕하세요, 날리다: 나를알리다 입니다.  \n\n카카오톡 챗봇 '날리냥'을 통해 명함 제작을 요청하셔서 인증메일을 보내드립니다. \n\n만약 본인이 요청하신게 아니라면 메세지 삭제 후 fb.me/nalida2 를 통해 신고 부탁드립니다. \n\n\n날리냥에게 다음 인증키를 입력해주세요. \n\n 인증번호 :" + (str)(auth_key) 
        msg.attach(MIMEText(body, 'plain')) 
        s = smtplib.SMTP('smtp.gmail.com', 587) 
        s.starttls() 
        s.login(fromaddr, gmail_password) 
        text = msg.as_string() 
        s.sendmail(fromaddr, toaddr, text) 
        s.quit() 
    except Exception:
        pass
