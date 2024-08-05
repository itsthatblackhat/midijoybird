const midi = require('midi');
const readline = require('readline');
const fs = require('fs');
const path = require('path');
const configPath = path.join(__dirname, 'config.json');

// Set up a new input.
const input = new midi.Input();
let mappingMode = false;

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function initialize(callback) {
    const portCount = input.getPortCount();

    if (portCount === 0) {
        console.error("No MIDI input devices found.");
        return;
    }

    console.log(`Found ${portCount} MIDI input ports:`);
    for (let i = 0; i < portCount; i++) {
        console.log(`${i}: ${input.getPortName(i)}`);
    }

    // Open the first available input port.
    input.openPort(0);
    console.log(`Opened MIDI input port: ${input.getPortName(0)}`);

    // Handle MIDI input and map to key
    input.on('message', (deltaTime, message) => {
        if (mappingMode) {
            handleMappingMode(message);
        } else {
            callback(message);
        }
    });

    rl.on('line', (input) => {
        if (input.trim().toLowerCase() === 'setup') {
            enterMappingMode();
        }
    });
}

function enterMappingMode() {
    mappingMode = true;
    console.log("Entered setup mapping mode. Press a button on the Launchpad to map it to a keyboard key.");
}

function handleMappingMode(message) {
    const [status, data1, data2] = message;
    if (status === 144 && data2 > 0) { // Note on
        rl.question(`Press the key you want to map to MIDI note ${data1}: `, (key) => {
            saveMapping(data1, key);
            console.log(`Mapped MIDI note ${data1} to key ${key}.`);
            mappingMode = false;
        });
    }
}

function saveMapping(note, key) {
    let config = {};
    if (fs.existsSync(configPath)) {
        const data = fs.readFileSync(configPath);
        if (data.length > 0) {
            config = JSON.parse(data);
        }
    }
    config[note] = key;
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
}

module.exports = { initialize };
