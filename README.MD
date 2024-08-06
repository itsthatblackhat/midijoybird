
# MidiJoy-LaunchpadMini

This project maps MIDI inputs from a Novation Launchpad Mini to gamepad buttons or keyboard keys, allowing you to use the Launchpad to control games or other applications.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/itsthatblackhat/midijoybird.git
   cd MidiJoy-LaunchpadMini
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scriptsctivate
   ```

3. Install the required packages:
   ```bash
   pip install mido python-rtmidi vgamepad pynput
   ```

## Usage

1. Run the script:
   ```bash
   python launchpad_to_gamepad.py
   ```

2. Select the MIDI input port when prompted:
   ```
   Available MIDI input ports:
   0: Launchpad Mini 0
   Select the MIDI input port index: 0
   ```

3. Use the interactive menu to choose an option:
   ```
   Menu:
   1. Listen for MIDI inputs
   2. Setup mode (map MIDI notes to gamepad buttons or keyboard keys)
   3. Exit
   Select an option: 
   ```

4. In Setup mode, press a button on the Launchpad and follow the prompts to map it to a gamepad button or keyboard key:
   ```
   Do you want to map MIDI note 24 to a gamepad button or a keyboard key? (Enter 'gamepad' or 'keyboard', or 'exit' to return to main menu): keyboard
   Enter the keyboard key to map to MIDI note 24 (e.g., 'a', 'space', 'enter'): r
   Mapped MIDI note 24 to keyboard key r.
   ```

5. To listen for MIDI inputs, select option 1 in the main menu and press the mapped buttons on the Launchpad to see the corresponding gamepad button or keyboard key presses.

6. To exit the program, select option 3 in the main menu.
