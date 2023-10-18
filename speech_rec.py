import csv
import warnings
import pyttsx3
import os
import time

from whisper_mic.whisper_mic import WhisperMic
from hand_tracker import HandTracker
from serial_connection import SerialConnection


class SpeechRecognition:
    def __init__(self):
        self.serial_flag = False
        self.use_mic = True

        warnings.filterwarnings("ignore")
        self.hand_tracker = HandTracker()
        if self.serial_flag:
            self.serial_connection = SerialConnection()
            self.serial_connection.read_until('Setup complete')
        self.mic = WhisperMic(english=True)
        self.engine = pyttsx3.init()

        # self.voice = self.engine.getProperty('voices')[12] # Linux (Alberto)
        self.voice = self.engine.getProperty('voices')[1] # Windows (Karim)
        self.engine.setProperty('voice', self.voice.id)

        self.wake_up_command = "Hey Robot"
        self.commands_list = []
        self.servos_ratio_list = []
        self.close_words = []

        with open('speech_commands.csv', 'r') as file:
            csv_reader = csv.reader(file)
            self.commands_list.extend(row for row in csv_reader)       

        with open('Characters_servos_ratios.csv', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            self.servos_ratio_list.extend(row for row in csv_reader) 

        with open('close_words.csv', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            self.close_words.extend(row for row in csv_reader)        

    def do_something(self):
        command_found = -1
        while command_found == -1:
            input_text = self.input_listen()

            command_found = next((index for index, row in enumerate(self.commands_list)
                                  if str(row[1].lower()) in input_text.lower()), -1)
            if command_found > -1: 
                command = self.commands_list[command_found][0]

                if command == 'replicate':
                    self.replicate_hand(self.commands_list[command_found])
                elif command == 'show':
                    self.show_character(self.commands_list[command_found])
                elif command == 'knowledge':
                    self.knowledge_check(self.commands_list[command_found])
                elif command == 'words':
                    self.spell_word(self.commands_list[command_found])

                self.say("Anything else? Simply say Yes or No")
                input_text = ""
                while "yes" not in input_text and "no" not in input_text.lower():
                    input_text = self.input_listen()
                if "yes" in input_text:
                    self.say("How can I assist you?")
                    print("List of commands:")
                    [print(f'{i + 1}: {row[1]}') for i, row in
                     enumerate(self.commands_list)]
                    print("")
                    self.do_something()
                else:
                    self.say("Alright, bye!")
                    self.exit_program()
            self.say("I'm sorry I didn't understand that.")

    def get_char_in(self):
        char_index = []
        input_char = self.input_listen(do_print=False).split()[0]
        while len(char_index) == 0:
            char_index = [i for i, row in enumerate(self.close_words)
                          if input_char.lower() in row or input_char.upper() in row]
            time.sleep(0.1)
            print("input_char:", input_char)
            print("char_index:", char_index)
            if len(char_index) == 0:
                self.say("I'm sorry I didn't understand that.")
                input_char = self.input_listen(do_print=False).split()[0]
                print("You -", input_char)

        char_in = self.close_words[char_index[0]][0]
        print("You -", char_in.upper())
        return char_in

    def store_finger_values(self, char_in, fingers_pos):
        for row in self.servos_ratio_list:
            if row[0] == char_in.upper():
                row[1:] = fingers_pos

        with open('Characters_servos_ratios.csv', 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(self.servos_ratio_list)

    def replicate_hand(self, command_data):
        self.say(command_data[2])
        fingers_pos = self.get_camera_capture()
        fingers_pos_percent = [int(float(pos)*100) for pos in fingers_pos]
        self.send_hand_positions(fingers_pos_percent)

        self.say(command_data[3])
        char_in = self.get_char_in()
        stored_char_list = {row[0]: row[1:] for (i, row) in enumerate(self.servos_ratio_list) if row[1] != '-'}

        if char_in in stored_char_list:
            self.say(f"Character {char_in.upper()} already exists, do you want to override it?")
            input_text = ""
            while "yes" not in input_text and "no" not in input_text.lower():
                input_text = self.input_listen()
            if "no" in input_text:
                return

        self.store_finger_values(char_in, fingers_pos)
        output = command_data[4].replace('_', char_in[0].upper())
        self.say(output)

    def show_character(self, command_data):
        self.say("What character would you want me to show?")

        char_in = self.get_char_in()
        stored_char_list = {row[0]: row[1:] for (i, row) in enumerate(self.servos_ratio_list) if row[1] != '-'}
        if char_in in stored_char_list:
            output = command_data[2].replace('_', char_in.upper())
            self.say(output)
            for row in self.servos_ratio_list:
                if row[0] == char_in.upper():
                    fingers_pos = row[1:]
            fingers_pos = [int(float(pos) * 100) for pos in fingers_pos]
            self.send_hand_positions(fingers_pos)

        else:
            output = command_data[3].replace('_', char_in.upper())
            self.say(output)
        
    def knowledge_check(self, command_data):
        self.say("Aim your hand towards the camera.")
        fingers_pos = self.get_camera_capture()
        filtered_servos_list = {row[0]: [float(num) for num in row[1:]]
                                for row in self.servos_ratio_list if row[1] != '-'}
        closest_entry = min(filtered_servos_list.items(),
                            key=lambda x: self.calculate_total_difference(fingers_pos, x[1]))
        total_difference = self.calculate_total_difference(fingers_pos, closest_entry[1])
        stored_char_list = {row[0]: row[1:] for (i, row) in enumerate(self.servos_ratio_list) if row[1] != '-'}

        if total_difference < 1:
            self.say("Thinking...")
            time.sleep(1)
            output = command_data[2].replace('_', closest_entry[0].upper())
            self.say(output)
        else:
            self.say(command_data[3])
            input_text = ""
            while "yes" not in input_text and "no" not in input_text.lower():
                input_text = self.input_listen()
            if "yes" in input_text:
                self.say("What character is this?")
                char_in = self.get_char_in()
                if char_in in stored_char_list:
                    self.say(f"Character {char_in.upper()} already exists, do you want to override it?")
                    input_text = ""
                    while "yes" not in input_text and "no" not in input_text.lower():
                        input_text = self.input_listen()
                    if "no" in input_text:
                        return

                self.store_finger_values(char_in, fingers_pos)
                output = command_data[4].replace('_', char_in[0].upper())
                self.say(output)

        return

    def spell_word(self, command_data):
        stored_char_list = {row[0]: row[1:] for (i, row) in enumerate(self.servos_ratio_list) if row[1] != '-'}

        self.say("Certainly, what word do you want me to spell.")
        valid_chars = False
        while not valid_chars:
            valid_chars = True
            input_word = self.input_listen().split()[0]
            for char in input_word:
                if char.upper() not in stored_char_list:
                    self.say(command_data[3].replace('_', input_word))
                    valid_chars = False
                    break
        self.say("Spelling...")

        for char in input_word:
            self.say(char.upper())
            for row in self.servos_ratio_list:
                if row[0] == char.upper():
                    fingers_pos = row[1:]
            fingers_pos = [int(float(pos) * 100) for pos in fingers_pos]
            self.send_hand_positions(fingers_pos)
            time.sleep(1)
        self.say(command_data[2].replace('_', input_word))
        return

    @staticmethod
    def calculate_total_difference(fingers_pos, entry):
        return sum(abs(float(a) - float(b)) for a, b in zip(fingers_pos, entry))

    @staticmethod
    def filter_input(input_text):
        char_list = ",.!?:;"
        filtered_input = ''.join(filter(lambda char: char not in char_list, input_text))
        return filtered_input.lower()

    def get_camera_capture(self):

        while True:
            lm_list = self.hand_tracker.snapshot_capture()
            if len(lm_list) > 0:
                break
            else:
                self.say('Please show your right hand.')

        return [round(finger[2] * 10) / 10 for finger in lm_list[0]]

    def send_hand_positions(self, fingers_pos, debug=False):
        pos_list = [0,0,0,0,0]
        if self.serial_flag:
            for i, pos in enumerate(fingers_pos):
                pos_list[i] = pos
                self.serial_connection.send_hand_pos(pos_list, debug=debug)
                time.sleep(0.1)
            
            time.sleep(3)

            for i in reversed(range(5)):
                pos_list[i] = 0
                self.serial_connection.send_hand_pos(pos_list, debug=debug)
        else:
            print(fingers_pos)


    def input_listen(self, do_print=True):
        if self.use_mic:
            input_text = self.mic.listen()
        else:
            input_text = " " + input("Input: ")
        if do_print: 
            print("You -" + input_text)
        filtered_input = self.filter_input(input_text)
        return filtered_input

    def say(self, text, add_name=True, new_line='\n'):
        name = "Bot - " if add_name else ""
        print(name + text + new_line)
        self.engine.say(text)
        self.engine.runAndWait()
    
    def exit_program(self):
        self.send_hand_positions([0, 0, 0, 0, 0])
        time.sleep(1)
        exit(0)

def test_hand(sr):
    while True:
        test_pos = [0, 0, 0, 0, 0]
        test_pos[0] = int(input("Thumb: "))
        test_pos[1] = int(input("Index: "))
        test_pos[2] = int(input("Middle: "))
        test_pos[3] = int(input("Ring: "))
        test_pos[4] = int(input("Pinky: "))
        print("")
        sr.send_hand_positions(test_pos)

def main():
    sr = SpeechRecognition()
    os.system('cls')
    req_met = False
    # test_hand(sr) # Method used for manual inputs
    
    # sr.doSomething() # Skips the start, used for testing

    sr.say(f'\nHello, welcome to Sign Bot!\nTo get started simply say {sr.wake_up_command}.',
           add_name=False)

    while not req_met:
        input_txt = sr.input_listen()
        if sr.wake_up_command.lower() in input_txt:
            req_met = True
            sr.say("Hello, how may I assist you?")
            sr.say("List of commands:", new_line="")
            [sr.say(f'{i + 1}: {row[1]}', add_name=False, new_line="") for i, row in enumerate(sr.commands_list)]
            print("")
            sr.do_something()


if __name__ == '__main__':
    main()
