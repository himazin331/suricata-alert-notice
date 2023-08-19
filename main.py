import json
import os
import time
from datetime import datetime, timezone, timedelta

from send_mail import EMailSend
from send_line import LineNotifySend

from config.general import *

class Notice():
    def __init__(self):
        self.email_notice: EMailSend = EMailSend()
        self.line_notify: LineNotifySend = LineNotifySend()

        self.notice_target_eve: list[dict] = []

    # 通知
    def notice(self, notice_target_eve: list[dict]):
        self.notice_target_eve = notice_target_eve

        message: str = "不審な通信を検知しました！\n"
        message += f"件数: {len(self.notice_target_eve)} 件\n"
        if not (NOTICE_TYPE is NoticeType.Nothing):
            if NOTICE_TYPE is NoticeType.LineNotify or NOTICE_TYPE is NoticeType.Both: # LINE通知
                self.send_line(message)
            if NOTICE_TYPE is NoticeType.Email or NOTICE_TYPE is NoticeType.Both: # Email送信
                self.send_email(message)

    # メッセージ作成
    def create_message(self, eve: dict) -> str:
        try:
            message: str = "\n** 情報 **\n"
            message += f"timestamp: {eve['timestamp'].strftime('%Y/%m/%d %H:%M:%S')}\n"
            message += f"src: {eve['src_ip']}:{eve['src_port']} -> dest: {eve['dest_ip']}:{eve['dest_port']}\n"
            message += f"protocol: {eve['proto']}\n"
            message += f"\n{eve['alert']['signature']}\n"
            message += f"signature ID: {eve['alert']['signature_id']}\n"
            if "http" in eve:
                eve_http: dict = eve["http"]
                if eve_http != {}:
                    message += f"\n** HTTP情報 **\n"
                    message += f"hostname: {eve_http['hostname']}\n"
                    message += f"url: {eve_http['url']}\n"
                    message += f"{eve_http['http_content_type']} {eve_http['http_method']} {eve_http['status']}\n"
        except KeyError:
            pass
        return message

    # Email送信
    def send_email(self, message: str):
        for eve in self.notice_target_eve:
            message += self.create_message(eve)
            message += "\n===========================================================\n"
        self.email_notice.sendEmail(message)
    
    # LINE送信
    def send_line(self, message: str):
        self.line_notify.sendLineMessage(message)
        for eve in self.notice_target_eve:
            message = self.create_message(eve)
            self.line_notify.sendLineMessage(message)

def is_priority_sig(sig: str) -> bool:
    for category in FILTER_SIG_CATEGORY:
        if category in sig:
            return True
    return False

def main():
    notice: Notice = Notice()

    prev_timestamp: datetime = datetime.now(timezone(timedelta(hours=9)))
    last_modified: float = 0.0
    current_modified: float = os.path.getmtime(EVE_JSONL_PATH)
    lower_sig_id, upper_sig_id = SIGNATURE_ID_RANGE

    while True:
        notice_target_eve: list[dict] = []

        if current_modified != last_modified:
            # eve.json取得
            with open(EVE_JSONL_PATH, "r") as eve_jsonl:
                for jsonl in eve_jsonl:
                    eve: dict = json.loads(jsonl)

                    cur_timestamp: datetime = datetime.strptime(eve["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z")
                    eve["timestamp"] = cur_timestamp
                    if cur_timestamp > prev_timestamp and "alert" in eve:
                        sig_id: int = eve["alert"]["signature_id"] 
                        if lower_sig_id <= sig_id and sig_id <= upper_sig_id:
                            if is_priority_sig(eve["alert"]["signature"] ):
                                notice_target_eve.append(eve)
                        prev_timestamp = cur_timestamp
            # 通知
            if len(notice_target_eve) > 0:
                notice.notice(notice_target_eve)
            last_modified = current_modified
        current_modified = os.path.getmtime(EVE_JSONL_PATH)
        time.sleep(1)

if __name__ == '__main__':
    main()
