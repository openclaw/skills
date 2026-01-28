import { existsSync, mkdirSync, readFileSync, writeFileSync, mkdtempSync, rmSync, renameSync, unlinkSync, } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { completeSimple } from "@mariozechner/pi-ai";
import { EdgeTTS } from "node-edge-tts";
import { normalizeChannelId } from "../channels/plugins/index.js";
import { logVerbose } from "../globals.js";
import { isVoiceCompatibleAudio } from "../media/audio.js";
import { CONFIG_DIR, resolveUserPath } from "../utils.js";
import { getApiKeyForModel, requireApiKey } from "../agents/model-auth.js";
import { buildModelAliasIndex, resolveDefaultModelForAgent, resolveModelRefFromString, } from "../agents/model-selection.js";
import { resolveModel } from "../agents/pi-embedded-runner/model.js";
const DEFAULT_TIMEOUT_MS = 30_000;
const DEFAULT_TTS_MAX_LENGTH = 1500;
const DEFAULT_TTS_SUMMARIZE = true;
const DEFAULT_MAX_TEXT_LENGTH = 4000;
const TEMP_FILE_CLEANUP_DELAY_MS = 5 * 60 * 1000; // 5 minutes
const DEFAULT_ELEVENLABS_BASE_URL = "https://api.elevenlabs.io";
const DEFAULT_ELEVENLABS_VOICE_ID = "pMsXgVXv3BLzUgSXRplE";
const DEFAULT_ELEVENLABS_MODEL_ID = "eleven_multilingual_v2";
const DEFAULT_OPENAI_MODEL = "gpt-4o-mini-tts";
const DEFAULT_OPENAI_VOICE = "alloy";
const DEFAULT_EDGE_VOICE = "en-US-MichelleNeural";
const DEFAULT_EDGE_LANG = "en-US";
const DEFAULT_EDGE_OUTPUT_FORMAT = "audio-24khz-48kbitrate-mono-mp3";
const DEFAULT_ELEVENLABS_VOICE_SETTINGS = {
    stability: 0.5,
    similarityBoost: 0.75,
    style: 0.0,
    useSpeakerBoost: true,
    speed: 1.0,
};
const TELEGRAM_OUTPUT = {
    openai: "opus",
    // ElevenLabs output formats use codec_sample_rate_bitrate naming.
    // Opus @ 48kHz/64kbps is a good voice-note tradeoff for Telegram.
    elevenlabs: "opus_48000_64",
    extension: ".opus",
    voiceCompatible: true,
};
const DEFAULT_OUTPUT = {
    openai: "mp3",
    elevenlabs: "mp3_44100_128",
    extension: ".mp3",
    voiceCompatible: false,
};
const TELEPHONY_OUTPUT = {
    openai: { format: "pcm", sampleRate: 24000 },
    elevenlabs: { format: "pcm_22050", sampleRate: 22050 },
};
const TTS_AUTO_MODES = new Set(["off", "always", "inbound", "tagged"]);
let lastTtsAttempt;
export function normalizeTtsAutoMode(value) {
    if (typeof value !== "string")
        return undefined;
    const normalized = value.trim().toLowerCase();
    if (TTS_AUTO_MODES.has(normalized)) {
        return normalized;
    }
    return undefined;
}
function resolveModelOverridePolicy(overrides) {
    const enabled = overrides?.enabled ?? true;
    if (!enabled) {
        return {
            enabled: false,
            allowText: false,
            allowProvider: false,
            allowVoice: false,
            allowModelId: false,
            allowVoiceSettings: false,
            allowNormalization: false,
            allowSeed: false,
        };
    }
    const allow = (value) => value ?? true;
    return {
        enabled: true,
        allowText: allow(overrides?.allowText),
        allowProvider: allow(overrides?.allowProvider),
        allowVoice: allow(overrides?.allowVoice),
        allowModelId: allow(overrides?.allowModelId),
        allowVoiceSettings: allow(overrides?.allowVoiceSettings),
        allowNormalization: allow(overrides?.allowNormalization),
        allowSeed: allow(overrides?.allowSeed),
    };
}
export function resolveTtsConfig(cfg) {
    const raw = cfg.messages?.tts ?? {};
    const providerSource = raw.provider ? "config" : "default";
    const edgeOutputFormat = raw.edge?.outputFormat?.trim();
    const auto = normalizeTtsAutoMode(raw.auto) ?? (raw.enabled ? "always" : "off");
    return {
        auto,
        mode: raw.mode ?? "final",
        provider: raw.provider ?? "edge",
        providerSource,
        summaryModel: raw.summaryModel?.trim() || undefined,
        modelOverrides: resolveModelOverridePolicy(raw.modelOverrides),
        elevenlabs: {
            apiKey: raw.elevenlabs?.apiKey,
            baseUrl: raw.elevenlabs?.baseUrl?.trim() || DEFAULT_ELEVENLABS_BASE_URL,
            voiceId: raw.elevenlabs?.voiceId ?? DEFAULT_ELEVENLABS_VOICE_ID,
            modelId: raw.elevenlabs?.modelId ?? DEFAULT_ELEVENLABS_MODEL_ID,
            seed: raw.elevenlabs?.seed,
            applyTextNormalization: raw.elevenlabs?.applyTextNormalization,
            languageCode: raw.elevenlabs?.languageCode,
            voiceSettings: {
                stability: raw.elevenlabs?.voiceSettings?.stability ?? DEFAULT_ELEVENLABS_VOICE_SETTINGS.stability,
                similarityBoost: raw.elevenlabs?.voiceSettings?.similarityBoost ??
                    DEFAULT_ELEVENLABS_VOICE_SETTINGS.similarityBoost,
                style: raw.elevenlabs?.voiceSettings?.style ?? DEFAULT_ELEVENLABS_VOICE_SETTINGS.style,
                useSpeakerBoost: raw.elevenlabs?.voiceSettings?.useSpeakerBoost ??
                    DEFAULT_ELEVENLABS_VOICE_SETTINGS.useSpeakerBoost,
                speed: raw.elevenlabs?.voiceSettings?.speed ?? DEFAULT_ELEVENLABS_VOICE_SETTINGS.speed,
            },
        },
        openai: {
            apiKey: raw.openai?.apiKey,
            model: raw.openai?.model ?? DEFAULT_OPENAI_MODEL,
            voice: raw.openai?.voice ?? DEFAULT_OPENAI_VOICE,
        },
        edge: {
            enabled: raw.edge?.enabled ?? true,
            voice: raw.edge?.voice?.trim() || DEFAULT_EDGE_VOICE,
            lang: raw.edge?.lang?.trim() || DEFAULT_EDGE_LANG,
            outputFormat: edgeOutputFormat || DEFAULT_EDGE_OUTPUT_FORMAT,
            outputFormatConfigured: Boolean(edgeOutputFormat),
            pitch: raw.edge?.pitch?.trim() || undefined,
            rate: raw.edge?.rate?.trim() || undefined,
            volume: raw.edge?.volume?.trim() || undefined,
            saveSubtitles: raw.edge?.saveSubtitles ?? false,
            proxy: raw.edge?.proxy?.trim() || undefined,
            timeoutMs: raw.edge?.timeoutMs,
        },
        prefsPath: raw.prefsPath,
        maxTextLength: raw.maxTextLength ?? DEFAULT_MAX_TEXT_LENGTH,
        timeoutMs: raw.timeoutMs ?? DEFAULT_TIMEOUT_MS,
    };
}
export function resolveTtsPrefsPath(config) {
    if (config.prefsPath?.trim())
        return resolveUserPath(config.prefsPath.trim());
    const envPath = process.env.CLAWDBOT_TTS_PREFS?.trim();
    if (envPath)
        return resolveUserPath(envPath);
    return path.join(CONFIG_DIR, "settings", "tts.json");
}
function resolveTtsAutoModeFromPrefs(prefs) {
    const auto = normalizeTtsAutoMode(prefs.tts?.auto);
    if (auto)
        return auto;
    if (typeof prefs.tts?.enabled === "boolean") {
        return prefs.tts.enabled ? "always" : "off";
    }
    return undefined;
}
export function resolveTtsAutoMode(params) {
    const sessionAuto = normalizeTtsAutoMode(params.sessionAuto);
    if (sessionAuto)
        return sessionAuto;
    const prefsAuto = resolveTtsAutoModeFromPrefs(readPrefs(params.prefsPath));
    if (prefsAuto)
        return prefsAuto;
    return params.config.auto;
}
export function buildTtsSystemPromptHint(cfg) {
    const config = resolveTtsConfig(cfg);
    const prefsPath = resolveTtsPrefsPath(config);
    const autoMode = resolveTtsAutoMode({ config, prefsPath });
    if (autoMode === "off")
        return undefined;
    const maxLength = getTtsMaxLength(prefsPath);
    const summarize = isSummarizationEnabled(prefsPath) ? "on" : "off";
    const autoHint = autoMode === "inbound"
        ? "Only use TTS when the user's last message includes audio/voice."
        : autoMode === "tagged"
            ? "Only use TTS when you include [[tts]] or [[tts:text]] tags."
            : undefined;
    return [
        "Voice (TTS) is enabled.",
        autoHint,
        `Keep spoken text ≤${maxLength} chars to avoid auto-summary (summary ${summarize}).`,
        "Use [[tts:...]] and optional [[tts:text]]...[[/tts:text]] to control voice/expressiveness.",
    ]
        .filter(Boolean)
        .join("\n");
}
function readPrefs(prefsPath) {
    try {
        if (!existsSync(prefsPath))
            return {};
        return JSON.parse(readFileSync(prefsPath, "utf8"));
    }
    catch {
        return {};
    }
}
function atomicWriteFileSync(filePath, content) {
    const tmpPath = `${filePath}.tmp.${Date.now()}.${Math.random().toString(36).slice(2)}`;
    writeFileSync(tmpPath, content);
    try {
        renameSync(tmpPath, filePath);
    }
    catch (err) {
        try {
            unlinkSync(tmpPath);
        }
        catch {
            // ignore
        }
        throw err;
    }
}
function updatePrefs(prefsPath, update) {
    const prefs = readPrefs(prefsPath);
    update(prefs);
    mkdirSync(path.dirname(prefsPath), { recursive: true });
    atomicWriteFileSync(prefsPath, JSON.stringify(prefs, null, 2));
}
export function isTtsEnabled(config, prefsPath, sessionAuto) {
    return resolveTtsAutoMode({ config, prefsPath, sessionAuto }) !== "off";
}
export function setTtsAutoMode(prefsPath, mode) {
    updatePrefs(prefsPath, (prefs) => {
        const next = { ...prefs.tts };
        delete next.enabled;
        next.auto = mode;
        prefs.tts = next;
    });
}
export function setTtsEnabled(prefsPath, enabled) {
    setTtsAutoMode(prefsPath, enabled ? "always" : "off");
}
export function getTtsProvider(config, prefsPath) {
    const prefs = readPrefs(prefsPath);
    if (prefs.tts?.provider)
        return prefs.tts.provider;
    if (config.providerSource === "config")
        return config.provider;
    if (resolveTtsApiKey(config, "openai"))
        return "openai";
    if (resolveTtsApiKey(config, "elevenlabs"))
        return "elevenlabs";
    return "edge";
}
export function setTtsProvider(prefsPath, provider) {
    updatePrefs(prefsPath, (prefs) => {
        prefs.tts = { ...prefs.tts, provider };
    });
}
export function getTtsMaxLength(prefsPath) {
    const prefs = readPrefs(prefsPath);
    return prefs.tts?.maxLength ?? DEFAULT_TTS_MAX_LENGTH;
}
export function setTtsMaxLength(prefsPath, maxLength) {
    updatePrefs(prefsPath, (prefs) => {
        prefs.tts = { ...prefs.tts, maxLength };
    });
}
export function isSummarizationEnabled(prefsPath) {
    const prefs = readPrefs(prefsPath);
    return prefs.tts?.summarize ?? DEFAULT_TTS_SUMMARIZE;
}
export function setSummarizationEnabled(prefsPath, enabled) {
    updatePrefs(prefsPath, (prefs) => {
        prefs.tts = { ...prefs.tts, summarize: enabled };
    });
}
export function getLastTtsAttempt() {
    return lastTtsAttempt;
}
export function setLastTtsAttempt(entry) {
    lastTtsAttempt = entry;
}
function resolveOutputFormat(channelId) {
    if (channelId === "telegram")
        return TELEGRAM_OUTPUT;
    return DEFAULT_OUTPUT;
}
function resolveChannelId(channel) {
    return channel ? normalizeChannelId(channel) : null;
}
function resolveEdgeOutputFormat(config) {
    return config.edge.outputFormat;
}
export function resolveTtsApiKey(config, provider) {
    if (provider === "elevenlabs") {
        return config.elevenlabs.apiKey || process.env.ELEVENLABS_API_KEY || process.env.XI_API_KEY;
    }
    if (provider === "openai") {
        return config.openai.apiKey || process.env.OPENAI_API_KEY;
    }
    return undefined;
}
export const TTS_PROVIDERS = ["openai", "elevenlabs", "edge"];
export function resolveTtsProviderOrder(primary) {
    return [primary, ...TTS_PROVIDERS.filter((provider) => provider !== primary)];
}
export function isTtsProviderConfigured(config, provider) {
    if (provider === "edge")
        return config.edge.enabled;
    return Boolean(resolveTtsApiKey(config, provider));
}
function isValidVoiceId(voiceId) {
    return /^[a-zA-Z0-9]{10,40}$/.test(voiceId);
}
function normalizeElevenLabsBaseUrl(baseUrl) {
    const trimmed = baseUrl.trim();
    if (!trimmed)
        return DEFAULT_ELEVENLABS_BASE_URL;
    return trimmed.replace(/\/+$/, "");
}
function requireInRange(value, min, max, label) {
    if (!Number.isFinite(value) || value < min || value > max) {
        throw new Error(`${label} must be between ${min} and ${max}`);
    }
}
function assertElevenLabsVoiceSettings(settings) {
    requireInRange(settings.stability, 0, 1, "stability");
    requireInRange(settings.similarityBoost, 0, 1, "similarityBoost");
    requireInRange(settings.style, 0, 1, "style");
    requireInRange(settings.speed, 0.5, 2, "speed");
}
function normalizeLanguageCode(code) {
    const trimmed = code?.trim();
    if (!trimmed)
        return undefined;
    const normalized = trimmed.toLowerCase();
    if (!/^[a-z]{2}$/.test(normalized)) {
        throw new Error("languageCode must be a 2-letter ISO 639-1 code (e.g. en, de, fr)");
    }
    return normalized;
}
function normalizeApplyTextNormalization(mode) {
    const trimmed = mode?.trim();
    if (!trimmed)
        return undefined;
    const normalized = trimmed.toLowerCase();
    if (normalized === "auto" || normalized === "on" || normalized === "off")
        return normalized;
    throw new Error("applyTextNormalization must be one of: auto, on, off");
}
function normalizeSeed(seed) {
    if (seed == null)
        return undefined;
    const next = Math.floor(seed);
    if (!Number.isFinite(next) || next < 0 || next > 4_294_967_295) {
        throw new Error("seed must be between 0 and 4294967295");
    }
    return next;
}
function parseBooleanValue(value) {
    const normalized = value.trim().toLowerCase();
    if (["true", "1", "yes", "on"].includes(normalized))
        return true;
    if (["false", "0", "no", "off"].includes(normalized))
        return false;
    return undefined;
}
function parseNumberValue(value) {
    const parsed = Number.parseFloat(value);
    return Number.isFinite(parsed) ? parsed : undefined;
}
function parseTtsDirectives(text, policy) {
    if (!policy.enabled) {
        return { cleanedText: text, overrides: {}, warnings: [], hasDirective: false };
    }
    const overrides = {};
    const warnings = [];
    let cleanedText = text;
    let hasDirective = false;
    const blockRegex = /\[\[tts:text\]\]([\s\S]*?)\[\[\/tts:text\]\]/gi;
    cleanedText = cleanedText.replace(blockRegex, (_match, inner) => {
        hasDirective = true;
        if (policy.allowText && overrides.ttsText == null) {
            overrides.ttsText = inner.trim();
        }
        return "";
    });
    const directiveRegex = /\[\[tts:([^\]]+)\]\]/gi;
    cleanedText = cleanedText.replace(directiveRegex, (_match, body) => {
        hasDirective = true;
        const tokens = body.split(/\s+/).filter(Boolean);
        for (const token of tokens) {
            const eqIndex = token.indexOf("=");
            if (eqIndex === -1)
                continue;
            const rawKey = token.slice(0, eqIndex).trim();
            const rawValue = token.slice(eqIndex + 1).trim();
            if (!rawKey || !rawValue)
                continue;
            const key = rawKey.toLowerCase();
            try {
                switch (key) {
                    case "provider":
                        if (!policy.allowProvider)
                            break;
                        if (rawValue === "openai" || rawValue === "elevenlabs" || rawValue === "edge") {
                            overrides.provider = rawValue;
                        }
                        else {
                            warnings.push(`unsupported provider "${rawValue}"`);
                        }
                        break;
                    case "voice":
                    case "openai_voice":
                    case "openaivoice":
                        if (!policy.allowVoice)
                            break;
                        if (isValidOpenAIVoice(rawValue)) {
                            overrides.openai = { ...overrides.openai, voice: rawValue };
                        }
                        else {
                            warnings.push(`invalid OpenAI voice "${rawValue}"`);
                        }
                        break;
                    case "voiceid":
                    case "voice_id":
                    case "elevenlabs_voice":
                    case "elevenlabsvoice":
                        if (!policy.allowVoice)
                            break;
                        if (isValidVoiceId(rawValue)) {
                            overrides.elevenlabs = { ...overrides.elevenlabs, voiceId: rawValue };
                        }
                        else {
                            warnings.push(`invalid ElevenLabs voiceId "${rawValue}"`);
                        }
                        break;
                    case "model":
                    case "modelid":
                    case "model_id":
                    case "elevenlabs_model":
                    case "elevenlabsmodel":
                    case "openai_model":
                    case "openaimodel":
                        if (!policy.allowModelId)
                            break;
                        if (isValidOpenAIModel(rawValue)) {
                            overrides.openai = { ...overrides.openai, model: rawValue };
                        }
                        else {
                            overrides.elevenlabs = { ...overrides.elevenlabs, modelId: rawValue };
                        }
                        break;
                    case "stability":
                        if (!policy.allowVoiceSettings)
                            break;
                        {
                            const value = parseNumberValue(rawValue);
                            if (value == null) {
                                warnings.push("invalid stability value");
                                break;
                            }
                            requireInRange(value, 0, 1, "stability");
                            overrides.elevenlabs = {
                                ...overrides.elevenlabs,
                                voiceSettings: { ...overrides.elevenlabs?.voiceSettings, stability: value },
                            };
                        }
                        break;
                    case "similarity":
                    case "similarityboost":
                    case "similarity_boost":
                        if (!policy.allowVoiceSettings)
                            break;
                        {
                            const value = parseNumberValue(rawValue);
                            if (value == null) {
                                warnings.push("invalid similarityBoost value");
                                break;
                            }
                            requireInRange(value, 0, 1, "similarityBoost");
                            overrides.elevenlabs = {
                                ...overrides.elevenlabs,
                                voiceSettings: { ...overrides.elevenlabs?.voiceSettings, similarityBoost: value },
                            };
                        }
                        break;
                    case "style":
                        if (!policy.allowVoiceSettings)
                            break;
                        {
                            const value = parseNumberValue(rawValue);
                            if (value == null) {
                                warnings.push("invalid style value");
                                break;
                            }
                            requireInRange(value, 0, 1, "style");
                            overrides.elevenlabs = {
                                ...overrides.elevenlabs,
                                voiceSettings: { ...overrides.elevenlabs?.voiceSettings, style: value },
                            };
                        }
                        break;
                    case "speed":
                        if (!policy.allowVoiceSettings)
                            break;
                        {
                            const value = parseNumberValue(rawValue);
                            if (value == null) {
                                warnings.push("invalid speed value");
                                break;
                            }
                            requireInRange(value, 0.5, 2, "speed");
                            overrides.elevenlabs = {
                                ...overrides.elevenlabs,
                                voiceSettings: { ...overrides.elevenlabs?.voiceSettings, speed: value },
                            };
                        }
                        break;
                    case "speakerboost":
                    case "speaker_boost":
                    case "usespeakerboost":
                    case "use_speaker_boost":
                        if (!policy.allowVoiceSettings)
                            break;
                        {
                            const value = parseBooleanValue(rawValue);
                            if (value == null) {
                                warnings.push("invalid useSpeakerBoost value");
                                break;
                            }
                            overrides.elevenlabs = {
                                ...overrides.elevenlabs,
                                voiceSettings: { ...overrides.elevenlabs?.voiceSettings, useSpeakerBoost: value },
                            };
                        }
                        break;
                    case "normalize":
                    case "applytextnormalization":
                    case "apply_text_normalization":
                        if (!policy.allowNormalization)
                            break;
                        overrides.elevenlabs = {
                            ...overrides.elevenlabs,
                            applyTextNormalization: normalizeApplyTextNormalization(rawValue),
                        };
                        break;
                    case "language":
                    case "languagecode":
                    case "language_code":
                        if (!policy.allowNormalization)
                            break;
                        overrides.elevenlabs = {
                            ...overrides.elevenlabs,
                            languageCode: normalizeLanguageCode(rawValue),
                        };
                        break;
                    case "seed":
                        if (!policy.allowSeed)
                            break;
                        overrides.elevenlabs = {
                            ...overrides.elevenlabs,
                            seed: normalizeSeed(Number.parseInt(rawValue, 10)),
                        };
                        break;
                    default:
                        break;
                }
            }
            catch (err) {
                warnings.push(err.message);
            }
        }
        return "";
    });
    return {
        cleanedText,
        ttsText: overrides.ttsText,
        hasDirective,
        overrides,
        warnings,
    };
}
export const OPENAI_TTS_MODELS = ["gpt-4o-mini-tts", "tts-1", "tts-1-hd"];
/**
 * Custom OpenAI-compatible TTS endpoint.
 * When set, model/voice validation is relaxed to allow non-OpenAI models.
 * Example: OPENAI_TTS_BASE_URL=http://localhost:8880/v1
 */
