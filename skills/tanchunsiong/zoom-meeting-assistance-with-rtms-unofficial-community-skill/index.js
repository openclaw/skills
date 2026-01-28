import express from 'express';
import crypto from 'crypto';
import { WebSocket } from 'ws';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { resetTranscriptForStream, setStreamStartTimestamp } from './writeTranscriptToVtt.js';

//used for saving audio and video frm RTMS stream
import { saveRawAudio as saveRawAudioAdvance } from './saveRawAudioAdvance.js';
import { saveRawVideo as saveRawVideoAdvance } from './saveRawVideoAdvance.js';

//used for saving transcript
import { writeTranscriptToVtt } from './writeTranscriptToVtt.js';

//used for saving screenshare 
import { handleShareData, generatePDFAndText } from './saveSharescreen.js';



import { sanitizeFileName } from './tool.js';

// Import Clawdbot AI functions
import { chatWithClawdbot, chatWithClawdbotFast, generateDialogSuggestions, analyzeSentiment, generateRealTimeSummary, queryCurrentMeeting, notifyUser } from './chatWithClawdbot.js';

// Load environment variables from a .env file
dotenv.config();

// Runtime notification toggle
let notificationsEnabled = true;

// AI processing cache for interval-based debouncing
const aiCache = new Map();
const AI_PROCESSING_INTERVAL_MS = parseInt(process.env.AI_PROCESSING_INTERVAL_MS || '30000');
const AI_FUNCTION_STAGGER_MS = parseInt(process.env.AI_FUNCTION_STAGGER_MS || '5000');

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const app = express();
const port = process.env.PORT || 3000;

const ZOOM_SECRET_TOKEN = process.env.ZOOM_SECRET_TOKEN;
const CLIENT_ID = process.env.ZOOM_CLIENT_ID;
const CLIENT_SECRET = process.env.ZOOM_CLIENT_SECRET;
const WEBHOOK_PATH = process.env.WEBHOOK_PATH || '/webhook';


// Middleware to parse JSON and URL-encoded bodies
app.use(express.json());
app.use(express.urlencoded({ extended: true }));



// Map to keep track of active WebSocket connections and audio chunks (stream_id -> connection data)
const activeConnections = new Map();

app.post('/api/notify-toggle', express.json(), (req, res) => {
  const { enabled } = req.body;
  if (typeof enabled === 'boolean') {
    notificationsEnabled = enabled;
  }
  res.json({ notificationsEnabled });
});

app.get('/api/notify-toggle', (req, res) => {
  res.json({ notificationsEnabled });
});



