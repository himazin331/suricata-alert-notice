import smbus2
import math
import time

I2C_ADDR = 0x27
I2C_PORT = 1
LCD_WIDTH = 16
LCD_CHR = 1
LCD_CMD = 0
LCD_LINE_LIST = [0x80, 0xC0]

LCD_CLEAR = 0x01        # ディスプレイクリア
LCD_BACKLIGHT_ON = 0x08 # バックライト-オン
LCD_BACKLIGHT_OFF = 0x00 # バックライト-オフ
ENABLE = 0b00000100     # 有効

bus = smbus2.SMBus(I2C_PORT)

def lcd_init():
    # レジスタ初期化（4ビットモード）
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    # レジスタ設定（4ビットモード、2行表示、5x8ドットフォント）
    lcd_byte(0x28, LCD_CMD)
    # ディスプレイ表示オン、カーソル表示オン、カーソル点滅オン
    lcd_byte(0x0C, LCD_CMD)
    # ディスプレイクリア
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.1)

def lcd_byte(bits, mode):
    # 4ビットモードでのデータ送信
    # 上位4ビット
    high_bits = mode | (bits & 0xF0) | LCD_BACKLIGHT_ON
    bus.write_byte(I2C_ADDR, high_bits)
    lcd_toggle_enable(high_bits)

    # 下位4ビット
    low_bits = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT_ON
    bus.write_byte(I2C_ADDR, low_bits)
    lcd_toggle_enable(low_bits)

def lcd_toggle_enable(bits):
    # Enableをトグルする
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(0.0005)

def lcd_string(msg: str):
    msg_line: list[str] = [msg[i:i+LCD_WIDTH] for i in range(0, len(msg), LCD_WIDTH)]
    msg_line[-1] = msg_line[-1].ljust(LCD_WIDTH, " ")

    for i in range(math.ceil(len(msg_line) / 2)):
        lcd_clear()
        lcd_byte(LCD_LINE_LIST[0], LCD_CMD)
        for j in range(LCD_WIDTH):
            lcd_byte(ord(msg_line[i * 2][j]), LCD_CHR)

        if len(msg_line) > i * 2 + 1:
            lcd_byte(LCD_LINE_LIST[1], LCD_CMD)
            for j in range(LCD_WIDTH):
                lcd_byte(ord(msg_line[i * 2 + 1][j]), LCD_CHR)

        time.sleep(2)

def lcd_clear():
    lcd_byte(LCD_CLEAR, LCD_CMD)