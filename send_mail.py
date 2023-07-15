import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config.notice import *

# メール送信
class EMailSend():
    # MIMEメッセージの作成
    def __init__(self):
        self.msg: MIMEMultipart = MIMEMultipart()
        self.msg["From"] = SENDER_EMAIL
        self.msg["To"] = RECEIVER_EMAIL
        self.msg["Subject"] = "[SuricataAlertNotice] 不審なパケットを検知しました！"

    # メール送信
    def sendEmail(self, message: str):
        # メール本文の追加
        self.msg.attach(MIMEText(message, "plain"))

        # GmailのSMTPサーバーへの接続とメール送信
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls() # TLS暗号化の開始
                server.login(SMTP_USER, SMTP_PASS) # SMTPサーバーへのログイン

                server.send_message(self.msg)
        except Exception as e:
            print(e)