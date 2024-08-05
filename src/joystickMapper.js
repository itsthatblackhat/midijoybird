const vJoy = require('vjoy');

// Initialize the vJoy device
const joystick = vJoy();

if (!joystick) {
    console.log("Failed to initialize vJoy. Please check your vJoy installation.");
    process.exit();
}

function mapMidiToJoystick(message) {
    const [status, data1, data2] = message;
    if (status === 144) { // Note on
        joystick.buttons[data1] = data2 > 0 ? true : false;
        joystick.update();
    }
}

module.exports = { mapMidiToJoystick };
