import mido
import vgamepad as vg
import time
import json
import os
from pynput.keyboard import Controller as KeyboardController

# Path to the configuration file
config_path = 'config.json'

# Load MIDI to input mappings
def load_mappings():
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

# Save MIDI to input mappings
def save_mappings(mappings):
    with open(config_path, 'w') as f:
        json.dump(mappings, f, indent=2)

# Initialize gamepad and keyboard
gamepad = vg.VX360Gamepad()
keyboard = KeyboardController()

# Load mappings
midi_to_input_map = load_mappings()

# Function to press and release a gamepad button
def press_gamepad_button(button):
    gamepad.press_button(button=button)
    gamepad.update()
    time.sleep(0.05)
    gamepad.release_button(button=button)
    gamepad.update()

# Function to press and release a keyboard key
def press_keyboard_key(key):
    keyboard.press(key)
    time.sleep(0.05)
    keyboard.release(key)

# Setup mode to map MIDI notes to gamepad buttons or keyboard keys
def setup_mode(port):
    global midi_to_input_map
    print("Entered setup mapping mode. Press a button on the Launchpad to map it to a gamepad button or keyboard key.")
    while True:
        for message in port:
            if message.type == 'note_on' and message.velocity > 0:
                midi_note = message.note
                input_type = input(f"Do you want to map MIDI note {midi_note} to a gamepad button or a keyboard key? (Enter 'gamepad' or 'keyboard', or 'exit' to return to main menu): ").strip().lower()
                if input_type == 'exit':
                    return
                elif input_type == 'gamepad':
                    while True:
                        try:
                            button = int(input(f"Enter the gamepad button number to map to MIDI note {midi_note} (an integer from 1 to 15 for buttons, 16 to 23 for axes): "))
                            midi_to_input_map[midi_note] = {"type": "gamepad", "value": button}
                            save_mappings(midi_to_input_map)
                            print(f"Mapped MIDI note {midi_note} to gamepad button {button}.")
                            break
                        except ValueError:
                            print("Invalid input. Please enter a valid integer.")
                    break
                elif input_type == 'keyboard':
                    key = input(f"Enter the keyboard key to map to MIDI note {midi_note} (e.g., 'a', 'space', 'enter'): ").strip()
                    midi_to_input_map[midi_note] = {"type": "keyboard", "value": key}
                    save_mappings(midi_to_input_map)
                    print(f"Mapped MIDI note {midi_note} to keyboard key {key}.")
                    break
                else:
                    print("Invalid input. Please enter 'gamepad', 'keyboard', or 'exit'.")

# Main function to map MIDI input to gamepad buttons or keyboard keys
def listen_for_midi(port):
    global midi_to_input_map
    print("Listening for MIDI inputs...")
    for message in port:
        if message.type == 'note_on' and message.velocity > 0:
            midi_note = message.note
            input_map = midi_to_input_map.get(midi_note)
            if input_map:
                input_type = input_map["type"]
                value = input_map["value"]
                if input_type == "gamepad":
                    print(f"Pressing gamepad button: {value} for MIDI note: {midi_note}")
                    press_gamepad_button(value)
                elif input_type == "keyboard":
                    print(f"Pressing keyboard key: {value} for MIDI note: {midi_note}")
                    press_keyboard_key(value)
            else:
                print(f"No input mapping found for MIDI note: {midi_note}")

def main():
    global midi_to_input_map

    # Select MIDI input port
    print("Available MIDI input ports:")
    for i, port in enumerate(mido.get_input_names()):
        print(f"{i}: {port}")
    port_index = int(input("Select the MIDI input port index: "))
    port_name = mido.get_input_names()[port_index]

    with mido.open_input(port_name) as port:
        print(f"Opened MIDI input port: {port_name}")

        while True:
            print("\nMenu:")
            print("1. Listen for MIDI inputs")
            print("2. Setup mode (map MIDI notes to gamepad buttons or keyboard keys)")
            print("3. Exit")
            choice = input("Select an option: ")

            if choice == '1':
                listen_for_midi(port)
            elif choice == '2':
                setup_mode(port)
            elif choice == '3':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
