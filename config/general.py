from enum import Enum

class NoticeType(Enum):
    Nothing = 0
    Email = 1
    LineNotify = 2
    Both = 3

EVE_JSONL_PATH: str = "/usr/local/var/log/suricata/eve.json"
NOTICE_TYPE = NoticeType.Email
# SIGNATURE_ID_RANGE内のシグネチャのみ通知
SIGNATURE_ID_RANGE: tuple[int, int] = (2000000, 2099999) # ET Open Rulesets
FILTER_SIG_CATEGORY: list[str] = [
        "Attack Response", "DNS", "DOS", "Exploit", "FTP", 
        "ICMP", "IMAP", "Malware", "NETBIOS", "Phishing", 
        "POP3", "RPC", "Shellcode", "SMTP", "SNMP", "SQL", 
        "TELNET", "TFTP", "Web Client", "Web Server", "Web Specific Apps", "WORM"
    ] # "ET xxx"のxxx。