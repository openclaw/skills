import fs from 'fs';
import path from 'path';
import { sanitizeFileName } from './tool.js';

let srtIndex = 1;
const streamStartTimestamps = new Map(); // Track start timestamp per stream

// 🔧 Set session start (optional external call)
export function setTranscriptStartTimestamp(ts) {
  console.log(`⚠️ setTranscriptStartTimestamp is deprecated - timestamps are now auto-managed per stream`);
}

// Reset transcript state for a new stream
export function resetTranscriptForStream(streamId) {
  const safeStreamId = sanitizeFileName(streamId);
  streamStartTimestamps.delete(safeStreamId);
  console.log(`🔄 Reset transcript tracking for stream: ${safeStreamId}`);
}

// Set the start timestamp for a specific stream
export function setStreamStartTimestamp(streamId, timestamp) {
  const safeStreamId = sanitizeFileName(streamId);
  streamStartTimestamps.set(safeStreamId, timestamp);
  console.log(`⏱️ Set start timestamp for stream ${safeStreamId}: ${timestamp} (${new Date(timestamp).toISOString()})`);
}

function formatVttTimestamp(ms) {
  if (isNaN(ms) || ms < 0) return '00:00:00.000';

  const totalSeconds = Math.floor(ms / 1000);
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  const msPart = ms % 1000;

  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${String(msPart).padStart(3, '0')}`;
}

function formatSrtTimestamp(ms) {
  if (isNaN(ms) || ms < 0) return '00:00:00,000';

  const totalSeconds = Math.floor(ms / 1000);
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  const msPart = ms % 1000;

  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')},${String(msPart).padStart(3, '0')}`;
}

// ✨ Accept meetingFolder as extra parameter
export function writeTranscriptToVtt(user_name, timestamp, data, streamId) {

  const safeStreamId = sanitizeFileName(streamId);

  const meetingFolder = path.join('recordings', safeStreamId);
  if (!fs.existsSync(meetingFolder)) {
    fs.mkdirSync(meetingFolder, { recursive: true });
  }

  // Get or set start timestamp for this stream
  if (!streamStartTimestamps.has(safeStreamId)) {
    streamStartTimestamps.set(safeStreamId, timestamp);
    console.log(`⏱️ First transcript for stream ${safeStreamId} - setting start timestamp: ${timestamp}`);
  }

  const startTimestamp = streamStartTimestamps.get(safeStreamId);

  // 🔥 Ensure the meeting folder exists
  if (!fs.existsSync(meetingFolder)) {
    fs.mkdirSync(meetingFolder, { recursive: true });
  }

  // Build output file paths inside the meeting folder
  const vttFilePath = path.join(meetingFolder, 'transcript.vtt');
  const srtFilePath = path.join(meetingFolder, 'transcript.srt');
  const txtFilePath = path.join(meetingFolder, 'transcript.txt');

  const relative = timestamp - startTimestamp;
  console.log(`📊 Timestamp calculation for ${safeStreamId}:`);
  console.log(`   Current timestamp: ${timestamp} (${new Date(timestamp).toISOString()})`);
  console.log(`   Start timestamp: ${startTimestamp} (${new Date(startTimestamp).toISOString()})`);
  console.log(`   Relative time: ${relative}ms = ${Math.floor(relative / 1000)}s`);

  const start = formatVttTimestamp(relative);
  const end = formatVttTimestamp(relative + 2000);
  const vttLine = `${start} --> ${end}\n${user_name}: ${data}\n\n`;

  if (!fs.existsSync(vttFilePath)) {
    fs.writeFileSync(vttFilePath, 'WEBVTT\n\n');
  }
  fs.appendFileSync(vttFilePath, vttLine);
  //console.log(`📝 VTT saved to ${vttFilePath}`);

  const srtStart = formatSrtTimestamp(relative);
  const srtEnd = formatSrtTimestamp(relative + 2000);
  const srtLine = `${srtIndex++}\n${srtStart} --> ${srtEnd}\n${user_name}: ${data}\n\n`;

  fs.appendFileSync(srtFilePath, srtLine);
  //console.log(`🎞️ SRT saved to ${srtFilePath}`);

  const readableTime = new Date(timestamp).toISOString();
  const txtLine = `[${readableTime}] ${user_name}: ${data}\n`;
  fs.appendFileSync(txtFilePath, txtLine);
  //console.log(`📄 TXT saved to ${txtFilePath}`);
}
