import serial
import time


class SerialConnection:

    def __init__(self):
        self.arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)

    def write_read(self, x):
        self.arduino.write(bytes(x, 'utf-8'))
        time.sleep(0.05)
        data = self.read_until()
        return data

    def read_until(self, end_msg="**"):
        data = self.arduino.readline()
        all_data = data
        while not data.endswith(bytes(end_msg, 'utf-8')):
            data = self.arduino.readline()
            all_data += data

        return str(all_data, "utf-8")

    def send_hand_pos(self, fingers_pos):
        data = self.encode_hand(fingers_pos)
        self.arduino.write(bytes(data, 'utf-8'))

        print(self.read_until("**"))

    @staticmethod
    def encode_hand(fingers_pos):
        string = ""
        for i in fingers_pos:
            if i < 0:
                i = 0
            elif i > 99:
                i = 99

            string += str(i).zfill(2)
        return string

    def main(self):
        time.sleep(1)
        print(self.read_until("Setup complete"))
        while True:
            num1 = int(input("Enter a thumb: "))
            num2 = int(input("Enter a index: "))
            num3 = int(input("Enter a middle: "))
            num4 = int(input("Enter a ring: "))
            num5 = int(input("Enter a pinky: "))

            # value = self.write_read(num)
            # print(value)
            self.send_hand_pos([num1, num2, num3, num4, num5])
            print("\n")
            # print(self.read_until("**"))


if __name__ == "__main__":
    SerialConnection().main()
