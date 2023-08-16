import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config.notice import *

# メール送信
class EMailSend():
    # メール送信
    def sendEmail(self, message: str):
        msg: MIMEMultipart = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = "[SuricataAlertNotice] 不審なパケットを検知しました！"
        msg.attach(MIMEText(message, "plain"))

        # GmailのSMTPサーバーへの接続とメール送信
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls() # TLS暗号化の開始
                server.login(SMTP_USER, SMTP_PASS) # SMTPサーバーへのログイン

                server.send_message(self.msg)
        except Exception as e:
            print(e)