// Handle POST requests to the webhook endpoint
app.post(WEBHOOK_PATH, async (req, res) => {
  // Respond with HTTP 200 status
  res.sendStatus(200);
  console.log('RTMS Webhook received:', JSON.stringify(req.body, null, 2));
  const { event, payload } = req.body;

  // Handle URL validation event
  if (event === 'endpoint.url_validation' && payload?.plainToken) {
    // Generate a hash for URL validation using the plainToken and a secret token
    const hash = crypto
      .createHmac('sha256', ZOOM_SECRET_TOKEN)
      .update(payload.plainToken)
      .digest('hex');
    console.log('Responding to URL validation challenge');
    return res.json({
      plainToken: payload.plainToken,
      encryptedToken: hash,
    });
  }

  // Handle RTMS started event
  if (event === 'meeting.rtms_started') {
    console.log('RTMS Started event received');
    const { meeting_uuid, rtms_stream_id, server_urls } = payload;
    // Initiate connection to the signaling WebSocket server
    connectToSignalingWebSocket(meeting_uuid, rtms_stream_id, server_urls);
  }

   // Handle RTMS stopped event
   if (event === 'meeting.rtms_stopped') {
     console.log('RTMS Stopped event received');

     const { meeting_uuid, rtms_stream_id, server_urls } = payload;
     // Close all active WebSocket connections for the given meeting UUID
     if (activeConnections.has(rtms_stream_id)) {
       const connections = activeConnections.get(rtms_stream_id);
       connections.shouldReconnect = false;
       console.log('Closing active connections for stream: ' + rtms_stream_id);
       for (const [key, conn] of Object.entries(connections)) {
         if (key !== 'shouldReconnect' && conn && typeof conn.close === 'function') {
           conn.close();
         }
       }
       activeConnections.delete(rtms_stream_id);
     }

     await notifyUser(`Meeting stream ended: ${rtms_stream_id}`);

     // Generate PDF from the unique screen share images
     console.log('Generating PDF from screen share images for stream: ' + rtms_stream_id);
     await generatePDFAndText(rtms_stream_id);
   }
});

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function scheduleAIProcessing(streamId, meetingUuid) {
  const now = Date.now();
  const safeStreamId = sanitizeFileName(streamId);
  const cache = aiCache.get(streamId) || {};

  if (cache.lastUpdated && (now - cache.lastUpdated) < AI_PROCESSING_INTERVAL_MS) {
    return;
  }

  if (cache.processing) {
    return;
  }

  cache.processing = true;
  cache.lastUpdated = now;
  aiCache.set(streamId, cache);

  try {
    const vttPath = `recordings/${safeStreamId}/transcript.vtt`;
    const eventsPath = `recordings/${safeStreamId}/events.log`;
    const transcript = fs.existsSync(vttPath) ? fs.readFileSync(vttPath, 'utf-8') : '';
    const eventsLog = fs.existsSync(eventsPath) ? fs.readFileSync(eventsPath, 'utf-8') : '';

    if (!transcript || transcript.trim().length < 50) {
      cache.processing = false;
      aiCache.set(streamId, cache);
      return;
    }

    const outDir = `recordings/${safeStreamId}`;
    fs.mkdirSync(outDir, { recursive: true });

    const dialogResult = await generateDialogSuggestions(transcript);
    cache.dialog = dialogResult;
    fs.writeFileSync(`${outDir}/ai_dialog.json`, JSON.stringify(dialogResult, null, 2));
    if (notificationsEnabled) {
      const dialogText = Array.isArray(dialogResult) ? dialogResult.join('\n') : JSON.stringify(dialogResult);
      await notifyUser(`🗣️ Dialog suggestions:\n${dialogText}`);
    }

    await sleep(AI_FUNCTION_STAGGER_MS);

    const sentimentResult = await analyzeSentiment(transcript);
    cache.sentiment = sentimentResult;
    fs.writeFileSync(`${outDir}/ai_sentiment.json`, JSON.stringify(sentimentResult, null, 2));
    if (notificationsEnabled) {
      await notifyUser(`😊 Sentiment update:\n${JSON.stringify(sentimentResult, null, 2)}`);
    }

    await sleep(AI_FUNCTION_STAGGER_MS);

    const summaryResult = await generateRealTimeSummary(transcript, eventsLog, [], streamId, meetingUuid);
    cache.summary = summaryResult;
    fs.writeFileSync(`${outDir}/ai_summary.md`, summaryResult);
    if (notificationsEnabled) {
      await notifyUser(`📝 Meeting summary:\n${summaryResult.substring(0, 500)}`);
    }

    console.log(`✅ AI processing completed for stream ${streamId}`);
  } catch (err) {
    console.error(`❌ AI processing error for stream ${streamId}:`, err.message);
  } finally {
    cache.processing = false;
    aiCache.set(streamId, cache);
  }
}

// Function to generate a signature for authentication
function generateSignature(CLIENT_ID, meetingUuid, streamId, CLIENT_SECRET) {
  console.log('Generating signature with parameters:');
  console.log('meetingUuid:', meetingUuid);
  console.log('streamId:', streamId);
  console.log('CLIENT_ID:', CLIENT_ID);

  // Create a message string and generate an HMAC SHA256 signature
  const message = `${CLIENT_ID},${meetingUuid},${streamId}`;
  const signature = crypto.createHmac('sha256', CLIENT_SECRET).update(message).digest('hex');
  console.log('Generated signature:', signature);
  return signature;
}

