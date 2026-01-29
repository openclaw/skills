#!/usr/bin/env tsx

import { promises as fs } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import dotenv from 'dotenv';
import { ElevenLabsClient } from 'elevenlabs';
import Anthropic from '@anthropic-ai/sdk';

const execFileAsync = promisify(execFile);

dotenv.config({ path: path.resolve(__dirname, '.env') });

// ---------- config -----------------------------------------------------------

// CLI arguments
const args = process.argv.slice(2);
const RAW_FLAG = args.includes('--raw');
const INPUT = args.find(arg => !arg.startsWith('--')) ?? 'https://www.youtube.com/watch?v=fdQtJ6TD5fE';
const BASE_TRANSCRIPTS_DIR = path.join(require('os').homedir(), 'Documents', 'transcripts');
const TMP_AUDIO = path.join(tmpdir(), `yt-audio-${Date.now()}.m4a`);

// supported audio/video extensions for local files
const MEDIA_EXTENSIONS = ['.mp3', '.m4a', '.wav', '.ogg', '.flac', '.mp4', '.mkv', '.webm', '.mov', '.avi'];

const eleven = new ElevenLabsClient({
    apiKey:
        process.env.ELEVEN_LABS_API_KEY ??
        (() => {
            throw new Error('Missing ELEVEN_LABS_API_KEY in .env');
        })(),
});

const anthropic = new Anthropic({
    apiKey:
        process.env.ANTHROPIC_API_KEY ??
        (() => {
            throw new Error('Missing ANTHROPIC_API_KEY in .env');
        })(),
});

// ---------- types ------------------------------------------------------------

interface Word {
    text: string;
    start: number;
    end: number;
    type: 'word' | 'spacing' | 'punctuation' | string;
    speaker_id: string;
}

// From ElevenLabs API response
interface SpeechToTextWordResponse {
    text: string;
    start?: number;
    end?: number;
    type?: 'word' | 'spacing' | 'punctuation' | string;
    speaker_id?: string;
}

interface ThemeClassification {
    primaryTheme: string;
    subTheme: string;
    folderName: string;
    confidence: 'high' | 'medium' | 'low';
    summary: string;
}

interface TranscriptMetadata {
    sourceUrl: string;  // youtube URL or file:// path
    title: string;
    date: string;
    theme: ThemeClassification;
    language?: string;
    confidence?: number;
    wordsDetected?: number;
}

/**
 * Rich source metadata from yt-dlp or local file analysis
 */
interface SourceMetadata {
    title: string;
    channel?: string;
    uploader?: string;
    duration?: number;
    duration_string?: string;
    description?: string;
    like_count?: number;
    comment_count?: number;
    view_count?: number;
    thumbnail?: string;
    upload_date?: string;  // YYYYMMDD format from yt-dlp, or ISO for local
    webpage_url?: string;
    extractor?: string;  // e.g., 'youtube', 'instagram', 'local'
}

interface FolderNode {
    name: string;
    path: string;
    type: 'folder' | 'transcript';
    children?: FolderNode[];
    metadata?: TranscriptMetadata;
}

interface OrganizationPlan {
    newTranscriptPath: string;
    reasoning: string;
    confidence: 'high' | 'medium' | 'low';
}

// ---------- helpers ----------------------------------------------------------

/**
 * Check if input is a URL or local file
 */
function isUrl(input: string): boolean {
    return input.startsWith('http://') || input.startsWith('https://');
}

/**
 * Check if URL is a YouTube video
 */
function isYouTubeUrl(url: string): boolean {
    return url.includes('youtube.com') || url.includes('youtu.be');
}

/**
 * Check if URL is an Instagram Reel
 */
function isInstagramUrl(url: string): boolean {
    return url.includes('instagram.com/reel') || url.includes('instagram.com/p/');
}

/**
 * Check if file is a video that needs audio extraction
 */
function isVideoFile(filePath: string): boolean {
    const ext = path.extname(filePath).toLowerCase();
    return ['.mp4', '.mkv', '.webm', '.mov', '.avi'].includes(ext);
}

/**
 * Get title from local file path
 */
