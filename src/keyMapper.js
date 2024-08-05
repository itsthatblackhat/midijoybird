const robot = require('robotjs');
const fs = require('fs');
const path = require('path');
const configPath = path.join(__dirname, 'config.json');

let midiToKeyMap = {};

// Load the config file
if (fs.existsSync(configPath)) {
    try {
        const data = fs.readFileSync(configPath);
        if (data.length > 0) {
            midiToKeyMap = JSON.parse(data);
            console.log("Loaded mappings from config file:", midiToKeyMap);
        } else {
            console.warn("Config file is empty. No mappings loaded.");
        }
    } catch (err) {
        console.error("Error reading config file:", err);
    }
} else {
    console.warn("Config file not found. No mappings loaded.");
}

function mapMidiToKey(message) {
    const [status, data1, data2] = message;
    console.log(`Mapping MIDI message to key: status=${status}, data1=${data1}, data2=${data2}`);
    if (status === 144) { // Note on
        const key = midiToKeyMap[data1];
        if (key) {
            if (data2 > 0) {
                console.log(`Pressing key: ${key}`);
                robot.keyTap(key);
            }
        } else {
            console.log(`No key mapping found for MIDI note: ${data1}`);
        }
    }
}

module.exports = { mapMidiToKey };