// Function to connect to the signaling WebSocket server
function connectToSignalingWebSocket(meetingUuid, streamId, serverUrl) {
  console.log(`Connecting to signaling WebSocket for stream ${streamId}`);
  console.log('Stream ID:', streamId);
  console.log('Server URL:', serverUrl);

  const safeStreamId = sanitizeFileName(streamId);
  console.log('Sanitized Meeting UUID:', safeStreamId);

  const ws = new WebSocket(serverUrl);
  console.log('WebSocket created successfully');

  // Store connection for cleanup later
  if (!activeConnections.has(streamId)) {
    activeConnections.set(streamId, { shouldReconnect: true });
  }
  activeConnections.get(streamId).signaling = ws;
  const streamStartTime = Date.now();
  activeConnections.get(streamId).startTime = streamStartTime;
  activeConnections.get(streamId).meetingUuid = meetingUuid;
  activeConnections.get(streamId).sanitizedMeetingUuid = sanitizeFileName(meetingUuid);
  console.log('Signaling connection stored for cleanup');

  // Set the transcript start timestamp for this stream
  resetTranscriptForStream(streamId); // Clear any previous data for this stream
  setStreamStartTimestamp(streamId, streamStartTime);
  console.log(`⏱️ Set transcript start time for stream ${streamId}: ${streamStartTime} (${new Date(streamStartTime).toISOString()})`);


  // Function to format timestamp to VTT format (HH:MM:SS.mmm)
  function formatVTTTime(ms) {
    const hours = Math.floor(ms / 3600000);
    const minutes = Math.floor((ms % 3600000) / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    const milliseconds = ms % 1000;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
  }

  // Event type map for verbose names
  const eventTypeNames = {
    2: 'active_speaker_changed',
    3: 'participant_joined',
    4: 'participant_left'
  };

  ws.on('open', () => {
    console.log(`Signaling WebSocket connection opened for stream ${streamId}`);
    const signature = generateSignature(
      CLIENT_ID,
      meetingUuid,
      streamId,
      CLIENT_SECRET
    );

    // Send handshake message to the signaling server
    const handshake = {
      msg_type: 1, // SIGNALING_HAND_SHAKE_REQ
      protocol_version: 1,
      meeting_uuid: meetingUuid,
      rtms_stream_id: streamId,
      sequence: Math.floor(Math.random() * 1e9),
      signature,
    };
    ws.send(JSON.stringify(handshake));
    console.log('Sent handshake to signaling server');
  });

  ws.on('message', (data) => {
    const msg = JSON.parse(data);
    console.log('Signaling Message:', JSON.stringify(msg, null, 2));

    // Handle successful handshake response
    if (msg.msg_type === 2 && msg.status_code === 0) { // SIGNALING_HAND_SHAKE_RESP
      const mediaUrl = msg.media_server?.server_urls?.all;
      if (mediaUrl) {
        // Connect to the media WebSocket server using the media URL
        connectToMediaWebSocket(mediaUrl, meetingUuid, safeStreamId, streamId, ws);
      }

      //subscribe to events 
      const payload = {
        msg_type: 5,
        events: [
          { event_type: 2, subscribe: true },
          { event_type: 3, subscribe: true },
          { event_type: 4, subscribe: true }
        ]
      };
      ws.send(JSON.stringify(payload));
      console.log('[SUCCESS] Event Subscription Payload sent:', JSON.stringify(payload, null, 2));
    }

    if (msg.msg_type === 6) {
      console.log("Event Subscription Received.");

      switch (msg.event.event_type) {
        case 1:
          console.log("Event: First packet capture timestamp received.");
          break;
        case 2:
          console.log("Event: Active speaker has changed.");
          const eventData2 = { ...msg.event, event_type: eventTypeNames[msg.event.event_type] };
          fs.mkdirSync(`recordings/${safeStreamId}`, { recursive: true });
          fs.appendFileSync(`recordings/${safeStreamId}/events.log`, JSON.stringify({ timestamp: formatVTTTime(Date.now() - activeConnections.get(streamId).startTime), event: eventData2 }) + '\n');
          break;
        case 3:
          console.log("Event: Participant joined.");
          const eventData3 = { ...msg.event, event_type: eventTypeNames[msg.event.event_type] };
          fs.mkdirSync(`recordings/${safeStreamId}`, { recursive: true });
          fs.appendFileSync(`recordings/${safeStreamId}/events.log`, JSON.stringify({ timestamp: formatVTTTime(Date.now() - activeConnections.get(streamId).startTime), event: eventData3 }) + '\n');
          break;
        case 4:
          console.log("Event: Participant left.");
          const eventData4 = { ...msg.event, event_type: eventTypeNames[msg.event.event_type] };
          fs.mkdirSync(`recordings/${safeStreamId}`, { recursive: true });
          fs.appendFileSync(`recordings/${safeStreamId}/events.log`, JSON.stringify({ timestamp: formatVTTTime(Date.now() - activeConnections.get(streamId).startTime), event: eventData4 }) + '\n');
          break;
        default:
          console.log("Event: Unknown event type.");
      }
    }

    if (msg.msg_type === 8) {
      console.log("Stream Update Received.");

      switch (msg.state) {
        case 0:
          console.log("Stream State: Inactive.");
          break;
        case 1:
          console.log("Stream State: Active.");
          break;
        case 2:
          console.log("Stream State: Interrupted.");
          break;
        case 3:
        case 4:
          console.log("Stream State: Terminating.");
          break;
        default:
          console.log("Stream State: Unknown state.");
      }

      switch (msg.reason) {
        case 1:
          console.log("Stopped because the host triggered it.");
          break;
        case 2:
          console.log("Stopped because the user triggered it.");
          break;
        case 3:
          console.log("Stopped because the user left.");
          break;
        case 4:
          console.log("Stopped because the user was ejected.");
          break;
        case 5:
          console.log("Stopped because the app was disabled by the host.");
          break;
        case 6:
          console.log("Stopped because the meeting ended.");
          break;
        case 7:
          console.log("Stopped because the stream was canceled.");
          break;
        case 8:
          console.log("Stopped because the stream was revoked.");
          break;
        case 9:
          console.log("Stopped because all apps were disabled.");
          break;
        case 10:
          console.log("Stopped due to an internal exception.");
          break;
        case 11:
          console.log("Stopped because the connection timed out.");
          break;
        case 12:
          console.log("Stopped due to meeting connection interruption.");
          break;
        case 13:
          console.log("Stopped because the signaling connection was interrupted.");
          break;
        case 14:
          console.log("Stopped because the data connection was interrupted.");
          break;
        case 15:
          console.log("Stopped because the signaling connection closed abnormally.");
          break;
        case 16:
          console.log("Stopped because the data connection closed abnormally.");
          break;
        case 17:
          console.log("Stopped due to receiving an exit signal.");
          break;
        case 18:
          console.log("Stopped due to an authentication failure.");
          break;
        default:
          console.log("Stopped for an unknown reason.");
      }
    }

    if (msg.msg_type === 9) {
      console.log("Session State Update Received.");

      switch (msg.state) {
        case 2:
          console.log("Session State: Started.");
          break;
        case 3:
          console.log("Session State: Paused.");
          break;
        case 4:
          console.log("Session State: Resumed.");
          break;
        case 5:
          console.log("Session State: Stopped.");
          break;
        default:
          console.log("Session State: Unknown state.");
      }

      switch (msg.reasone) {
        case 1:
          console.log("Stopped because the host triggered it.");
          break;
        case 2:
          console.log("Stopped because the user triggered it.");
          break;
        case 3:
          console.log("Stopped because the user left.");
          break;
        case 4:
          console.log("Stopped because the user was ejected.");
          break;
        case 5:
          console.log("Stopped because the app was disabled by the host.");
          break;
        case 6:
          console.log("Stopped because the meeting ended.");
          break;
        case 7:
          console.log("Stopped because the stream was canceled.");
          break;
        case 8:
          console.log("Stopped because the stream was revoked.");
          break;
        case 9:
          console.log("Stopped because all apps were disabled.");
          break;
        case 10:
          console.log("Stopped due to an internal exception.");
          break;
        case 11:
          console.log("Stopped because the connection timed out.");
          break;
        case 12:
          console.log("Stopped due to meeting connection interruption.");
          break;
        case 13:
          console.log("Stopped because the signaling connection was interrupted.");
          break;
        case 14:
          console.log("Stopped because the data connection was interrupted.");
          break;
        case 15:
          console.log("Stopped because the signaling connection closed abnormally.");
          break;
        case 16:
          console.log("Stopped because the data connection closed abnormally.");
          break;
        case 17:
          console.log("Stopped due to receiving an exit signal.");
          break;
        case 18:
          console.log("Stopped due to an authentication failure.");
          break;
        default:
          console.log("Stopped for an unknown reason.");
      }
    }
    // Respond to keep-alive requests
    if (msg.msg_type === 12) { // KEEP_ALIVE_REQ
      const keepAliveResponse = {
        msg_type: 13, // KEEP_ALIVE_RESP
        timestamp: msg.timestamp,
      };
      console.log('Responding to Signaling KEEP_ALIVE_REQ:', keepAliveResponse);
      ws.send(JSON.stringify(keepAliveResponse));
    }
  });

  ws.on('error', (err) => {
    console.error('Signaling socket error:', err);
  });

  ws.on('close', () => {
    console.log('Signaling socket closed');
    const conn = activeConnections.get(streamId);
    if (conn) {
      delete conn.signaling;
      if (conn.shouldReconnect !== false) {
        console.log(`🔄 Signaling reconnecting in 3000ms...`);
        setTimeout(() => {
          const c = activeConnections.get(streamId);
          if (c && c.shouldReconnect !== false) {
            connectToSignalingWebSocket(meetingUuid, streamId, serverUrl);
          }
        }, 3000);
      }
    }
  });
}

// Function to connect to the media WebSocket server
function connectToMediaWebSocket(mediaUrl, meetingUuid, safestreamId, streamId, signalingSocket) {
  console.log(`Connecting to media WebSocket at ${mediaUrl}`);

  const mediaWs = new WebSocket(mediaUrl, { rejectUnauthorized: false });

  // Store connection for cleanup later
  if (activeConnections.has(streamId)) {
    activeConnections.get(streamId).media = mediaWs;
  }



  mediaWs.on('open', () => {
    const signature = generateSignature(
      CLIENT_ID,
      meetingUuid,
      streamId,
      CLIENT_SECRET
    );
    const handshake = {
      msg_type: 3, // DATA_HAND_SHAKE_REQ
      protocol_version: 1,
      meeting_uuid: meetingUuid,
      rtms_stream_id: streamId,
      signature,
      media_type: 32, // AUDIO+VIDEO+TRANSCRIPT
      payload_encryption: false,
      media_params: {
        audio: {
          content_type: 1,
          sample_rate: 1,
          channel: 1,
          codec: 1,
          data_opt: 1,   //AUDIO_MIXED_STREAM = 1,     AUDIO_MULTI_STREAMS = 2,     
          send_rate: 100
        },
        video: {
          codec: 7, //H264
          resolution: 2,
          fps: 25
        },
        deskshare: {
          codec: 5, //JPG,
          resolution: 2, //720p
          fps: 1
        },
        chat: {
          content_type: 5, //TEXT
        },
        transcript: {
          content_type: 5 //TEXT
        }
      }
    };
    mediaWs.send(JSON.stringify(handshake));
  });

  mediaWs.on('message', (data) => {
    try {
      // Try to parse as JSON first
      const msg = JSON.parse(data.toString());
      //console.log('Media JSON Message:', JSON.stringify(msg, null, 2));

      // Handle successful media handshake
      if (msg.msg_type === 4 && msg.status_code === 0) { // DATA_HAND_SHAKE_RESP
        signalingSocket.send(
          JSON.stringify({
            msg_type: 7, // CLIENT_READY_ACK
            rtms_stream_id: streamId,
          })
        );
        console.log('Media handshake successful, sent start streaming request');
      }

      // Respond to keep-alive requests
      if (msg.msg_type === 12) { // KEEP_ALIVE_REQ
        mediaWs.send(
          JSON.stringify({
            msg_type: 13, // KEEP_ALIVE_RESP
            timestamp: msg.timestamp,
          })
        );
        console.log('Responded to Media KEEP_ALIVE_REQ');
      }

      // Handle audio data
      if (msg.msg_type === 14 && msg.content && msg.content.data) {

        let { user_id, user_name, data: audioData, timestamp } = msg.content;
        
        // Defensive logging: check for undefined fields
        if ((user_id === undefined || user_id === null) || !audioData || !timestamp) {
          console.warn(`⚠️ Missing expected fields in msg_type 14 (audio). Available keys:`, Object.keys(msg.content));
          console.warn(`⚠️ Values: user_id=${user_id}, user_name=${user_name}, data=${audioData ? 'present' : 'missing'}, timestamp=${timestamp}`);
        }
        
        let buffer = Buffer.from(audioData, 'base64');
        //console.log(`Processing audio data for user ${user_name} (ID: ${user_id}), buffer size: ${buffer.length} bytes`);
        saveRawAudioAdvance(buffer, streamId, user_id, Date.now()); // Primary method

      }
      // Handle video data
      if (msg.msg_type === 15 && msg.content && msg.content.data) {
        let epochMilliseconds = Date.now();
        let { user_id, user_name, data: videoData, timestamp } = msg.content;
        
        // Defensive logging: check for undefined fields
        if (!user_id || !user_name || !videoData || !timestamp) {
          console.warn(`⚠️ Missing expected fields in msg_type 15 (video). Available keys:`, Object.keys(msg.content));
          console.warn(`⚠️ Values: user_id=${user_id}, user_name=${user_name}, data=${videoData ? 'present' : 'missing'}, timestamp=${timestamp}`);
        }
        
        let buffer = Buffer.from(videoData, 'base64');
        //console.log(`Processing video data for user ${user_name} (ID: ${user_id}), buffer size: ${buffer.length} bytes`);
        saveRawVideoAdvance(buffer, user_name, timestamp, streamId); // Primary method
      }
      // Handle sharescreen data
      if (msg.msg_type === 16 && msg.content && msg.content.data) {
        let epochMilliseconds = Date.now();
        let { user_id, user_name, data: imgData, timestamp } = msg.content;
        
        // Defensive logging: check for undefined fields
        if (!user_id || !user_name || !imgData || !timestamp) {
          console.warn(`⚠️ Missing expected fields in msg_type 16 (screenshare). Available keys:`, Object.keys(msg.content));
          console.warn(`⚠️ Values: user_id=${user_id}, user_name=${user_name}, data=${imgData ? 'present' : 'missing'}, timestamp=${timestamp}`);
        }
        
        // Call handleShareData to process and save unique screen share images
        handleShareData(imgData, user_id, Date.now(), streamId).catch(err => console.error('Error handling share data:', err));
      }
      // Handle transcript data
      if (msg.msg_type === 17 && msg.content && msg.content.data) {
        let { user_id, user_name, data, timestamp, start_time, end_time, language, attribute } = msg.content;
        
        if (!user_id || !user_name || !data || !timestamp) {
          console.warn(`⚠️ Missing expected fields in msg_type 17 (transcript). Available keys:`, Object.keys(msg.content));
          console.warn(`⚠️ Values: user_id=${user_id}, user_name=${user_name}, data=${data}, timestamp=${timestamp}`);
        }
        
        //console.log(`Processing transcript: "${data}" from user ${user_name} (ID: ${user_id})`);
        writeTranscriptToVtt(user_name, timestamp / 1000, data, safestreamId);

        const connData = activeConnections.get(streamId);
        const mUuid = connData ? connData.meetingUuid : '';
        scheduleAIProcessing(streamId, mUuid);
      }

       // Handle chat data
       if (msg.msg_type === 18 && msg.content && msg.content.data) {
         let { user_id, user_name, data, timestamp } = msg.content;
         
         // Defensive logging: check for undefined fields
         if (!user_id || !user_name || !data || !timestamp) {
           console.warn(`⚠️ Missing expected fields in msg_type 18 (chat). Available keys:`, Object.keys(msg.content));
           console.warn(`⚠️ Values: user_id=${user_id}, user_name=${user_name}, data=${data}, timestamp=${timestamp}`);
         }
         
         console.log(`Chat message from ${user_name} (ID: ${user_id}): "${data}"`);
         const safeStreamId = sanitizeFileName(streamId);
         fs.mkdirSync(`recordings/${safeStreamId}`, { recursive: true });
         const chatLine = `[${new Date(timestamp).toISOString()}] ${user_name}: ${data}\n`;
         fs.appendFileSync(`recordings/${safeStreamId}/chat.txt`, chatLine);
       }
    } catch (err) {
      console.error('Error processing media message:', err);
    }
  });

  mediaWs.on('error', (err) => {
    console.error('Media socket error:', err);
  });

  mediaWs.on('close', () => {
    console.log('Media socket closed');
    if (activeConnections.has(streamId)) {
      delete activeConnections.get(streamId).media;
    }
  });
}



// Start the server and listen on the specified port
const server = app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
  console.log(`Webhook endpoint available at http://localhost:${port}${WEBHOOK_PATH}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  server.close(() => {
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully...');
  server.close(() => {
    process.exit(0);
  });
});
