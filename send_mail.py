import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

def send_namecard(user_mail, file_path):
   fromaddr = 'nalidaofficial@gmail.com'
   toaddr = user_mail
   msg = MIMEMultipart() 
   msg['From'] = fromaddr 
   msg['To'] = toaddr 
   msg['Subject'] = "[날리다] 명함 제작 이미지 파일 전송"
   body = "자기이해 워크샵 날리다에 관심을 가져주셔서 감사합니다. \n\n답변해 주신 내용을 바탕으로 제작된 명함을 보내드립니다. \n\n감사합니다. \n \n \n \n 날리다 : 나를알리다 드림"
   msg.attach(MIMEText(body, 'plain')) 
   filename = file_path
   attachment = open(file_path, "rb") 
   p = MIMEBase('application', 'octet-stream') 
   p.set_payload((attachment).read()) 
   encoders.encode_base64(p) 
   p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
   msg.attach(p) 
   s = smtplib.SMTP('smtp.gmail.com', 587) 
   s.starttls() 
   s.login(fromaddr, "nalinyangbot") 
   text = msg.as_string() 
   s.sendmail(fromaddr, toaddr, text) 
   s.quit() 
