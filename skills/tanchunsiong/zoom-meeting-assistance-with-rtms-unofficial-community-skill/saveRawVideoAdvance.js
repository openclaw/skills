import fs from 'fs';
import path from 'path';
import { sanitizeFileName } from './tool.js';

const spsWrittenMap = new Map();
const spsHeader = fs.readFileSync('sps_pps_keyframe.h264');

function hasStartCode(buffer) {
    return buffer.indexOf(Buffer.from([0x00, 0x00, 0x00, 0x01])) !== -1;
}

 const blackFrame = fs.readFileSync('black_frame.h264');

// Keep a simple map to reuse write streams
const videoWriteStreams = new Map();

// Define a map to store the last timestamps for each meeting
const lastTimestamps = new Map();

export function saveRawVideo(buffer, userName, timestamp, streamId) {
    const safeStreamId = sanitizeFileName(streamId);
    const outputDir = path.join('recordings', safeStreamId);

    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const filePath = path.join(outputDir, `combined.h264`);

    let writeStream = videoWriteStreams.get(filePath);
    if (!writeStream) {
        writeStream = fs.createWriteStream(filePath, { flags: 'a' });
        videoWriteStreams.set(filePath, writeStream);
    }

    // Write SPS/PPS headers once per meeting stream
    if (!spsWrittenMap.get(safeStreamId)) {
        writeStream.write(spsHeader);
        spsWrittenMap.set(safeStreamId, true);
    }

    // Step 3: Gap detection (global for the combined meeting video)
    const lastTimestamp = lastTimestamps.get(safeStreamId) || timestamp;
    const timeDifference = timestamp - lastTimestamp;

    if (timeDifference > 500) {
        const missingFrames = Math.floor(timeDifference / 40); // assuming 25fps
        console.log(`🕳️ Gap detected (${timeDifference}ms) in stream ${streamId}. Filling ${missingFrames} black frames.`);

        for (let i = 0; i < missingFrames; i++) {
            writeStream.write(blackFrame);
        }
    }

    // Step 4: Write frame + update timestamp
    writeStream.write(buffer);
    lastTimestamps.set(safeStreamId, timestamp);
}
