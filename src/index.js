const midiHandler = require('./midiHandler');
const keyMapper = require('./keyMapper');

midiHandler.initialize(keyMapper.mapMidiToKey);

console.log("Listening for MIDI inputs...");
