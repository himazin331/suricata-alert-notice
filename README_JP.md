# Suricata Alert Notice App

Suricataがアラートを発報したときに、メールまたはLINE(あるいは両方)で通知するアプリです。

## 前提
- 本アプリはSuricataが出力する`eve.json`を読み取りますので、出力されるようにSuricataの設定をしてください。

## 準備
### 1. config/notice.pyの設定
メッセージ送信に伴うメールサーバ認証の設定やLINE Notifyのトークン設定を行います。
なお、LINE Notifyの設定等は割愛。
```python
# config/notice.py
SENDER_EMAIL: str = "your_email@example.com"  # 送信元アドレス
RECEIVER_EMAIL: str = "your_email@gmail.com"  # 送信先アドレス
SMTP_SERVER: str = "smtp.gmail.com"           # SMTPサーバホスト名 (今回はGmailを利用)
SMTP_PORT: int = 587                          # SMTPサーバポート
SMTP_USER: str = "your_email@gmail.com"       # SMTPサーバ認証ユーザ名
SMTP_PASS: str = "**********************"     # SMTPサーバ認証パスワード

LINE_NOTIFY_TOKEN: str = "***************************" # Line Notify API Access Token
```

### 2. config/general.pyの設定
通知設定や通知対象とするシグネチャIDの指定などの設定を行います。
```python
# config/general.py
from enum import Enum

class NoticeType(Enum):
    Nothing = 0     # 通知しない (動作確認用)
    Email = 1       # メール通知
    LineNotify = 2  # LINE通知
    Both = 3        # メール&LINE通知

EVE_JSONL_PATH: str = "/usr/local/var/log/suricata/eve.json" # eve.json配置場所
NOTICE_TYPE = NoticeType.Email  # 通知設定
# SIGNATURE_ID_RANGE内のシグネチャのみ通知
SIGNATURE_ID_RANGE: tuple[int, int] = (2000000, 2099999) # ET Open Rulesets
# シグネチャID範囲に加え、シグネチャメッセージにFILTER_SIG_CATEGORYが含まれるシグネチャのみ通知
FILTER_SIG_CATEGORY: list[str] = [
        "Attack Response", "DNS", "DOS", "Exploit", "FTP", 
        "ICMP", "IMAP", "Malware", "NETBIOS", "Phishing", 
        "POP3", "RPC", "Shellcode", "SMTP", "SNMP", "SQL", 
        "TELNET", "TFTP", "Web Client", "Web Server", "Web Specific Apps", "WORM"
    ] # "ET xxx"のxxx。(例: "ET Exploit ~")
```
今回私は、Emerging threats open rulesetのシグネチャID`2000000 ~ 2099999`に該当するかつ、
FILTER_SIG_CATEGORYの文字列を含むalertのみを通知するように設定。

#### 参考
- Emerging threats open ruleset シグネチャID割当領域: \
https://community.emergingthreats.net/t/signature-id-allocation-ranges/491
- Emerging threats open ruleset ルールカテゴリ: \
https://community.emergingthreats.net/t/current-suricata-5-and-suricata-6-rule-categories/94

## 実行
```
$ python main.py
```
注: eve.jsonが指定した場所に存在しないとエラーにより終了します。

## 免責事項
- (誰も使わないと思うけど) 本アプリ利用・使用により発生したあらゆる損失の責任を負いません。自己責任で利用・使用をお願いします。