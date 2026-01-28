// handleShareData.js
import fs from 'fs';
import path from 'path';
import sharp from 'sharp';
import pixelmatch from 'pixelmatch';
import PDFDocument from 'pdfkit';
import { sanitizeFileName } from './tool.js';

// Session state: Map<meetingUuid, { uniqueFrameCounter: number, lastAcceptedBuffer: Buffer, uniqueFrames: Array<{filePath: string, timestamp: number}> }>
const meetingSessions = new Map();

async function handleShareData(shareData, user_id, timestamp, meetingUuid) {
    // Strip base64 prefix if present
    if (typeof shareData === 'string' && shareData.startsWith('data:')) {
        shareData = shareData.split(',')[1];
    }

    let buffer = Buffer.from(shareData, 'base64');

    // Sanitize meetingUuid for safe folder names using centralized function
    const safeMeetingUuid = sanitizeFileName(meetingUuid.toString()) || 'unknown';

    // Initialize session state if not exists
    if (!meetingSessions.has(meetingUuid)) {
        meetingSessions.set(meetingUuid, {
            uniqueFrameCounter: 0,
            lastAcceptedBuffer: null,  // RGBA buffer of last accepted frame
            uniqueFrames: []  // Array<{filePath: string, timestamp: number}>
        });
    }
    const session = meetingSessions.get(meetingUuid);

    // Detect file type
    let fileType = 'unknown';
    let fileExt = 'bin';

    const isJPEG = buffer.slice(0, 2).equals(Buffer.from([0xff, 0xd8]));
    const isJPEGEnd = buffer.slice(-2).equals(Buffer.from([0xff, 0xd9]));
    const isPNG = buffer.slice(0, 8).equals(
        Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])
    );
    const h264StartCodes = [
        Buffer.from([0x00, 0x00, 0x00, 0x01]),
        Buffer.from([0x00, 0x00, 0x01]),
    ];
    const isH264 = h264StartCodes.some(code => buffer.indexOf(code) === 0);

    // Only handle JPEG for screenshare
    if (!(isJPEG && isJPEGEnd)) {
        console.log('Only JPEG supported for screenshare uniqueness detection');
        return;
    }

    // Skip small frames
    const MIN_SIZE = 1000;
    if (buffer.length < MIN_SIZE) {
        console.warn(`⚠️ Skipping small JPEG (${buffer.length} bytes)`);
        return;
    }

    // Ensure processed folder exists
    const processedDir = path.resolve('recordings', safeMeetingUuid, 'processed', 'jpg');
    if (!fs.existsSync(processedDir)) {
        fs.mkdirSync(processedDir, { recursive: true });
    }

    // Decide if this frame is different enough
    let isDifferent = false;

    if (session.lastAcceptedBuffer === null) {
        // First frame, always accept
        isDifferent = true;
    } else {
        try {
            // Convert current buffer to RGBA
            const currentRGBA = await sharp(buffer).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
            const { width, height, channels } = currentRGBA.info;
            const currentBuffer = currentRGBA.data;

            // Last accepted is also RGBA with same dimensions (assuming screenshare consistent size)
            const lastBuffer = session.lastAcceptedBuffer;

            // Count differing pixels
            const totalPixels = width * height;
            const diffPixels = pixelmatch(currentBuffer, lastBuffer, null, width, height, { threshold: 0.1 }); // 0.1 threshold for pixel difference

            const diffRatio = diffPixels / totalPixels;
            if (diffRatio > 0.01) { // 1% threshold
                isDifferent = true;
            }
        } catch (error) {
            console.error('Error comparing images:', error);
            // On error, accept to be safe
            isDifferent = true;
        }
    }

    if (isDifferent) {
        // Increment counter and save
        session.uniqueFrameCounter++;
        const fileName = `unique_${session.uniqueFrameCounter}.jpg`;
        const filePath = path.join(processedDir, fileName);

        // Save JPEG
        fs.writeFileSync(filePath, buffer);

        // Update last accepted
        try {
            const rgba = await sharp(buffer).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
            session.lastAcceptedBuffer = rgba.data;
        } catch (error) {
            console.error('Error processing RGBA for next comparison:', error);
        }

        // Record unique frame
        session.uniqueFrames.push({ filePath, timestamp });

        console.log(`💾 Saved unique JPEG ${session.uniqueFrameCounter} to: ${filePath}  (${new Date(timestamp).toISOString()})`);
    } else {
        console.log(`⏭️ Skipping similar frame at ${new Date(timestamp).toISOString()}`);
    }
}