const OPENAI_TTS_BASE_URL = (process.env.OPENAI_TTS_BASE_URL?.trim() || "https://api.openai.com/v1").replace(/\/+$/, "");
const isCustomOpenAIEndpoint = OPENAI_TTS_BASE_URL !== "https://api.openai.com/v1";
export const OPENAI_TTS_VOICES = [
    "alloy",
    "ash",
    "coral",
    "echo",
    "fable",
    "onyx",
    "nova",
    "sage",
    "shimmer",
];
function isValidOpenAIModel(model) {
    // Allow any model when using custom endpoint (e.g., Kokoro, LocalAI)
    if (isCustomOpenAIEndpoint)
        return true;
    return OPENAI_TTS_MODELS.includes(model);
}
function isValidOpenAIVoice(voice) {
    // Allow any voice when using custom endpoint (e.g., Kokoro Chinese voices)
    if (isCustomOpenAIEndpoint)
        return true;
    return OPENAI_TTS_VOICES.includes(voice);
}
function resolveSummaryModelRef(cfg, config) {
    const defaultRef = resolveDefaultModelForAgent({ cfg });
    const override = config.summaryModel?.trim();
    if (!override)
        return { ref: defaultRef, source: "default" };
    const aliasIndex = buildModelAliasIndex({ cfg, defaultProvider: defaultRef.provider });
    const resolved = resolveModelRefFromString({
        raw: override,
        defaultProvider: defaultRef.provider,
        aliasIndex,
    });
    if (!resolved)
        return { ref: defaultRef, source: "default" };
    return { ref: resolved.ref, source: "summaryModel" };
}
function isTextContentBlock(block) {
    return block.type === "text";
}
async function summarizeText(params) {
    const { text, targetLength, cfg, config, timeoutMs } = params;
    if (targetLength < 100 || targetLength > 10_000) {
        throw new Error(`Invalid targetLength: ${targetLength}`);
    }
    const startTime = Date.now();
    const { ref } = resolveSummaryModelRef(cfg, config);
    const resolved = resolveModel(ref.provider, ref.model, undefined, cfg);
    if (!resolved.model) {
        throw new Error(resolved.error ?? `Unknown summary model: ${ref.provider}/${ref.model}`);
    }
    const apiKey = requireApiKey(await getApiKeyForModel({ model: resolved.model, cfg }), ref.provider);
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), timeoutMs);
        try {
            const res = await completeSimple(resolved.model, {
                messages: [
                    {
                        role: "user",
                        content: `You are an assistant that summarizes texts concisely while keeping the most important information. ` +
                            `Summarize the text to approximately ${targetLength} characters. Maintain the original tone and style. ` +
                            `Reply only with the summary, without additional explanations.\n\n` +
                            `<text_to_summarize>\n${text}\n</text_to_summarize>`,
                        timestamp: Date.now(),
                    },
                ],
            }, {
                apiKey,
                maxTokens: Math.ceil(targetLength / 2),
                temperature: 0.3,
                signal: controller.signal,
            });
            const summary = res.content
                .filter(isTextContentBlock)
                .map((block) => block.text.trim())
                .filter(Boolean)
                .join(" ")
                .trim();
            if (!summary) {
                throw new Error("No summary returned");
            }
            return {
                summary,
                latencyMs: Date.now() - startTime,
                inputLength: text.length,
                outputLength: summary.length,
            };
        }
        finally {
            clearTimeout(timeout);
        }
    }
    catch (err) {
        const error = err;
        if (error.name === "AbortError") {
            throw new Error("Summarization timed out");
        }
        throw err;
    }
}
function scheduleCleanup(tempDir, delayMs = TEMP_FILE_CLEANUP_DELAY_MS) {
    const timer = setTimeout(() => {
        try {
            rmSync(tempDir, { recursive: true, force: true });
        }
        catch {
            // ignore cleanup errors
        }
    }, delayMs);
    timer.unref();
}
async function elevenLabsTTS(params) {
    const { text, apiKey, baseUrl, voiceId, modelId, outputFormat, seed, applyTextNormalization, languageCode, voiceSettings, timeoutMs, } = params;
    if (!isValidVoiceId(voiceId)) {
        throw new Error("Invalid voiceId format");
    }
    assertElevenLabsVoiceSettings(voiceSettings);
    const normalizedLanguage = normalizeLanguageCode(languageCode);
    const normalizedNormalization = normalizeApplyTextNormalization(applyTextNormalization);
    const normalizedSeed = normalizeSeed(seed);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const url = new URL(`${normalizeElevenLabsBaseUrl(baseUrl)}/v1/text-to-speech/${voiceId}`);
        if (outputFormat) {
            url.searchParams.set("output_format", outputFormat);
        }
        const response = await fetch(url.toString(), {
            method: "POST",
            headers: {
                "xi-api-key": apiKey,
                "Content-Type": "application/json",
                Accept: "audio/mpeg",
            },
            body: JSON.stringify({
                text,
                model_id: modelId,
                seed: normalizedSeed,
                apply_text_normalization: normalizedNormalization,
                language_code: normalizedLanguage,
                voice_settings: {
                    stability: voiceSettings.stability,
                    similarity_boost: voiceSettings.similarityBoost,
                    style: voiceSettings.style,
                    use_speaker_boost: voiceSettings.useSpeakerBoost,
                    speed: voiceSettings.speed,
                },
            }),
            signal: controller.signal,
        });
        if (!response.ok) {
            throw new Error(`ElevenLabs API error (${response.status})`);
        }
        return Buffer.from(await response.arrayBuffer());
    }
    finally {
        clearTimeout(timeout);
    }
}
async function openaiTTS(params) {
    const { text, apiKey, model, voice, responseFormat, timeoutMs } = params;
    if (!isValidOpenAIModel(model)) {
        throw new Error(`Invalid model: ${model}`);
    }
    if (!isValidOpenAIVoice(voice)) {
        throw new Error(`Invalid voice: ${voice}`);
    }
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const response = await fetch(`${OPENAI_TTS_BASE_URL}/audio/speech`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${apiKey}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                model,
                input: text,
                voice,
                response_format: responseFormat,
            }),
            signal: controller.signal,
        });
        if (!response.ok) {
            throw new Error(`OpenAI TTS API error (${response.status})`);
        }
        return Buffer.from(await response.arrayBuffer());
    }
    finally {
        clearTimeout(timeout);
    }
}
function inferEdgeExtension(outputFormat) {
    const normalized = outputFormat.toLowerCase();
    if (normalized.includes("webm"))
        return ".webm";
    if (normalized.includes("ogg"))
        return ".ogg";
    if (normalized.includes("opus"))
        return ".opus";
    if (normalized.includes("wav") || normalized.includes("riff") || normalized.includes("pcm")) {
        return ".wav";
    }
    return ".mp3";
}
async function edgeTTS(params) {
    const { text, outputPath, config, timeoutMs } = params;
    const tts = new EdgeTTS({
        voice: config.voice,
        lang: config.lang,
        outputFormat: config.outputFormat,
        saveSubtitles: config.saveSubtitles,
        proxy: config.proxy,
        rate: config.rate,
        pitch: config.pitch,
        volume: config.volume,
        timeout: config.timeoutMs ?? timeoutMs,
    });
    await tts.ttsPromise(text, outputPath);
}
export async function textToSpeech(params) {
    const config = resolveTtsConfig(params.cfg);
    const prefsPath = params.prefsPath ?? resolveTtsPrefsPath(config);
    const channelId = resolveChannelId(params.channel);
    const output = resolveOutputFormat(channelId);
    console.log(`[TTS-SPEECH] entry: channel=${params.channel} channelId=${channelId} textLen=${params.text.length} maxLen=${config.maxTextLength}`);
    if (params.text.length > config.maxTextLength) {
        console.log(`[TTS-SPEECH] FAIL: text too long`);
        return {
            success: false,
            error: `Text too long (${params.text.length} chars, max ${config.maxTextLength})`,
        };
    }
    const userProvider = getTtsProvider(config, prefsPath);
    const overrideProvider = params.overrides?.provider;
    const provider = overrideProvider ?? userProvider;
    const providers = resolveTtsProviderOrder(provider);
    console.log(`[TTS-SPEECH] provider=${provider} userProvider=${userProvider} providers=${JSON.stringify(providers)} apiKey=${config.elevenlabs.apiKey ? "SET(" + config.elevenlabs.apiKey.slice(0, 8) + "...)" : "MISSING"}`);
    let lastError;
    for (const provider of providers) {
        const providerStart = Date.now();
        try {
            if (provider === "edge") {
                if (!config.edge.enabled) {
                    lastError = "edge: disabled";
                    continue;
                }
                const tempDir = mkdtempSync(path.join(tmpdir(), "tts-"));
                let edgeOutputFormat = resolveEdgeOutputFormat(config);
                const fallbackEdgeOutputFormat = edgeOutputFormat !== DEFAULT_EDGE_OUTPUT_FORMAT ? DEFAULT_EDGE_OUTPUT_FORMAT : undefined;
                const attemptEdgeTts = async (outputFormat) => {
                    const extension = inferEdgeExtension(outputFormat);
                    const audioPath = path.join(tempDir, `voice-${Date.now()}${extension}`);
                    await edgeTTS({
                        text: params.text,
                        outputPath: audioPath,
                        config: {
                            ...config.edge,
                            outputFormat,
                        },
                        timeoutMs: config.timeoutMs,
                    });
                    return { audioPath, outputFormat };
                };
                let edgeResult;
                try {
                    edgeResult = await attemptEdgeTts(edgeOutputFormat);
                }
                catch (err) {
                    if (fallbackEdgeOutputFormat && fallbackEdgeOutputFormat !== edgeOutputFormat) {
                        logVerbose(`TTS: Edge output ${edgeOutputFormat} failed; retrying with ${fallbackEdgeOutputFormat}.`);
                        edgeOutputFormat = fallbackEdgeOutputFormat;
                        try {
                            edgeResult = await attemptEdgeTts(edgeOutputFormat);
                        }
                        catch (fallbackErr) {
                            try {
                                rmSync(tempDir, { recursive: true, force: true });
                            }
                            catch {
                                // ignore cleanup errors
                            }
                            throw fallbackErr;
                        }
                    }
                    else {
                        try {
                            rmSync(tempDir, { recursive: true, force: true });
                        }
                        catch {
                            // ignore cleanup errors
                        }
                        throw err;
                    }
                }
                scheduleCleanup(tempDir);
                const voiceCompatible = isVoiceCompatibleAudio({ fileName: edgeResult.audioPath });
                return {
                    success: true,
                    audioPath: edgeResult.audioPath,
                    latencyMs: Date.now() - providerStart,
                    provider,
                    outputFormat: edgeResult.outputFormat,
                    voiceCompatible,
                };
            }
            const apiKey = resolveTtsApiKey(config, provider);
            if (!apiKey) {
                lastError = `No API key for ${provider}`;
                continue;
            }
            let audioBuffer;
            if (provider === "elevenlabs") {
                const voiceIdOverride = params.overrides?.elevenlabs?.voiceId;
                const modelIdOverride = params.overrides?.elevenlabs?.modelId;
                const voiceSettings = {
                    ...config.elevenlabs.voiceSettings,
                    ...params.overrides?.elevenlabs?.voiceSettings,
                };
                const seedOverride = params.overrides?.elevenlabs?.seed;
                const normalizationOverride = params.overrides?.elevenlabs?.applyTextNormalization;
                const languageOverride = params.overrides?.elevenlabs?.languageCode;
                audioBuffer = await elevenLabsTTS({
                    text: params.text,
                    apiKey,
                    baseUrl: config.elevenlabs.baseUrl,
                    voiceId: voiceIdOverride ?? config.elevenlabs.voiceId,
                    modelId: modelIdOverride ?? config.elevenlabs.modelId,
                    outputFormat: output.elevenlabs,
                    seed: seedOverride ?? config.elevenlabs.seed,
                    applyTextNormalization: normalizationOverride ?? config.elevenlabs.applyTextNormalization,
                    languageCode: languageOverride ?? config.elevenlabs.languageCode,
                    voiceSettings,
                    timeoutMs: config.timeoutMs,
                });
            }
            else {
                const openaiModelOverride = params.overrides?.openai?.model;
                const openaiVoiceOverride = params.overrides?.openai?.voice;
                audioBuffer = await openaiTTS({
                    text: params.text,
                    apiKey,
                    model: openaiModelOverride ?? config.openai.model,
                    voice: openaiVoiceOverride ?? config.openai.voice,
                    responseFormat: output.openai,
                    timeoutMs: config.timeoutMs,
                });
            }
            const latencyMs = Date.now() - providerStart;
            const tempDir = mkdtempSync(path.join(tmpdir(), "tts-"));
            const audioPath = path.join(tempDir, `voice-${Date.now()}${output.extension}`);
            writeFileSync(audioPath, audioBuffer);
            scheduleCleanup(tempDir);
            return {
                success: true,
                audioPath,
                latencyMs,
                provider,
                outputFormat: provider === "openai" ? output.openai : output.elevenlabs,
                voiceCompatible: output.voiceCompatible,
            };
        }
        catch (err) {
            const error = err;
            if (error.name === "AbortError") {
                lastError = `${provider}: request timed out`;
            }
            else {
                lastError = `${provider}: ${error.message}`;
            }
        }
    }
    return {
        success: false,
        error: `TTS conversion failed: ${lastError || "no providers available"}`,
    };
}
export async function textToSpeechTelephony(params) {
    const config = resolveTtsConfig(params.cfg);
    const prefsPath = params.prefsPath ?? resolveTtsPrefsPath(config);
    if (params.text.length > config.maxTextLength) {
        return {
            success: false,
            error: `Text too long (${params.text.length} chars, max ${config.maxTextLength})`,
        };
    }
    const userProvider = getTtsProvider(config, prefsPath);
    const providers = resolveTtsProviderOrder(userProvider);
    let lastError;
    for (const provider of providers) {
        const providerStart = Date.now();
        try {
            if (provider === "edge") {
                lastError = "edge: unsupported for telephony";
                continue;
            }
            const apiKey = resolveTtsApiKey(config, provider);
            if (!apiKey) {
                lastError = `No API key for ${provider}`;
                continue;
            }
            if (provider === "elevenlabs") {
                const output = TELEPHONY_OUTPUT.elevenlabs;
                const audioBuffer = await elevenLabsTTS({
                    text: params.text,
                    apiKey,
                    baseUrl: config.elevenlabs.baseUrl,
                    voiceId: config.elevenlabs.voiceId,
                    modelId: config.elevenlabs.modelId,
                    outputFormat: output.format,
                    seed: config.elevenlabs.seed,
                    applyTextNormalization: config.elevenlabs.applyTextNormalization,
                    languageCode: config.elevenlabs.languageCode,
                    voiceSettings: config.elevenlabs.voiceSettings,
                    timeoutMs: config.timeoutMs,
                });
                return {
                    success: true,
                    audioBuffer,
                    latencyMs: Date.now() - providerStart,
                    provider,
                    outputFormat: output.format,
                    sampleRate: output.sampleRate,
                };
            }
            const output = TELEPHONY_OUTPUT.openai;
            const audioBuffer = await openaiTTS({
                text: params.text,
                apiKey,
                model: config.openai.model,
                voice: config.openai.voice,
                responseFormat: output.format,
                timeoutMs: config.timeoutMs,
            });
            return {
                success: true,
                audioBuffer,
                latencyMs: Date.now() - providerStart,
                provider,
                outputFormat: output.format,
                sampleRate: output.sampleRate,
            };
        }
        catch (err) {
            const error = err;
            if (error.name === "AbortError") {
                lastError = `${provider}: request timed out`;
            }
            else {
                lastError = `${provider}: ${error.message}`;
            }
        }
    }
    return {
        success: false,
        error: `TTS conversion failed: ${lastError || "no providers available"}`,
    };
}
export async function maybeApplyTtsToPayload(params) {
    const config = resolveTtsConfig(params.cfg);
    const prefsPath = resolveTtsPrefsPath(config);
    const autoMode = resolveTtsAutoMode({
        config,
        prefsPath,
        sessionAuto: params.ttsAuto,
    });
    console.log(`[TTS-APPLY] entry: autoMode=${autoMode} kind=${params.kind} inboundAudio=${params.inboundAudio} channel=${params.channel} provider=${config.provider} apiKey=${config.elevenlabs.apiKey ? "SET" : "MISSING"}`);
    if (autoMode === "off") {
        console.log(`[TTS-APPLY] SKIP: autoMode=off`);
        return params.payload;
    }
    const text = params.payload.text ?? "";
    const directives = parseTtsDirectives(text, config.modelOverrides);
    if (directives.warnings.length > 0) {
        logVerbose(`TTS: ignored directive overrides (${directives.warnings.join("; ")})`);
    }
    const cleanedText = directives.cleanedText;
    const trimmedCleaned = cleanedText.trim();
    const visibleText = trimmedCleaned.length > 0 ? trimmedCleaned : "";
    const ttsText = directives.ttsText?.trim() || visibleText;
    const nextPayload = visibleText === text.trim()
        ? params.payload
        : {
            ...params.payload,
            text: visibleText.length > 0 ? visibleText : undefined,
        };
    if (autoMode === "tagged" && !directives.hasDirective) {
        console.log(`[TTS-APPLY] SKIP: tagged mode, no directive`);
        return nextPayload;
    }
    if (autoMode === "inbound" && params.inboundAudio !== true) {
        console.log(`[TTS-APPLY] SKIP: inbound mode, inboundAudio=${params.inboundAudio}`);
        return nextPayload;
    }
    const mode = config.mode ?? "final";
    if (mode === "final" && params.kind && params.kind !== "final") {
        console.log(`[TTS-APPLY] SKIP: mode=final but kind=${params.kind}`);
        return nextPayload;
    }
    if (!ttsText.trim()) {
        console.log(`[TTS-APPLY] SKIP: empty ttsText`);
        return nextPayload;
    }
    if (params.payload.mediaUrl || (params.payload.mediaUrls?.length ?? 0) > 0) {
        console.log(`[TTS-APPLY] SKIP: payload already has mediaUrl`);
        return nextPayload;
    }
    if (text.includes("MEDIA:")) {
        console.log(`[TTS-APPLY] SKIP: text contains MEDIA:`);
        return nextPayload;
    }
    if (ttsText.trim().length < 10) {
        console.log(`[TTS-APPLY] SKIP: ttsText too short (${ttsText.trim().length} < 10)`);
        return nextPayload;
    }
    console.log(`[TTS-APPLY] PASSED all checks, proceeding to textToSpeech. textLen=${ttsText.trim().length}`);
    const maxLength = getTtsMaxLength(prefsPath);
    let textForAudio = ttsText.trim();
    let wasSummarized = false;
    if (textForAudio.length > maxLength) {
        if (!isSummarizationEnabled(prefsPath)) {
            logVerbose(`TTS: skipping long text (${textForAudio.length} > ${maxLength}), summarization disabled.`);
            return nextPayload;
        }
        try {
            const summary = await summarizeText({
                text: textForAudio,
                targetLength: maxLength,
                cfg: params.cfg,
                config,
                timeoutMs: config.timeoutMs,
            });
            textForAudio = summary.summary;
            wasSummarized = true;
            if (textForAudio.length > config.maxTextLength) {
                logVerbose(`TTS: summary exceeded hard limit (${textForAudio.length} > ${config.maxTextLength}); truncating.`);
                textForAudio = `${textForAudio.slice(0, config.maxTextLength - 3)}...`;
            }
        }
        catch (err) {
            const error = err;
            logVerbose(`TTS: summarization failed: ${error.message}`);
            return nextPayload;
        }
    }
    const ttsStart = Date.now();
    console.log(`[TTS-APPLY] calling textToSpeech with ${textForAudio.length} chars, channel=${params.channel}`);
    const result = await textToSpeech({
        text: textForAudio,
        cfg: params.cfg,
        prefsPath,
        channel: params.channel,
        overrides: directives.overrides,
    });
    console.log(`[TTS-APPLY] textToSpeech result: success=${result.success} audioPath=${result.audioPath ?? "none"} error=${result.error ?? "none"} provider=${result.provider ?? "none"} latency=${result.latencyMs ?? "?"}ms`);
    if (result.success && result.audioPath) {
        lastTtsAttempt = {
            timestamp: Date.now(),
            success: true,
            textLength: text.length,
            summarized: wasSummarized,
            provider: result.provider,
            latencyMs: result.latencyMs,
        };
        const channelId = resolveChannelId(params.channel);
        const shouldVoice = channelId === "telegram" && result.voiceCompatible === true;
        console.log(`[TTS-APPLY] SUCCESS: audioPath=${result.audioPath} shouldVoice=${shouldVoice}`);
        return {
            ...nextPayload,
            mediaUrl: result.audioPath,
            audioAsVoice: shouldVoice || params.payload.audioAsVoice,
        };
    }
    lastTtsAttempt = {
        timestamp: Date.now(),
        success: false,
        textLength: text.length,
        summarized: wasSummarized,
        error: result.error,
    };
    console.log(`[TTS-APPLY] FAILED: ${result.error ?? "unknown"}`);
    const latency = Date.now() - ttsStart;
    logVerbose(`TTS: conversion failed after ${latency}ms (${result.error ?? "unknown"}).`);
    return nextPayload;
}
export const _test = {
    isValidVoiceId,
    isValidOpenAIVoice,
    isValidOpenAIModel,
    OPENAI_TTS_MODELS,
    OPENAI_TTS_VOICES,
    parseTtsDirectives,
    resolveModelOverridePolicy,
    summarizeText,
    resolveOutputFormat,
    resolveEdgeOutputFormat,
};
