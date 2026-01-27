"""
Fliz Webhook Handler

A Flask server that receives webhook notifications from Fliz
when videos are completed or fail.

Installation:
    pip install flask

Usage:
    python webhook_handler.py
    
    # Or with custom port
    FLASK_PORT=8080 python webhook_handler.py

Configure your webhook URL in Fliz video creation:
    webhook_url: "https://your-domain.com/webhook/fliz"

Webhook Payload Examples:

Success:
{
    "event": "video.complete",
    "video_id": "uuid",
    "step": "complete",
    "url": "https://cdn.fliz.ai/videos/xxx.mp4",
    "title": "Video Title",
    "format": "size_16_9",
    "lang": "en"
}

Error:
{
    "event": "video.failed",
    "video_id": "uuid",
    "step": "failed",
    "error": {
        "code": "error_code",
        "message": "Error description"
    }
}
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store received webhooks (in-memory, use database in production)
webhook_history = []


@app.route('/webhook/fliz', methods=['POST'])
def handle_fliz_webhook():
    """
    Handle incoming Fliz webhook notifications.
    
    Fliz sends POST requests when:
    - Video generation completes successfully
    - Video generation fails
    """
    try:
        # Parse JSON payload
        payload = request.get_json()
        
        if not payload:
            logger.warning("Received empty webhook payload")
            return jsonify({"error": "Empty payload"}), 400
        
        # Extract key fields
        event = payload.get('event', 'unknown')
        video_id = payload.get('video_id')
        step = payload.get('step')
        
        # Log the webhook
        logger.info(f"Webhook received: {event} - Video: {video_id} - Step: {step}")
        
        # Store in history
        webhook_record = {
            "received_at": datetime.utcnow().isoformat(),
            "payload": payload
        }
        webhook_history.append(webhook_record)
        
        # Limit history size
        if len(webhook_history) > 100:
            webhook_history.pop(0)
        
        # Handle different events
        if step == 'complete':
            handle_video_complete(payload)
        elif 'failed' in step:
            handle_video_failed(payload)
        else:
            logger.info(f"Received status update: {step}")
        
        # Return success
        return jsonify({
            "status": "received",
            "video_id": video_id,
            "event": event
        }), 200
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        return jsonify({"error": "Invalid JSON"}), 400
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500


def handle_video_complete(payload):
    """
    Process completed video webhook.
    
    Args:
        payload: Webhook payload with video details
    """
    video_id = payload.get('video_id')
    video_url = payload.get('url')
    title = payload.get('title', 'Untitled')
    
    logger.info(f"✅ Video complete: {title}")
    logger.info(f"   ID: {video_id}")
    logger.info(f"   URL: {video_url}")
    
    # TODO: Add your custom logic here
    # Examples:
    # - Send notification email
    # - Update database record
    # - Trigger downstream workflow
    # - Post to social media
    # - Update CMS with video URL
    
    # Example: Save to file
    save_video_record(payload)


def handle_video_failed(payload):
    """
    Process failed video webhook.
    
    Args:
        payload: Webhook payload with error details
    """
    video_id = payload.get('video_id')
    step = payload.get('step')
    error = payload.get('error', {})
    
    error_code = error.get('code', 'unknown')
    error_message = error.get('message', 'No details')
    
    logger.error(f"❌ Video failed: {video_id}")
    logger.error(f"   Step: {step}")
    logger.error(f"   Error: {error_code} - {error_message}")
    
    # TODO: Add your custom error handling
    # Examples:
    # - Send alert to admin
    # - Log to error tracking service
    # - Retry video creation
    # - Update status in database


def save_video_record(payload):
    """Save video record to file (example implementation)."""
    filename = f"videos_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
    
    with open(filename, 'a') as f:
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            **payload
        }
        f.write(json.dumps(record) + '\n')
    
    logger.info(f"Saved to {filename}")


@app.route('/webhook/fliz/history', methods=['GET'])
def get_webhook_history():
    """Get recent webhook history (for debugging)."""
    return jsonify({
        "count": len(webhook_history),
        "webhooks": webhook_history[-20:]  # Last 20
    })


@app.route('/webhook/fliz/test', methods=['POST'])
def test_webhook():
    """Test endpoint to simulate a webhook."""
    test_payload = {
        "event": "video.complete",
        "video_id": "test-" + datetime.utcnow().strftime('%Y%m%d%H%M%S'),
        "step": "complete",
        "url": "https://example.com/test-video.mp4",
        "title": "Test Video",
        "format": "size_16_9",
        "lang": "en"
    }
    
    # Process like a real webhook
    webhook_history.append({
        "received_at": datetime.utcnow().isoformat(),
        "payload": test_payload,
        "test": True
    })
    
    return jsonify({
        "status": "test_received",
        "payload": test_payload
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })


# ============================================================
# Alternative: Express.js Webhook Handler (Node.js)
# ============================================================
"""
const express = require('express');
const app = express();
app.use(express.json());

app.post('/webhook/fliz', (req, res) => {
    const { event, video_id, step, url, error } = req.body;
    
    console.log(`Webhook: ${event} - Video: ${video_id} - Step: ${step}`);
    
    if (step === 'complete') {
        console.log(`✅ Video ready: ${url}`);
        // Handle completion
    } else if (step.includes('failed')) {
        console.log(`❌ Video failed: ${error?.message}`);
        // Handle failure
    }
    
    res.json({ status: 'received', video_id });
});

app.listen(3000, () => console.log('Webhook server on port 3000'));
"""


# ============================================================
# Alternative: Serverless (AWS Lambda)
# ============================================================
"""
import json

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    video_id = body.get('video_id')
    step = body.get('step')
    
    if step == 'complete':
        # Handle completion
        print(f"Video complete: {body.get('url')}")
    elif 'failed' in step:
        # Handle failure
        print(f"Video failed: {body.get('error')}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({'status': 'received', 'video_id': video_id})
    }
"""


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║             Fliz Webhook Handler                           ║
╠════════════════════════════════════════════════════════════╣
║  Webhook URL:  http://localhost:{port}/webhook/fliz          ║
║  History:      http://localhost:{port}/webhook/fliz/history  ║
║  Test:         POST http://localhost:{port}/webhook/fliz/test║
║  Health:       http://localhost:{port}/health                ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