function getTitleFromPath(filePath: string): string {
    const basename = path.basename(filePath, path.extname(filePath));
    return basename
        .replace(/[<>:"/\\|?*]/g, '-')
        .replace(/\s+/g, '-')
        .toLowerCase()
        .slice(0, 100);
}

/**
 * Extract audio from video file using ffmpeg
 */
async function extractAudioFromVideo(videoPath: string, destAudio: string): Promise<void> {
    try {
        await execFileAsync('ffmpeg', [
            '-i', videoPath,
            '-vn',                    // no video
            '-acodec', 'aac',         // audio codec
            '-b:a', '192k',           // audio bitrate
            '-y',                     // overwrite output
            destAudio,
        ]);
    } catch (error: any) {
        if (error.code === 'ENOENT') {
            throw new Error(
                'ffmpeg not found. Install it with:\n' +
                '  macOS: brew install ffmpeg\n' +
                '  Linux: apt install ffmpeg\n' +
                '  Windows: winget install ffmpeg'
            );
        }
        throw error;
    }
}

/**
 * Read the entire library structure from ~/Documents/transcripts/
 */
async function readLibraryStructure(): Promise<FolderNode> {
    const baseDir = BASE_TRANSCRIPTS_DIR;

    // Check if base directory exists
    try {
        await fs.access(baseDir);
    } catch {
        // Directory doesn't exist yet, return empty structure
        return {
            name: 'transcripts',
            path: baseDir,
            type: 'folder',
            children: [],
        };
    }

    async function readDir(dirPath: string, relativePath: string = ''): Promise<FolderNode[]> {
        const entries = await fs.readdir(dirPath, { withFileTypes: true });
        const nodes: FolderNode[] = [];

        for (const entry of entries) {
            const fullPath = path.join(dirPath, entry.name);
            const relPath = relativePath ? `${relativePath}/${entry.name}` : entry.name;

            if (entry.isDirectory()) {
                // Check if this is a transcript folder (contains metadata.json)
                const metadataPath = path.join(fullPath, 'metadata.json');
                let metadata: TranscriptMetadata | undefined;

                try {
                    const metadataContent = await fs.readFile(metadataPath, 'utf8');
                    metadata = JSON.parse(metadataContent);
                } catch {
                    // No metadata, it's a category folder
                }

                if (metadata) {
                    // This is a transcript folder
                    nodes.push({
                        name: entry.name,
                        path: relPath,
                        type: 'transcript',
                        metadata,
                    });
                } else {
                    // This is a category folder, recurse
                    const children = await readDir(fullPath, relPath);
                    nodes.push({
                        name: entry.name,
                        path: relPath,
                        type: 'folder',
                        children,
                    });
                }
            }
        }

        return nodes;
    }

    const children = await readDir(baseDir);
    return {
        name: 'transcripts',
        path: baseDir,
        type: 'folder',
        children,
    };
}

/**
 * Convert folder tree to a compact string representation for Claude
 */
function folderTreeToString(node: FolderNode, indent: string = ''): string {
    const lines: string[] = [];

    if (node.type === 'transcript' && node.metadata) {
        lines.push(`${indent}📄 ${node.name}`);
        lines.push(`${indent}   Summary: ${node.metadata.theme.summary}`);
        lines.push(`${indent}   Theme: ${node.metadata.theme.primaryTheme} > ${node.metadata.theme.subTheme}`);
    } else if (node.type === 'folder') {
        if (indent) lines.push(`${indent}📁 ${node.name}/`);
        if (node.children) {
            for (const child of node.children) {
                lines.push(...folderTreeToString(child, indent + '  ').split('\n').filter(Boolean));
            }
        }
    }

    return lines.join('\n');
}

/**
 * Estimate token count (conservative: ~4 chars per token)
 */
function estimateTokens(text: string): number {
    return Math.ceil(text.length / 4);
}

/**
 * Truncate transcript to fit within token limit
 * Strategy: Take beginning, middle, and end samples for better theme detection
 */
function truncateTranscript(text: string, maxTokens: number = 150000): string {
    const estimated = estimateTokens(text);

    if (estimated <= maxTokens) {
        return text;
    }

    // Take samples from beginning, middle, and end
    const targetChars = maxTokens * 4;
    const chunkSize = Math.floor(targetChars / 3);

    const beginning = text.slice(0, chunkSize);
    const middle = text.slice(
        Math.floor(text.length / 2 - chunkSize / 2),
        Math.floor(text.length / 2 + chunkSize / 2)
    );
    const end = text.slice(-chunkSize);

    return `${beginning}\n\n[... middle section ...]\n\n${middle}\n\n[... later section ...]\n\n${end}`;
}

/**
 * Classify transcript and organize within existing library structure
 */
async function classifyAndOrganize(
    transcript: string,
    videoUrl: string,
    videoTitle: string,
    libraryStructure: FolderNode
): Promise<OrganizationPlan> {
    const estimatedTokens = estimateTokens(transcript);
    console.log(`📊 Estimated tokens: ${estimatedTokens.toLocaleString()}`);

    const processedTranscript = truncateTranscript(transcript);
    const folderTreeString = folderTreeToString(libraryStructure);

    const hasExistingTranscripts = libraryStructure.children && libraryStructure.children.length > 0;

    const prompt = hasExistingTranscripts
        ? `You are maintaining a knowledge library of audio/video transcripts.

SOURCE INFORMATION:
URL: ${videoUrl}
Title: ${videoTitle}

CURRENT LIBRARY STRUCTURE:
${folderTreeString || '(Empty - this will be the first transcript)'}

NEW TRANSCRIPT TO ORGANIZE:
${processedTranscript}

YOUR TASK:
1. Analyze the new transcript's content and main themes
2. Review the existing library structure
3. Decide the optimal SINGLE-LEVEL category folder for this transcript

DECISION CRITERIA:
- Use existing folders when semantically appropriate (similar content/theme)
- Create new categories when the content doesn't fit existing ones
- Use kebab-case for folder names
- Keep categories broad enough to group related content but specific enough to be meaningful
- IMPORTANT: Use only ONE level of categorization (e.g., "ai-podcasts" not "technology/ai/podcasts")

Respond with a JSON object (no markdown code blocks):
{
  "newTranscriptPath": "category-name",
  "reasoning": "Explain why this category fits the content",
  "confidence": "high/medium/low"
}`
        : `You are creating a knowledge library of audio/video transcripts.

SOURCE INFORMATION:
URL: ${videoUrl}
Title: ${videoTitle}

TRANSCRIPT:
${processedTranscript}

This is the FIRST transcript in the library. Create an initial folder structure that:
- Uses a SINGLE level of categorization
- Is specific enough to be useful but not over-categorized
- Uses kebab-case for folder names
- Sets a good foundation for future organization
- Example: "ai-podcasts" or "business-interviews" (NOT "technology/ai/podcasts")

Respond with a JSON object (no markdown code blocks):
{
  "newTranscriptPath": "category-name",
  "reasoning": "Explain why you chose this category",
  "confidence": "high/medium/low"
}`;

    const message = await anthropic.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 2048,
        messages: [
            {
                role: 'user',
                content: prompt,
            },
        ],
    });

    const content = message.content[0];
    if (content.type !== 'text') {
        throw new Error('Unexpected response type from Claude');
    }

    // Parse JSON response
    const result = JSON.parse(content.text) as OrganizationPlan;
    return result;
}


