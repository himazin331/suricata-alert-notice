# Suricata Alert Notice App

※ 日本語版は[こちら](README_JP.md)

This is an application that sends notifications via email or LINE (or both) when Suricata generates an alert. 

## Prerequisites
- This application reads the `eve.json` output by Suricata, so make sure you configure Suricata to generate the output.

## Setup
### 1. Configure config/notice.py
Configure the email server authentication and LINE Notify token for sending messages. Note that the details of LINE Notify configuration are not provided here.
```python
# config/notice.py
SENDER_EMAIL: str = "your_email@example.com"  # Sender's email address
RECEIVER_EMAIL: str = "your_email@gmail.com"  # Recipient's email address
SMTP_SERVER: str = "smtp.gmail.com"           # SMTP server hostname (Using Gmail in this case)
SMTP_PORT: int = 587                          # SMTP server port
SMTP_USER: str = "your_email@gmail.com"       # SMTP server authentication username
SMTP_PASS: str = "**********************"     # SMTP server authentication password

LINE_NOTIFY_TOKEN: str = "***************************" # Line Notify API Access Token
```

### 2. Configure config/general.py
Configure notification settings, target signature IDs, and other settings.
```python
# config/general.py
from enum import Enum

class NoticeType(Enum):
    Nothing = 0     # No notification (for verification)
    Email = 1       # Email notification
    LineNotify = 2  # LINE notification
    Both = 3        # Email & LINE notification

EVE_JSONL_PATH: str = "/usr/local/var/log/suricata/eve.json" # Path to eve.json
NOTICE_TYPE = NoticeType.Email  # Notification settings
# Notify only for signatures within SIGNATURE_ID_RANGE
SIGNATURE_ID_RANGE: tuple[int, int] = (2000000, 2099999) # ET Open Rulesets
# Notify only signatures that contain FILTER_SIG_CATEGORY in the signature message in addition to the signature ID range
FILTER_SIG_CATEGORY: list[str] = [
        "Attack Response", "DNS", "DOS", "Exploit", "FTP", 
        "ICMP", "IMAP", "Malware", "NETBIOS", "Phishing", 
        "POP3", "RPC", "Shellcode", "SMTP", "SNMP", "SQL", 
        "TELNET", "TFTP", "Web Client", "Web Server", "Web Specific Apps", "WORM"
    ] # Categories like "ET xxx" (e.g., "ET Exploit ~")
```
This time, I set it so that only alerts that fall under the Emerging threats open ruleset signature ID `2000000 ~ 2099999` and that contain the FILTER_SIG_CATEGORY string are notified.

#### References
- Emerging Threats Open Ruleset Signature ID Allocation Ranges: \
https://community.emergingthreats.net/t/signature-id-allocation-ranges/491
- Emerging Threats Open Ruleset Rule Categories: \
https://community.emergingthreats.net/t/current-suricata-5-and-suricata-6-rule-categories/94

## Execution
```
$ python main.py
```
Note: The application will exit with an error if `eve.json` is not found at the specified location.

## Disclaimer
- (Although I don't think anyone will use this) We are not responsible for any losses incurred through the use of this application. Please use it at your own risk.