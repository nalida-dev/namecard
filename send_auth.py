import smtplib 
import shutil
import os
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

from credentials import gmail_password
# make a file named `credentials.py` and add a line as:
# gmail_password = "GMAIL_PASSWORD"


def send_auth(user_mail, auth_key):
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
