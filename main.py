import json
import os
import threading
import time
from datetime import datetime, timezone, timedelta
import RPi.GPIO as GPIO

from i2c_control import lcd_init, lcd_string, lcd_clear
from bz_control import BzControl
from led_control import LedType, LedControl
from send_mail import EMailSend
from send_line import LineNotifySend

from config.general import *

STOP_SW_PIN: int = 23

led_control: LedControl = LedControl()
bz_control: BzControl = BzControl()
stop_event: threading.Event = threading.Event()


class Notice():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(STOP_SW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.email_notice: EMailSend = EMailSend()
        self.line_notify: LineNotifySend = LineNotifySend()

        self.notice_target_eve: list[dict] = []

    # 通知
    def notice(self, notice_target_eve: list[dict]):
        self.notice_target_eve = notice_target_eve
        hw_thread = threading.Thread(target=self.hardware_control)

        led_control.led_on(LedType.Red)
        hw_thread.start()

        message: str = "不審な通信を検知しました！\n"
        message += f"件数: {len(self.notice_target_eve)} 件\n"
        if not (NOTICE_TYPE is NoticeType.Nothing):
            if NOTICE_TYPE is NoticeType.Email or NOTICE_TYPE is NoticeType.Both: # Email送信
                self.send_email(message)
            if NOTICE_TYPE is NoticeType.LineNotify or NOTICE_TYPE is NoticeType.Both: # LINE通知
                self.send_line(message)

        hw_thread.join()
        led_control.led_off(LedType.Red)

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

    # LCD表示 & ブザー発報
    def hardware_control(self):
        for _ in range(5):
            stop_state = GPIO.input(STOP_SW_PIN)
            if stop_state == GPIO.LOW or stop_event.is_set(): # 停止
                break

            bz_control.bz_beep()
            lcd_string(self.notice_target_eve[-1]["alert"]["signature"])
            bz_control.bz_stop()
            lcd_string("Detected !!")
                

def main():
    notice: Notice = Notice()
    lcd_init()

    prev_timestamp: datetime = datetime.now(timezone(timedelta(hours=9)))
    last_modified: float = 0.0
    current_modified: float = os.path.getmtime(EVE_JSONL_PATH)

    led_control.led_on(LedType.Green)
    try:
        while True:
            lcd_clear()
            notice_target_eve: list[dict] = []

            if current_modified != last_modified:
                # eve.json取得
                with open(EVE_JSONL_PATH, "r") as eve_jsonl:
                    for jsonl in eve_jsonl:
                        eve: dict = json.loads(jsonl)

                        cur_timestamp: datetime = datetime.strptime(eve["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z")
                        eve["timestamp"] = cur_timestamp
                        if cur_timestamp > prev_timestamp and "alert" in eve:
                            notice_target_eve.append(eve)
                            prev_timestamp = cur_timestamp
                # 通知
                if len(notice_target_eve) > 0:
                    notice.notice(notice_target_eve)
                last_modified = current_modified
            current_modified = os.path.getmtime(EVE_JSONL_PATH)
            time.sleep(1)
    except KeyboardInterrupt:
        # GPIO開放処理
        stop_event.set() # スレッド処理停止
        lcd_clear()
        GPIO.cleanup()
    

if __name__ == '__main__':
    main()
