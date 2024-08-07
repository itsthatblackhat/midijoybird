import sys
import mido
import vgamepad as vg
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QInputDialog, QMessageBox, QCheckBox, QDialog, QDialogButtonBox
from PyQt5.QtCore import Qt
from pynput.keyboard import Controller as KeyboardController

# Path to the configuration file
config_path = 'config.json'

# Load MIDI to input mappings
def load_mappings():
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            try:
                raw_mappings = json.load(f)
                mappings = {tuple(k.split(',')): v for k, v in raw_mappings.items()}
                print(f"Loaded mappings: {mappings}")
                return mappings
            except json.JSONDecodeError:
                print("Failed to decode JSON from config file. Creating a new one.")
                return {}
    else:
        print("Config file does not exist. Creating a new one.")
        save_mappings({})
        return {}

# Save MIDI to input mappings
def save_mappings(mappings):
    with open(config_path, 'w') as f:
        raw_mappings = {','.join(map(str, k)): v for k, v in mappings.items()}
        json.dump(raw_mappings, f, indent=2)
        print(f"Saved mappings: {raw_mappings}")

# Initialize keyboard controller
keyboard = KeyboardController()

# Load mappings
midi_to_input_map = load_mappings()

# Function to press and release a gamepad button
def press_gamepad_button(gamepad, button):
    gamepad.press_button(button=button)
    gamepad.update()
    gamepad.release_button(button=button)
    gamepad.update()

# Function to press and release a keyboard key
def press_keyboard_key(key):
    keyboard.press(key)
    keyboard.release(key)

# Function to handle knob (axis) movements
def move_gamepad_axis(gamepad, axis, value, min_value, max_value):
    normalized_value = int((value - min_value) / (max_value - min_value) * 65535 - 32768)
    print(f"Setting gamepad axis {axis} to normalized value {normalized_value} (MIDI value: {value}, min: {min_value}, max: {max_value})")
    if axis == 3:
        gamepad.left_joystick(normalized_value, gamepad.report.sThumbLY)
    elif axis == 4:
        gamepad.left_joystick(gamepad.report.sThumbLX, normalized_value)
    elif axis == 5:
        gamepad.right_joystick(normalized_value, gamepad.report.sThumbRY)
    elif axis == 6:
        gamepad.right_joystick(normalized_value, gamepad.report.sThumbRX)
    gamepad.update()

# Function to handle knob (axis) movements for joystick
def move_joystick_axis(joystick, axis, value, min_value, max_value):
    normalized_value = int((value - min_value) / (max_value - min_value) * 65535 - 32768)
    print(f"Setting joystick axis {axis} to normalized value {normalized_value} (MIDI value: {value}, min: {min_value}, max: {max_value})")
    if axis == 1:
        joystick.left_joystick(normalized_value, joystick.report.sThumbLY)
    elif axis == 2:
        joystick.left_joystick(joystick.report.sThumbLX, normalized_value)
    elif axis == 3:
        joystick.right_joystick(normalized_value, joystick.report.sThumbRY)
    elif axis == 4:
        joystick.right_joystick(normalized_value, joystick.report.sThumbRX)
    joystick.update()

# Function to calibrate a knob (axis)
def calibrate_knob(port, device_name, cc_number):
    QMessageBox.information(None, "Calibration", f"Turn the knob for CC {cc_number} from {device_name} to its maximum position.")
    max_value = None
    for message in port:
        if message.type == 'control_change' and message.control == cc_number:
            max_value = message.value
            break

    QMessageBox.information(None, "Calibration", f"Turn the knob for CC {cc_number} from {device_name} to its minimum position.")
    min_value = None
    for message in port:
        if message.type == 'control_change' and message.control == cc_number:
            min_value = message.value
            break

    if max_value is not None and min_value is not None:
        return min_value, max_value
    else:
        QMessageBox.warning(None, "Calibration Failed", f"Calibration failed for CC {cc_number} from {device_name}.")
        return None, None