/**
 * Sanitize a title string for use in file paths
 */
function sanitizeTitle(title: string): string {
    return title
        .replace(/[<>:"/\\|?*]/g, '-')
        .replace(/\s+/g, '-')
        .toLowerCase()
        .slice(0, 100);
}

/**
 * Get rich metadata from URL using yt-dlp --dump-json
 */
async function getUrlMetadata(url: string): Promise<SourceMetadata> {
    try {
        const args = ['--dump-json', '--no-download'];

        // Add YouTube-specific options only for YouTube URLs
        if (isYouTubeUrl(url)) {
            args.push('--extractor-args', 'youtube:player_client=android,web');
        }

        args.push(url);

        const { stdout } = await execFileAsync('yt-dlp', args, { maxBuffer: 10 * 1024 * 1024 });
        const data = JSON.parse(stdout);

        return {
            title: data.title || data.fulltitle || `video-${Date.now()}`,
            channel: data.channel || data.channel_name || undefined,
            uploader: data.uploader || data.uploader_id || undefined,
            duration: data.duration || undefined,
            duration_string: data.duration_string || undefined,
            description: data.description || undefined,
            like_count: data.like_count || undefined,
            comment_count: data.comment_count || undefined,
            view_count: data.view_count || undefined,
            thumbnail: data.thumbnail || (data.thumbnails && data.thumbnails.length > 0 ? data.thumbnails[data.thumbnails.length - 1]?.url : undefined),
            upload_date: data.upload_date || undefined,
            webpage_url: data.webpage_url || url,
            extractor: data.extractor_key || data.extractor || 'unknown',
        };
    } catch (error: any) {
        console.warn('⚠️  Failed to extract full metadata, falling back to basic info');
        // Fallback: try just getting the title
        try {
            const args = ['--get-title'];
            if (isYouTubeUrl(url)) {
                args.push('--extractor-args', 'youtube:player_client=android,web');
            }
            args.push(url);
            const { stdout } = await execFileAsync('yt-dlp', args);
            return {
                title: stdout.trim() || `video-${Date.now()}`,
                webpage_url: url,
                extractor: 'unknown',
            };
        } catch {
            return {
                title: `video-${Date.now()}`,
                webpage_url: url,
                extractor: 'unknown',
            };
        }
    }
}

/**
 * Get duration of a media file using ffprobe
 */
async function getFileDuration(filePath: string): Promise<{ duration?: number; duration_string?: string }> {
    try {
        const { stdout } = await execFileAsync('ffprobe', [
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            filePath,
        ]);
        const data = JSON.parse(stdout);
        const duration = parseFloat(data.format?.duration);
        if (!isNaN(duration)) {
            const hours = Math.floor(duration / 3600);
            const minutes = Math.floor((duration % 3600) / 60);
            const seconds = Math.floor(duration % 60);
            const duration_string = hours > 0
                ? `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
                : `${minutes}:${seconds.toString().padStart(2, '0')}`;
            return { duration, duration_string };
        }
        return {};
    } catch {
        return {};
    }
}

/**
 * Get metadata from a local file
 */
async function getLocalFileMetadata(filePath: string): Promise<SourceMetadata> {
    const basename = path.basename(filePath, path.extname(filePath));
    const title = basename;

    // Get file stats for modification date
    let upload_date: string | undefined;
    try {
        const stats = await fs.stat(filePath);
        // Format as YYYYMMDD to match yt-dlp format
        upload_date = stats.mtime.toISOString().split('T')[0].replace(/-/g, '');
    } catch {
        // Ignore stat errors
    }

    // Get duration via ffprobe
    const durationInfo = await getFileDuration(filePath);

    return {
        title,
        duration: durationInfo.duration,
        duration_string: durationInfo.duration_string,
        upload_date,
        webpage_url: `file://${path.resolve(filePath)}`,
        extractor: 'local',
        // These fields are not available for local files
        channel: undefined,
        uploader: undefined,
        description: undefined,
        like_count: undefined,
        comment_count: undefined,
        view_count: undefined,
        thumbnail: undefined,
    };
}

/**
 * Get video title from URL using yt-dlp (works for YouTube, Instagram, etc.)
 * @deprecated Use getUrlMetadata instead for richer metadata
 */
async function getVideoTitle(url: string): Promise<string> {
    const metadata = await getUrlMetadata(url);
    return sanitizeTitle(metadata.title);
}

async function downloadAudio(url: string, dest: string) {
    // Use yt-dlp for reliable video downloads from YouTube, Instagram, etc.
    // Install with: brew install yt-dlp (macOS) or pip install yt-dlp
    try {
        const args = [
            '--extract-audio',
            '--audio-format', 'm4a',
            '--audio-quality', '0', // best quality
            '--output', dest,
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ];

        // Add YouTube-specific options only for YouTube URLs
        if (isYouTubeUrl(url)) {
            args.push('--extractor-args', 'youtube:player_client=android,web');
        }

        args.push(url);

        await execFileAsync('yt-dlp', args);
    } catch (error: any) {
        if (error.code === 'ENOENT') {
            throw new Error(
                'yt-dlp not found. Install it with:\n' +
                '  macOS: brew install yt-dlp\n' +
                '  Linux: pip install yt-dlp\n' +
                '  Windows: winget install yt-dlp'
            );
        }
        throw error;
    }
}

async function transcribeAudio(filePath: string) {
    const audioBuffer = await fs.readFile(filePath);
    const audioBlob = new Blob([audioBuffer], { type: 'audio/m4a' });

    return eleven.speechToText.convert(
        {
            model_id: 'scribe_v1_experimental',
            file: audioBlob,
            diarize: true,
            tag_audio_events: true,
        },
        {
            timeoutInSeconds: 1200,
        }
    );
}

export function wordsToTranscript(words: Word[]): string {
    if (!words.length) return '';

    const lines: string[] = [];
    let currentSpeaker = words[0].speaker_id;
    let currentSentence: string[] = [];

    const flush = () => {
        if (currentSentence.length) {
            lines.push(`${currentSpeaker}: ${currentSentence.join(' ').replace(/\s+([.,!?;:])/g, '$1')}`);
            currentSentence = [];
        }
    };

    for (const token of words) {
        // Whenever the speaker changes, finish the previous line.
        if (token.speaker_id !== currentSpeaker) {
            flush();
            currentSpeaker = token.speaker_id;
        }

        // Skip spacing tokens (we'll insert our own spaces),
        // but keep words and punctuation.
        if (token.type !== 'spacing') {
            currentSentence.push(token.text);
        }
    }

    flush(); // push the last speaker's line
    return lines.join('\n');
}

// ---------- main -------------------------------------------------------------

async function main() {
    console.time('▶️  total');

    let audioPath: string;
    let title: string;
    let sourceUrl: string;
    let sourceMetadata: SourceMetadata;
    let needsCleanup = false;

    // branch: URL vs local file
    if (isUrl(INPUT)) {
        sourceUrl = INPUT;

        console.time('📹  video metadata');
        sourceMetadata = await getUrlMetadata(INPUT);
        title = sanitizeTitle(sourceMetadata.title);
        console.timeEnd('📹  video metadata');

        // Log extracted metadata
        console.log(`📊 Source: ${sourceMetadata.extractor}`);
        if (sourceMetadata.channel) console.log(`   Channel: ${sourceMetadata.channel}`);
        if (sourceMetadata.duration_string) console.log(`   Duration: ${sourceMetadata.duration_string}`);
        if (sourceMetadata.view_count) console.log(`   Views: ${sourceMetadata.view_count.toLocaleString()}`);

        console.time('⬇️  youtube');
        await downloadAudio(INPUT, TMP_AUDIO);
        console.timeEnd('⬇️  youtube');

        audioPath = TMP_AUDIO;
        needsCleanup = true;
    } else {
        // local file
        const resolvedPath = path.resolve(INPUT);

        // verify file exists
        try {
            await fs.access(resolvedPath);
        } catch {
            throw new Error(`File not found: ${resolvedPath}`);
        }

        // verify supported extension
        const ext = path.extname(resolvedPath).toLowerCase();
        if (!MEDIA_EXTENSIONS.includes(ext)) {
            throw new Error(`Unsupported file type: ${ext}\nSupported: ${MEDIA_EXTENSIONS.join(', ')}`);
        }

        sourceUrl = `file://${resolvedPath}`;
        
        console.time('📹  file metadata');
        sourceMetadata = await getLocalFileMetadata(resolvedPath);
        title = sanitizeTitle(sourceMetadata.title);
        console.timeEnd('📹  file metadata');

        console.log(`📁 Local file: ${resolvedPath}`);
        if (sourceMetadata.duration_string) console.log(`   Duration: ${sourceMetadata.duration_string}`);

        // extract audio if video file
        if (isVideoFile(resolvedPath)) {
            console.time('🎬  extracting audio');
            await extractAudioFromVideo(resolvedPath, TMP_AUDIO);
            console.timeEnd('🎬  extracting audio');
            audioPath = TMP_AUDIO;
            needsCleanup = true;
        } else {
            audioPath = resolvedPath;
        }
    }

    // transcribe
    console.time('📝  elevenlabs');
    const resp = await transcribeAudio(audioPath);
    console.timeEnd('📝  elevenlabs');

    // convert API response words to our Word interface
    const words: Word[] = resp.words.map((w) => ({
        text: w.text || '',
        start: w.start || 0,
        end: w.end || 0,
        type: w.type || 'word',
        speaker_id: w.speaker_id || 'unknown',
    }));
    const structuredTranscript = wordsToTranscript(words);

    // read existing library structure
    console.time('📚  reading library');
    const libraryStructure = await readLibraryStructure();
    console.timeEnd('📚  reading library');

    // classify and organize using Claude
    console.time('🤖  category classification');
    const plan = await classifyAndOrganize(structuredTranscript, sourceUrl, title, libraryStructure);
    console.timeEnd('🤖  category classification');

    // display organization plan
    console.log('\n📂 Category:');
    console.log(`  ${plan.newTranscriptPath}`);
    console.log(`  Confidence: ${plan.confidence}`);
    console.log(`  Reasoning: ${plan.reasoning}\n`);

    // create output directory
    const dateStr = new Date().toISOString().split('T')[0];
    const outputDir = path.join(BASE_TRANSCRIPTS_DIR, plan.newTranscriptPath, `${title}-${dateStr}`);
    await fs.mkdir(outputDir, { recursive: true });

    // define output file paths
    const transcriptOut = path.join(outputDir, 'transcript.txt');
    const metadataOut = path.join(outputDir, 'metadata.json');
    const rawJsonOut = path.join(outputDir, 'transcript-raw.json');

    // extract theme info for metadata
    const themeInfo: ThemeClassification = {
        primaryTheme: plan.newTranscriptPath || 'general',
        subTheme: title,
        folderName: plan.newTranscriptPath,
        confidence: plan.confidence,
        summary: plan.reasoning,
    };

    // Build complete metadata object with source info
    const completeMetadata = {
        // Source identification
        sourceUrl,
        title: sourceMetadata.title,  // Original title (not sanitized)
        date: dateStr,
        
        // Rich source metadata from yt-dlp or local file
        source: {
            extractor: sourceMetadata.extractor,
            channel: sourceMetadata.channel,
            uploader: sourceMetadata.uploader,
            duration: sourceMetadata.duration,
            duration_string: sourceMetadata.duration_string,
            description: sourceMetadata.description,
            like_count: sourceMetadata.like_count,
            comment_count: sourceMetadata.comment_count,
            view_count: sourceMetadata.view_count,
            thumbnail: sourceMetadata.thumbnail,
            upload_date: sourceMetadata.upload_date,
            webpage_url: sourceMetadata.webpage_url,
        },
        
        // Theme classification
        theme: themeInfo,
        
        // Transcription metadata
        transcription: {
            language: resp.language_code,
            confidence: resp.language_probability,
            wordsDetected: resp.words.length,
        },
    };

    // save files (default: 2 files, with --raw: 3 files)
    const writePromises = [
        fs.writeFile(transcriptOut, structuredTranscript, 'utf8'),
        fs.writeFile(metadataOut, JSON.stringify(completeMetadata, null, 2), 'utf8'),
    ];

    if (RAW_FLAG) {
        writePromises.push(fs.writeFile(rawJsonOut, JSON.stringify(resp, null, 2), 'utf8'));
    }

    await Promise.all(writePromises);

    console.log(`\n✅ Saved files to:\n  ${outputDir}\n`);
    const fileList = RAW_FLAG
        ? `Files:\n  • transcript.txt\n  • metadata.json\n  • transcript-raw.json`
        : `Files:\n  • transcript.txt\n  • metadata.json`;
    console.log(fileList);

    // cleanup temp audio if needed
    if (needsCleanup) {
        await fs.unlink(TMP_AUDIO);
    }

    console.timeEnd('▶️  total');
}

main().catch((err) => {
    console.error('❌  Fatal:', err);
    fs.unlink(TMP_AUDIO).catch(() => {});
    process.exitCode = 1;
});
