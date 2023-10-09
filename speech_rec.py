import csv
import warnings
import pyttsx3
import threading
import os
from whisper_mic.whisper_mic import WhisperMic

class SpeechRecognition:
    def __init__(self):
        warnings.filterwarnings("ignore")
        self.mic = WhisperMic(english=True)
        self.engine = pyttsx3.init()
        self.listening_done = threading.Event()

        self.voice = self.engine.getProperty('voices')[1]
        self.engine.setProperty('voice', self.voice.id)

        self.wake_up_command = "Hey Robot"
        self.list_of_commands = []

        with open('commands.csv', 'r') as file:
            csv_reader = csv.reader(file)
            self.list_of_commands.extend(row for row in csv_reader)        

    def doSomething(self):
        command_found = -1
        while command_found == -1:
            print("")
            input = self.inputListen()
            self.listening_done.wait()
            command_found = next((index for index, row in enumerate(self.list_of_commands) if str(row[0]) in input.lower()), -1)
            if command_found > -1: 
                self.say(self.list_of_commands[command_found][1])
                self.say("Anything else? Simply say Yes or No")
                input = ""
                while "yes" not in input and "no" not in input.lower():
                    input = self.inputListen()
                    self.listening_done.wait()
                if "yes" in input:
                    self.say("How can I assist you?")
                    self.doSomething()
                else:
                    self.say("Alright, bye!")
                    exit(0)
            self.say("I'm sorry I didn't understand that.")

    def filter_input(self, input):
        char_list = ",.!?:;"
        filtered_input = ''.join(filter(lambda char: char not in char_list, input))
        return filtered_input.lower()

    def inputListen(self):
        self.listening_done.clear()
        input = self.mic.listen()
        print(type(input))
        print(input)
        self.listening_done.set()
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

    sr.say(f'\nHello, welcome to Sign Language Bot (SLB)!\nTo get started simply say {sr.wake_up_command}.', add_name=False)

    while not req_met:
        input = sr.inputListen()
        sr.listening_done.wait()
        if sr.wake_up_command.lower() in input:
            req_met = True
            sr.say("Hello, how may I assist you?")
            sr.say("List of commands:", new_line="")
            [sr.say(f'{i + 1}: {row[0]}', add_name=False, new_line="") for i, row in enumerate(sr.list_of_commands)]
            sr.doSomething()

if __name__ == '__main__':
    main()