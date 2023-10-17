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
        warnings.filterwarnings("ignore")
        self.hand_tracker = HandTracker()
        self.serial_connection = SerialConnection()
        self.mic = WhisperMic(english=True)
        self.engine = pyttsx3.init()

        self.voice = self.engine.getProperty('voices')[1]
        self.engine.setProperty('voice', self.voice.id)

        self.wake_up_command = "Hey Robot"
        self.commands_list = []
        self.servos_ratio_list = []
        self.close_words = []

        self.serial_connection.read_until('Setup complete')

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

    def doSomething(self):
        command_found = -1
        while command_found == -1:
            input = self.inputListen()
            # input = "Do you know this sign" # Used for testing
            self.listening_done.wait()
            command_found = next((index for index, row in enumerate(self.commands_list) 
                                  if str(row[1].lower()) in input.lower()), -1)
            if command_found > -1: 
                command = self.commands_list[command_found][0]

                if command == 'replicate':
                    self.replicateHand(self.commands_list[command_found])
                elif command == 'show':
                    self.showCharacter(self.commands_list[command_found], input)
                elif command == 'knowledge':
                    self.knowledgeCheck(self.commands_list[command_found])

                # self.say(self.commands_list[command_found][1])
                self.say("Anything else? Simply say Yes or No")
                input = "yes"
                while "yes" not in input and "no" not in input.lower():
                    input = self.inputListen()
                if "yes" in input:
                    self.say("How can I assist you?")
                    self.doSomething()
                else:
                    self.say("Alright, bye!")
                    exit(0)
            self.say("I'm sorry I didn't understand that.")
    def getCharIn(self, input):
        char_index = []
        while(len(char_index) == 0):
            char_index = [i for i, row in enumerate(self.close_words) if input in row]
            if len(char_index) == 0:
                self.say("I'm sorry I didn't understand that.")
                input = self.inputListen(do_print=False).split()[0]
                # input = 'weight this test'.split()[0] # Used for testing

        char_in = self.close_words[char_index[0]][0]
        print("You -", char_in.upper())

    def storeFingerValues(self, char_in, fingers_pos):
        for row in self.servos_ratio_list:
            if row[0] == char_in.upper():
                row[1:] = fingers_pos

        with open('Characters_servos_ratios.csv', 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(self.servos_ratio_list)

    def replicateHand(self, command_data):
        self.say(command_data[2])
        fingers_pos = self.getCameraCapture()
        fingers_pos = [pos*100 for pos in fingers_pos]
        self.serial_connection.send_hand_pos(fingers_pos)
        # print(fingers_pos)

    def showCharacter(self, command_data, input):
        self.say("What character would you want me to show?")
        input = self.inputListen(do_print=False).split()[0]
        # input = 'F' # Used for testing

        char_in = self.getCharIn(input)
        stored_char_list = {row[0]: row[1:] for (i, row) in enumerate(self.servos_ratio_list) if row[1] != '-'}
        if char_in in stored_char_list:
            output = command_data[2].replace('_', char_in.upper())
            self.say(output)
            print(stored_char_list[char_in])

        else:
            output = command_data[3].replace('_', char_in.upper())
            self.say(output)
        
    def knowledgeCheck(self, command_data):
        fingers_pos = self.getCameraCapture()
        print("Finger pos: ", [float(pos) for pos in fingers_pos])
        filtered_servos_list = {row[0]: [float(num) for num in row[1:]] for row in self.servos_ratio_list if row[1] != '-'}
        closest_entry = min(filtered_servos_list.items(), key=lambda x: self.calculate_total_difference(fingers_pos, x[1]))
        total_difference = self.calculate_total_difference(fingers_pos, closest_entry[1])
        stored_char_list = {row[0]: row[1:] for (i, row) in enumerate(self.servos_ratio_list) if row[1] != '-'}

        print("Closest Entry:", closest_entry)
        print("Min difference:", total_difference)

        if total_difference < 1:
            output = command_data[2].replace('_', closest_entry[0].upper())
            self.say(output)
        else:
            self.say(command_data[3])
            input = "yes"
            while "yes" not in input and "no" not in input.lower():
                input = self.inputListen()
            if "yes" in input:
                self.say("What character is this?")
                char_in = self.getCharIn(input)
                # char_in = "Z" # Used for testing
                if char_in in stored_char_list:
                    self.say(f"Character {char_in.upper()} already exists, do you want to override it?")
                    input = ""
                    while "yes" not in input and "no" not in input.lower():
                        input = self.inputListen()
                    if "no" in input:
                        return

                self.storeFingerValues(char_in, fingers_pos)
                output = command_data[4].replace('_', char_in[0].upper())
                self.say(output)

        return

    def calculate_total_difference(self, fingers_pos, entry):
        return sum(abs(float(a) - float(b)) for a, b in zip(fingers_pos, entry))


    def filter_input(self, input):
        char_list = ",.!?:;"
        filtered_input = ''.join(filter(lambda char: char not in char_list, input))
        return filtered_input.lower()

    def getCameraCapture(self):
        self.say('Aim your hand towards the camera')
        lm_list = []
        while True:
            lm_list = self.hand_tracker.snapshot_capture()
            if len(lm_list) > 0:
                break
            else:
                self.say('Please show your right hand.')

        return [round(finger[2] * 10) / 10  for finger in lm_list[0]]

    def inputListen(self, do_print=True):
        input = self.mic.listen()
        if do_print: 
            print("You -" + input)
        filtered_input = self.filter_input(input)
        return filtered_input

    def say(self, text, add_name=True, new_line = '\n'):
        name = "Bot - " if add_name else ""
        print(name + text + new_line)
        self.engine.say(text)
        self.engine.runAndWait()


def main():
    sr = SpeechRecognition()
    os.system('cls')
    req_met = False
    
    # sr.doSomething() # Skips the start, used for testing

    sr.say(f'\nHello, welcome to Sign Language Bot (SLB)!\nTo get started simply say {sr.wake_up_command}.', add_name=False)

    while not req_met:
        input = sr.inputListen()
        if sr.wake_up_command.lower() in input:
            req_met = True
            sr.say("Hello, how may I assist you?")
            sr.say("List of commands:", new_line="")
            [sr.say(f'{i + 1}: {row[1]}', add_name=False, new_line="") for i, row in enumerate(sr.commands_list)]
            sr.doSomething()

if __name__ == '__main__':
    main()