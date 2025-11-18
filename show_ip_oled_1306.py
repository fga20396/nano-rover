import time
import socket
from PIL import Image, ImageDraw, ImageFont
import board
import busio
import adafruit_ssd1306


def get_ip():
    """Returns the current IP address of the Raspberry Pi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "No IP"
    return ip


def main():
    # I2C setup
    i2c = busio.I2C(board.SCL, board.SDA)

    # 128x32 OLED
    display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

    # Clear display
    display.fill(0)
    display.show()

    # Create image buffer
    width = display.width
    height = display.height
    image = Image.new("1", (width, height))
    draw = ImageDraw.Draw(image)

    # Use default font
    font = ImageFont.load_default()

    while True:
        ip = get_ip()

        # Clear image
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Draw IP text
        draw.text((0, 0), "IP Address:", font=font, fill=255)
        draw.text((0, 15), ip, font=font, fill=255)

        # Show it
        display.image(image)
        display.show()

        time.sleep(5)  # update every 5 seconds


if __name__ == "__main__":
    main()
