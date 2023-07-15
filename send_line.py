import requests

from config.notice import LINE_NOTIFY_TOKEN

# Notify送信
class LineNotifySend():
    # Line Notify API セットアップ
    def __init__(self):
        self.url: str = "https://notify-api.line.me/api/notify"
        self.line_headers: dict[str, str] = {'Authorization': 'Bearer ' + LINE_NOTIFY_TOKEN}

    # メッセージ送信
    def sendLineMessage(self, message: str):
        try:
            payload: dict[str, str] = {'message': message}
            # Line送信
            requests.post(self.url, headers=self.line_headers, params=payload)
        except requests.exceptions.RequestException as e:
            print(e)
