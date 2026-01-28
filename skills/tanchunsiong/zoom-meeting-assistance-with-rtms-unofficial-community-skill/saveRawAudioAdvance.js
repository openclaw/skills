import fs from 'fs';
import path from 'path';
import { sanitizeFileName } from './tool.js';

// Cache for open write streams
const writeStreams = new Map();
// Map to store the last timestamps for each audio stream
const lastAudioTimestamps = new Map();

// Generate silent audio frame (PCM silence) for 16-bit, 16 kHz, mono
function generateSilentAudioFrame(sampleRate, durationMs) {
    const samples = (sampleRate * durationMs) / 1000;
    return Buffer.alloc(samples * 2, 0); // 16-bit PCM, silence (mono)
}

export function saveRawAudio(chunk, streamId, user_id, timestamp) {

    const safeStreamId = sanitizeFileName(streamId);

    // Build path: recordings/{streamId}/{userId}.raw
    const filePath = `recordings/${safeStreamId}/${user_id}.raw`;

    // If the folder doesn't exist yet, create it
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }

    // Check if a stream already exists for this file
    let stream = writeStreams.get(filePath);
    if (!stream) {
        stream = fs.createWriteStream(filePath, { flags: 'a' }); // append mode
        writeStreams.set(filePath, stream);
    }

    // Handle padding for audio gaps only if the gap is 500ms or more
    const key = `${streamId}_${user_id}`;
    const lastTimestamp = lastAudioTimestamps.get(key) || timestamp;
    const timeDifference = timestamp - lastTimestamp;

    // Assume audio sample rate of 16 kHz (mono)
    if (timeDifference >= 500) { // Gap of 500 ms or more
        const numberOfFrames = Math.floor(timeDifference / 20);
        console.log(`Detected gap of ${timeDifference}ms. Filling with ${numberOfFrames} silent audio frames.`);

        for (let i = 0; i < numberOfFrames; i++) {
            const silentFrame = generateSilentAudioFrame(16000, 20); // 20 ms frame
            stream.write(silentFrame);
        }
    }

    lastAudioTimestamps.set(key, timestamp);
    stream.write(chunk);
}

// (Optional) Close all streams when needed
export function closeAllStreams() {
    for (const stream of writeStreams.values()) {
        stream.end();
    }
    writeStreams.clear();
}
