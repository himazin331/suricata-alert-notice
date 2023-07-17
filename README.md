# Suricata Alert Notice App

Suricataがアラートを発報したときに、メールまたはLINE(あるいは両方)で通知するアプリです。\
おまけでLCD表示とインジケータLED表示、ブザー発報を実装してます。

## 前提
- 本アプリはSuricataが出力する`eve.json`を読み取りますので、出力されるようにSuricataの設定をしてください。
- LCD表示はI2Cで行っています。それに伴い、`smbus2`をpipインストールしてください。
  ```
  pip install smbus2
  ```
- smbus2を除いて、標準でインストールされてるPythonパッケージを使ってますが、インストールされていない場合は随時インストールしてください。

## ハードウェア
- Raspberry Pi 4 Model B x1
- 1602 LCD - I2C I/Oエキスパンダ(PCF8574)付 x1
- タクタイルスイッチ S1 x1
- 発光ダイオード 緑LED1 x1, 黄LED2 x1, 赤LED3 x1
- 圧電ブザー(自励式) J1 x1
- 100Ω抵抗器 R1 x1
- 10Ω抵抗器 R2 x1
- 0.33μFコンデンサ C1 x1
- 適当な基板 or ブレッドボード x1
- 電線 or ジャンパ線

### 回路図
LCDとPCF8574の配線は参考程度に....\
![suricata_alert_notice回路図](images/suricata_alert_notice.svg)

### 実体配線図
![suricata_alert_notice実体配線図](images/suricata_alert_notice_bb.png)

## 準備
### 1. 各GPIOピンの指定
- 圧電ブザーのGPIOピン指定
  ```python
  # bz_control.py
  BZ_PIN: int = 18
  ```

- 発光ダイオードのGPIOピン指定
  ```python
  # led_control.py
  GREEN_LED_PIN: int = 17
  YELLOW_LED_PIN: int = 27
  RED_LED_PIN: int = 22
  ```

- 停止スイッチのGPIOピン指定
  ```python
  # main.py
  STOP_SW_PIN: int = 23
  ```

- I2Cアドレスの指定
  1. `sudo raspi-config`にてI2Cを有効にしてください。(割愛)
  2. I2Cバス周りのツールセット`i2c-tools`をapt installします。
      ```
      $ sudo apt install i2c-tools
      ```
  3. 以下のコマンドを実行し、利用可能なI2Cバスを確認します。バス番号1のI2Cバスを利用します。("コレ"とあるやつ)
      ```
      $ i2cdetect -l
      i2c-20  i2c             fef04500.i2c                            I2C adapter
      i2c-1   i2c             bcm2835 (i2c@7e804000)                  I2C adapter <-コレ
      i2c-21  i2c             fef09500.i2c                            I2C adapter
      ```
  4. 以下のコマンドを実行し、接続されたデバイスのアドレスを確認します。今回は`0x27`です。
      ```
      $ i2cdetect -y 1
          0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
      00:                         -- -- -- -- -- -- -- -- 
      10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
      20: -- -- -- -- -- -- -- 27 -- -- -- -- -- -- -- -- 
      30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
      40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
      50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
      60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
      70: -- -- -- -- -- -- -- --                         
      ```
  5. 4で確認したアドレスを`i2c_control.py`の`I2C_ADDR`に指定してください。
      ```python
      # i2c_control.py
      I2C_ADDR = 0x27
      ```
  6. (options) 使用するLCDによっては他の定義値も変更する必要があります。\
  データシート等参照のうえ、適切な値に変更してください。

### 2. config/notice.pyの設定
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

### 3. config/general.pyの設定
通知設定や通知対象とするシグネチャIDの指定などの設定を行います。
```python
# config/general.py
from enum import Enum

class NoticeType(Enum):
    Nothing = 0     # 通知しない (LCD表示のみ)
    Email = 1       # メール通知
    LineNotify = 2  # LINE通知
    Both = 3        # メール&LINE通知

EVE_JSONL_PATH: str = "/usr/local/var/log/suricata/eve.json" # eve.json配置場所
NOTICE_TYPE = NoticeType.Email  # 通知設定
# SIGNATURE_ID_RANGE内のシグネチャのみ通知
SIGNATURE_ID_RANGE: tuple[int, int] = (2000000, 2099999) # ET Open Rulesets
# シグネチャメッセージにPRIORITY_SIG_CATEGORYが含まれる場合はブザー発報
PRIORITY_SIG_CATEGORY: list[str] = [
        "Attack Response", "DNS", "DOS", "Exploit", "FTP", 
        "ICMP", "IMAP", "Malware", "NETBIOS", "Phishing", 
        "POP3", "RPC", "Shellcode", "SMTP", "SNMP", "SQL", 
        "TELNET", "TFTP", "Web Client", "Web Server", "Web Specific Apps", "WORM"
    ] # "ET xxx"のxxx。(例: "ET Exploit ~")
```
今回私は、Emerging threats open rulesetのシグネチャID`2000000 ~ 2099999`に該当するalertのみを通知するように設定。\
また、上記の`PRIORITY_SIG_CATEGORY`にある文字列を含む`ET xxx ~`から始まるシグネチャを高レベルアラートとして処理する(=ブザー発報と赤色LED点灯)。

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

### 機能
- Suricataアラートを検知したら、黄色LEDが点灯し、LCDにシグネチャメッセージが表示され、メールまたはLINEあるいはその両方にて通知されます。
- 高レベルアラート(`PRIORITY_SIG_CATEGORY`を含むルール)を検知した場合は、黄色LEDに加えて赤色LEDも点灯され、ブザーを鳴らします。
- LCD表示中に停止スイッチを長押しすると、途中でLCD表示とブザー発報を止めることができます。
- 終了したいときはCtrl+Cで終了できます。\
  (終了時、GPIO周りでRuntimeError発生するけど動作に支障はないからへーきへーき←おい)


## 免責事項
- (誰も使わないと思うけど) 本アプリ利用・使用により発生したあらゆる損失の責任を負いません。自己責任で利用・使用をお願いします。