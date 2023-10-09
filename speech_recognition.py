import csv
import warnings
import pyttsx3
import threading
import os

from whisper_mic.whisper_mic import WhisperMic

warnings.filterwarnings("ignore")

mic = WhisperMic(english=True)
engine = pyttsx3.init()
listening_done = threading.Event()

voice = engine.getProperty('voices')[1]
engine.setProperty('voice', voice.id)

wake_up_command = "Hey Robot"
list_of_commands = []

with open('speech_commands.csv', 'r') as file:
    csv_reader = csv.reader(file)
    list_of_commands.extend(row for row in csv_reader)


def main():
    os.system('cls')
    req_met = False
    say(f'\nHello, welcome to Sign Language Bot (SLB)!\nTo get started simply say {wake_up_command}.', add_name=False)

    while not req_met:
        input = inputListen()
        listening_done.wait()
        if wake_up_command.lower() in input:
            req_met = True
            say("Hello, how may I assist you?")
            say("List of commands:", new_line="")
            [say(f'{i + 1}: {row[0]}', add_name=False, new_line="") for i, row in enumerate(list_of_commands)]
            doSomething()

def doSomething():
    command_found = -1
    while command_found == -1:
        print("")
        input = inputListen()
        listening_done.wait()
        command_found = next((index for index, row in enumerate(list_of_commands) if str(row[0]) in input.lower()), -1)
        if command_found > -1: 
            say(list_of_commands[command_found][1])
            say("Anything else? Simply say Yes or No")
            input = ""
            while "yes" not in input and "no" not in input.lower():
                input = inputListen()
                listening_done.wait()
            if "yes" in input:
                say("How can I assist you?")
                doSomething()
            else:
                say("Alright, bye!")
                exit(0)
        say("I'm sorry I didn't understand that.")

def filter_input(input):
    char_list = ",.!?:;"
    filtered_input = ''.join(filter(lambda char: char not in char_list, input))
    return filtered_input.lower()

def inputListen():
    listening_done.clear()
    input = mic.listen()
    listening_done.set()
    print("You -" + input)
    filtered_input = filter_input(input)
    return filtered_input

def say(text, add_name=True, new_line = '\n'):
    name = "Bot - " if add_name else ""
    print(name + text + new_line)
    engine.say(text)
    engine.runAndWait()

if __name__ == '__main__':
    main()