async function generatePDFAndText(streamId) {
    const session = meetingSessions.get(streamId);
    if (!session || session.uniqueFrames.length === 0) {
        console.log(`No unique frames for stream ${streamId}, skipping PDF generation`);
        return;
    }

    // Sanitize id for safe folder names (preserve + character as it's valid)
    const safeStreamId = sanitizeFileName(streamId.toString()) || 'unknown';

    console.log(`Generating PDF for stream ${safeStreamId} with ${session.uniqueFrames.length} frames`);

    const processedDir = path.resolve('recordings', safeStreamId, 'processed');
    const pdfPath = path.join(processedDir, 'screenshare.pdf');
    const txtPath = path.join(processedDir, 'frames.txt');

    // Create PDF with 16:9 aspect ratio (typical monitor) for optimal screen share display
    const MONITOR_ASPECT_RATIO = 16 / 9; // Standard 16:9 widescreen monitor ratio
    const pageWidthPoints = 595; // Standard width matching A4-ish dimensions
    const pageHeightPoints = pageWidthPoints / MONITOR_ASPECT_RATIO; // ≈ 333.75 points

    const doc = new PDFDocument({
        margins: { top: 0, bottom: 0, left: 0, right: 0 },
        size: [pageWidthPoints, pageHeightPoints] // Custom 16:9 page size
    });
    doc.pipe(fs.createWriteStream(pdfPath));

    console.log(`Creating PDF with 16:9 monitor aspect ratio: ${pageWidthPoints}x${pageHeightPoints} points`);

    for (const frame of session.uniqueFrames) {
        try {
            // Get image dimensions to fit properly
            const imageInfo = await sharp(frame.filePath).metadata();
            const imageRatio = imageInfo.width / imageInfo.height;
            const pageRatio = pageWidthPoints / pageHeightPoints;

            let width, height, x, y;

            if (imageRatio > pageRatio) {
                // Image is wider than page ratio, fit to width
                width = pageWidthPoints;
                height = width / imageRatio;
                x = 0;
                y = (pageHeightPoints - height) / 2; // Center vertically
            } else {
                // Image is taller than page ratio, fit to height
                height = pageHeightPoints;
                width = height * imageRatio;
                x = (pageWidthPoints - width) / 2; // Center horizontally
                y = 0;
            }

            // Add image to fill the page
            doc.image(frame.filePath, x, y, { width: width, height: height });

            // Only add a new page if there are more images
            if (session.uniqueFrames.indexOf(frame) < session.uniqueFrames.length - 1) {
                doc.addPage({ margins: { top: 0, bottom: 0, left: 0, right: 0 } });
            }
        } catch (error) {
            console.error(`Error adding image ${frame.filePath} to PDF:`, error);
        }
    }

    doc.end();

    // Create text file
    let txtContent = '';
    session.uniqueFrames.forEach((frame, index) => {
        const time = new Date(frame.timestamp).toISOString();
        txtContent += `Page ${index + 1}: ${time}\n`;
    });
    fs.writeFileSync(txtPath, txtContent);

    console.log(`PDF saved to: ${pdfPath}`);
    console.log(`Text file saved to: ${txtPath}`);

    // Clean up session
    meetingSessions.delete(streamId);
}

export { handleShareData, generatePDFAndText };
