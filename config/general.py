from enum import Enum

class NoticeType(Enum):
    Nothing = 0
    Email = 1
    LineNotify = 2
    Both = 3

EVE_JSONL_PATH: str = "/usr/local/var/log/suricata/eve.json"
NOTICE_TYPE = NoticeType.Nothing