# Setup mode to map MIDI notes to gamepad buttons, joystick axes, or keyboard keys
def setup_mode(port, device_name, gamepad, joystick, window):
    global midi_to_input_map
    QMessageBox.information(window, "Setup Mode", "Entered setup mapping mode. Press a button or turn a knob on the device to map it.")
    for message in port:
        if message.type == 'note_on' and message.velocity > 0:
            midi_note = message.note
            input_type, ok = QInputDialog.getText(window, "Input Type", f"Do you want to map MIDI note {midi_note} from {device_name} to a gamepad button, joystick axis, or a keyboard key? (Enter 'gamepad', 'joystick', 'keyboard', or 'exit' to return to main menu): ")
            if not ok or input_type.strip().lower() == 'exit':
                return
            elif input_type.strip().lower() == 'gamepad':
                button, ok = QInputDialog.getInt(window, "Gamepad Button", f"Enter the gamepad button number to map to MIDI note {midi_note} from {device_name} (an integer from 1 to 15 for buttons): ")
                if ok:
                    midi_to_input_map[(device_name, str(midi_note), 'note_on')] = {"type": "gamepad", "value": button, "device_id": id(gamepad)}
                    save_mappings(midi_to_input_map)
                    QMessageBox.information(window, "Mapping Saved", f"Mapped MIDI note {midi_note} from {device_name} to gamepad button {button}.")
            elif input_type.strip().lower() == 'joystick':
                axis, ok = QInputDialog.getInt(window, "Joystick Axis", f"Enter the joystick axis number to map to MIDI note {midi_note} from {device_name} (1-4 for axes): ")
                if ok and axis in [1, 2, 3, 4]:
                    midi_to_input_map[(device_name, str(midi_note), 'note_on')] = {"type": "axis", "value": axis, "device_id": id(joystick)}
                    save_mappings(midi_to_input_map)
                    QMessageBox.information(window, "Mapping Saved", f"Mapped MIDI note {midi_note} from {device_name} to joystick axis {axis}.")
            elif input_type.strip().lower() == 'keyboard':
                key, ok = QInputDialog.getText(window, "Keyboard Key", f"Enter the keyboard key to map to MIDI note {midi_note} from {device_name} (e.g., 'a', 'space', 'enter'): ")
                if ok:
                    midi_to_input_map[(device_name, str(midi_note), 'note_on')] = {"type": "keyboard", "value": key.strip()}
                    save_mappings(midi_to_input_map)
                    QMessageBox.information(window, "Mapping Saved", f"Mapped MIDI note {midi_note} from {device_name} to keyboard key {key.strip()}.")
        elif message.type == 'control_change':
            cc_number = message.control
            input_type, ok = QInputDialog.getText(window, "Input Type", f"Do you want to map CC {cc_number} from {device_name} to a gamepad axis, joystick axis, or a keyboard key? (Enter 'gamepad', 'joystick', 'keyboard', or 'exit' to return to main menu): ")
            if not ok or input_type.strip().lower() == 'exit':
                return
            elif input_type.strip().lower() == 'gamepad':
                axis, ok = QInputDialog.getInt(window, "Gamepad Axis", f"Enter the gamepad axis number to map to CC {cc_number} from {device_name} (3: left_thumb_x, 4: left_thumb_y, 5: right_thumb_x, 6: right_thumb_y): ")
                if ok and axis in [3, 4, 5, 6]:
                    min_value, max_value = calibrate_knob(port, device_name, cc_number)
                    if min_value is not None and max_value is not None:
                        midi_to_input_map[(device_name, str(cc_number), 'control_change')] = {
                            "type": "axis",
                            "value": axis,
                            "device_id": id(gamepad),
                            "min_value": min_value,
                            "max_value": max_value
                        }
                        save_mappings(midi_to_input_map)
                        QMessageBox.information(window, "Mapping Saved", f"Mapped CC {cc_number} from {device_name} to gamepad axis {axis} with calibration.")
            elif input_type.strip().lower() == 'joystick':
                axis, ok = QInputDialog.getInt(window, "Joystick Axis", f"Enter the joystick axis number to map to CC {cc_number} from {device_name} (1-4 for axes): ")
                if ok and axis in [1, 2, 3, 4]:
                    min_value, max_value = calibrate_knob(port, device_name, cc_number)
                    if min_value is not None and max_value is not None:
                        midi_to_input_map[(device_name, str(cc_number), 'control_change')] = {
                            "type": "axis",
                            "value": axis,
                            "device_id": id(joystick),
                            "min_value": min_value,
                            "max_value": max_value
                        }
                        save_mappings(midi_to_input_map)
                        QMessageBox.information(window, "Mapping Saved", f"Mapped CC {cc_number} from {device_name} to joystick axis {axis} with calibration.")
            elif input_type.strip().lower() == 'keyboard':
                key, ok = QInputDialog.getText(window, "Keyboard Key", f"Enter the keyboard key to map to CC {cc_number} from {device_name} (e.g., 'a', 'space', 'enter'): ")
                if ok:
                    midi_to_input_map[(device_name, str(cc_number), 'control_change')] = {"type": "keyboard", "value": key.strip()}
                    save_mappings(midi_to_input_map)
                    QMessageBox.information(window, "Mapping Saved", f"Mapped CC {cc_number} from {device_name} to keyboard key {key.strip()}.")

