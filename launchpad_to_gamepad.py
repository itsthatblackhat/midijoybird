import sys
import mido
import vgamepad as vg
import time
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt
from pynput.keyboard import Controller as KeyboardController

# Path to the configuration file
config_path = 'config.json'

# Load MIDI to input mappings
def load_mappings():
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
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
def setup_mode(port, window):
    global midi_to_input_map
    QMessageBox.information(window, "Setup Mode", "Entered setup mapping mode. Press a button on the Launchpad to map it to a gamepad button or keyboard key.")
    for message in port:
        if message.type == 'note_on' and message.velocity > 0:
            midi_note = message.note
            input_type, ok = QInputDialog.getText(window, "Input Type", f"Do you want to map MIDI note {midi_note} to a gamepad button or a keyboard key? (Enter 'gamepad' or 'keyboard', or 'exit' to return to main menu): ")
            if not ok or input_type.strip().lower() == 'exit':
                return
            elif input_type.strip().lower() == 'gamepad':
                while True:
                    button, ok = QInputDialog.getInt(window, "Gamepad Button", f"Enter the gamepad button number to map to MIDI note {midi_note} (an integer from 1 to 15 for buttons, 16 to 23 for axes): ")
                    if ok:
                        midi_to_input_map[midi_note] = {"type": "gamepad", "value": button}
                        save_mappings(midi_to_input_map)
                        QMessageBox.information(window, "Mapping Saved", f"Mapped MIDI note {midi_note} to gamepad button {button}.")
                        break
                    else:
                        QMessageBox.warning(window, "Invalid Input", "Invalid input. Please enter a valid integer.")
            elif input_type.strip().lower() == 'keyboard':
                key, ok = QInputDialog.getText(window, "Keyboard Key", f"Enter the keyboard key to map to MIDI note {midi_note} (e.g., 'a', 'space', 'enter'): ")
                if ok:
                    midi_to_input_map[midi_note] = {"type": "keyboard", "value": key.strip()}
                    save_mappings(midi_to_input_map)
                    QMessageBox.information(window, "Mapping Saved", f"Mapped MIDI note {midi_note} to keyboard key {key.strip()}.")
                else:
                    QMessageBox.warning(window, "Invalid Input", "Invalid input. Please enter a valid key.")
            else:
                QMessageBox.warning(window, "Invalid Input", "Invalid input. Please enter 'gamepad', 'keyboard', or 'exit'.")

# Main function to map MIDI input to gamepad buttons or keyboard keys
def listen_for_midi(port, window):
    global midi_to_input_map
    QMessageBox.information(window, "Listening", "Listening for MIDI inputs...")
    for message in port:
        if message.type == 'note_on' and message.velocity > 0:
            midi_note = message.note
            input_map = midi_to_input_map.get(midi_note)
            if input_map:
                input_type = input_map["type"]
                value = input_map["value"]
                if input_type == "gamepad":
                    press_gamepad_button(value)
                elif input_type == "keyboard":
                    press_keyboard_key(value)
            else:
                QMessageBox.information(window, "No Mapping Found", f"No input mapping found for MIDI note: {midi_note}")

def select_midi_port(window):
    ports = mido.get_input_names()
    if not ports:
        QMessageBox.critical(window, "Error", "No MIDI input ports found.")
        return None

    items = [f"{i}: {port}" for i, port in enumerate(ports)]
    item, ok = QInputDialog.getItem(window, "Select MIDI Input Port", "Available MIDI input ports:", items, 0, False)
    if ok:
        return ports[int(item.split(":")[0])]
    return None

class MidiJoyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.listen_button = QPushButton('Listen for MIDI Inputs', self)
        self.listen_button.clicked.connect(self.on_listen)
        layout.addWidget(self.listen_button)

        self.setup_button = QPushButton('Setup Mode', self)
        self.setup_button.clicked.connect(self.on_setup)
        layout.addWidget(self.setup_button)

        self.exit_button = QPushButton('Exit', self)
        self.exit_button.clicked.connect(self.on_exit)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)
        self.setWindowTitle('Launchpad to Gamepad/Keyboard Mapper')
        self.show()

    def on_listen(self):
        port_name = select_midi_port(self)
        if port_name:
            with mido.open_input(port_name) as port:
                listen_for_midi(port, self)

    def on_setup(self):
        port_name = select_midi_port(self)
        if port_name:
            with mido.open_input(port_name) as port:
                setup_mode(port, self)

    def on_exit(self):
        self.close()

def main():
    app = QApplication(sys.argv)
    ex = MidiJoyApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