# Main listening function
def listen_for_midi(port, device_name, gamepad, joystick, window):
    global midi_to_input_map
    QMessageBox.information(window, "Listening", "Listening for MIDI inputs...")
    for message in port:
        if message.type == 'note_on' and message.velocity > 0:
            midi_note = message.note
            input_map = midi_to_input_map.get((device_name, str(midi_note), 'note_on'))
            print(f"Checking mapping for MIDI note {midi_note} from {device_name}: {input_map}")
            if input_map:
                input_type = input_map["type"]
                value = input_map["value"]
                if input_type == "gamepad" and id(gamepad) == input_map["device_id"]:
                    press_gamepad_button(gamepad, value)
                elif input_type == "keyboard":
                    press_keyboard_key(value)
            else:
                print(f"No input mapping found for MIDI note {midi_note} from {device_name}")
                QMessageBox.information(window, "No Mapping Found", f"No input mapping found for MIDI note {midi_note} from {device_name}")
        elif message.type == 'control_change':
            cc_number = str(message.control)
            input_map = midi_to_input_map.get((device_name, cc_number, 'control_change'))
            print(f"Checking mapping for CC {cc_number} from {device_name}: {input_map}")
            if input_map:
                input_type = input_map["type"]
                value = input_map["value"]
                min_value = input_map.get("min_value", 0)
                max_value = input_map.get("max_value", 127)
                knob_value = message.value
                if input_type == "axis":
                    if id(gamepad) == input_map["device_id"]:
                        move_gamepad_axis(gamepad, value, knob_value, min_value, max_value)
                    elif id(joystick) == input_map["device_id"]:
                        move_joystick_axis(joystick, value, knob_value, min_value, max_value)
                elif input_type == "keyboard":
                    press_keyboard_key(value)
                print(f"Knob value: {knob_value}")
            else:
                print(f"No input mapping found for CC {cc_number} from {device_name}")
                QMessageBox.information(window, "No Mapping Found", f"No input mapping found for CC {cc_number} from {device_name}")

class DeviceSelectionDialog(QDialog):
    def __init__(self, ports, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select MIDI Input Ports")
        self.layout = QVBoxLayout(self)
        self.checkboxes = []

        for port in ports:
            checkbox = QCheckBox(port)
            self.layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_selected_ports(self):
        return [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]

def select_midi_ports(window):
    ports = mido.get_input_names()
    if not ports:
        QMessageBox.critical(window, "Error", "No MIDI input ports found.")
        return None

    dialog = DeviceSelectionDialog(ports, window)
    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_selected_ports()
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
        port_names = select_midi_ports(self)
        if port_names:
            for port_name in port_names:
                gamepad = vg.VX360Gamepad()  # Create a gamepad for each selected MIDI device
                joystick = vg.VX360Gamepad()  # Create a joystick for each selected MIDI device
                with mido.open_input(port_name) as port:
                    listen_for_midi(port, port_name, gamepad, joystick, self)

    def on_setup(self):
        port_names = select_midi_ports(self)
        if port_names:
            for port_name in port_names:
                gamepad = vg.VX360Gamepad()  # Create a gamepad for each selected MIDI device
                joystick = vg.VX360Gamepad()  # Create a joystick for each selected MIDI device
                with mido.open_input(port_name) as port:
                    setup_mode(port, port_name, gamepad, joystick, self)

    def on_exit(self):
        self.close()

def main():
    app = QApplication(sys.argv)
    ex = MidiJoyApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
