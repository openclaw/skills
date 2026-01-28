import { resolveSessionAgentId } from "../../agents/agent-scope.js";
import { loadSessionStore, resolveStorePath } from "../../config/sessions.js";
import { logVerbose } from "../../globals.js";
import { isDiagnosticsEnabled } from "../../infra/diagnostic-events.js";
import { logMessageProcessed, logMessageQueued, logSessionStateChange, } from "../../logging/diagnostic.js";
import { getGlobalHookRunner } from "../../plugins/hook-runner-global.js";
import { getReplyFromConfig } from "../reply.js";
import { formatAbortReplyText, tryFastAbortFromMessage } from "./abort.js";
import { shouldSkipDuplicateInbound } from "./inbound-dedupe.js";
import { isRoutableChannel, routeReply } from "./route-reply.js";
import { maybeApplyTtsToPayload, normalizeTtsAutoMode } from "../../tts/tts.js";
const AUDIO_PLACEHOLDER_RE = /^<media:audio>(\s*\([^)]*\))?$/i;
const AUDIO_HEADER_RE = /^\[Audio\b/i;
const normalizeMediaType = (value) => value.split(";")[0]?.trim().toLowerCase();
const isInboundAudioContext = (ctx) => {
    const rawTypes = [
        typeof ctx.MediaType === "string" ? ctx.MediaType : undefined,
        ...(Array.isArray(ctx.MediaTypes) ? ctx.MediaTypes : []),
    ].filter(Boolean);
    const types = rawTypes.map((type) => normalizeMediaType(type));
    if (types.some((type) => type === "audio" || type.startsWith("audio/")))
        return true;
    const body = typeof ctx.BodyForCommands === "string"
        ? ctx.BodyForCommands
        : typeof ctx.CommandBody === "string"
            ? ctx.CommandBody
            : typeof ctx.RawBody === "string"
                ? ctx.RawBody
                : typeof ctx.Body === "string"
                    ? ctx.Body
                    : "";
    const trimmed = body.trim();
    if (!trimmed)
        return false;
    if (AUDIO_PLACEHOLDER_RE.test(trimmed))
        return true;
    return AUDIO_HEADER_RE.test(trimmed);
};
const resolveSessionTtsAuto = (ctx, cfg) => {
    const targetSessionKey = ctx.CommandSource === "native" ? ctx.CommandTargetSessionKey?.trim() : undefined;
    const sessionKey = (targetSessionKey ?? ctx.SessionKey)?.trim();
    if (!sessionKey)
        return undefined;
    const agentId = resolveSessionAgentId({ sessionKey, config: cfg });
    const storePath = resolveStorePath(cfg.session?.store, { agentId });
    try {
        const store = loadSessionStore(storePath);
        const entry = store[sessionKey.toLowerCase()] ?? store[sessionKey];
        return normalizeTtsAutoMode(entry?.ttsAuto);
    }
    catch {
        return undefined;
    }
};
export async function dispatchReplyFromConfig(params) {
    const { ctx, cfg, dispatcher } = params;
    const diagnosticsEnabled = isDiagnosticsEnabled(cfg);
    const channel = String(ctx.Surface ?? ctx.Provider ?? "unknown").toLowerCase();
    const chatId = ctx.To ?? ctx.From;
    const messageId = ctx.MessageSid ?? ctx.MessageSidFirst ?? ctx.MessageSidLast;
    const sessionKey = ctx.SessionKey;
    const startTime = diagnosticsEnabled ? Date.now() : 0;
    const canTrackSession = diagnosticsEnabled && Boolean(sessionKey);
    const recordProcessed = (outcome, opts) => {
        if (!diagnosticsEnabled)
            return;
        logMessageProcessed({
            channel,
            chatId,
            messageId,
            sessionKey,
            durationMs: Date.now() - startTime,
            outcome,
            reason: opts?.reason,
            error: opts?.error,
        });
    };
    const markProcessing = () => {
        if (!canTrackSession || !sessionKey)
            return;
        logMessageQueued({ sessionKey, channel, source: "dispatch" });
        logSessionStateChange({
            sessionKey,
            state: "processing",
            reason: "message_start",
        });
    };
    const markIdle = (reason) => {
        if (!canTrackSession || !sessionKey)
            return;
        logSessionStateChange({
            sessionKey,
            state: "idle",
            reason,
        });
    };
    if (shouldSkipDuplicateInbound(ctx)) {
        recordProcessed("skipped", { reason: "duplicate" });
        return { queuedFinal: false, counts: dispatcher.getQueuedCounts() };
    }
    const inboundAudio = isInboundAudioContext(ctx);
    const sessionTtsAuto = resolveSessionTtsAuto(ctx, cfg);
    // Disable block streaming when TTS should produce audio for this response.
    // Block streaming drops final payloads (text already sent as blocks), but
    // TTS only fires on "final" kind payloads (default mode), so TTS never
    // triggers when block streaming is active.  Disabling block streaming for
    // TTS-eligible messages ensures the final reply carries text for synthesis.
    const ttsAutoResolved = normalizeTtsAutoMode(sessionTtsAuto) ?? normalizeTtsAutoMode(cfg.messages?.tts?.auto);
    const ttsWillFire = ttsAutoResolved === "always" || (ttsAutoResolved === "inbound" && inboundAudio);
    // DEBUG: TTS pipeline tracing
    console.log(`[TTS-DEBUG] inboundAudio=${inboundAudio} sessionTtsAuto=${sessionTtsAuto} ttsAutoResolved=${ttsAutoResolved} ttsWillFire=${ttsWillFire} MediaType=${ctx.MediaType} MediaTypes=${JSON.stringify(ctx.MediaTypes)} Body=${(ctx.Body ?? "").slice(0, 80)}`);
    const hookRunner = getGlobalHookRunner();
    if (hookRunner?.hasHooks("message_received")) {
        const timestamp = typeof ctx.Timestamp === "number" && Number.isFinite(ctx.Timestamp)
            ? ctx.Timestamp
            : undefined;
        const messageIdForHook = ctx.MessageSidFull ?? ctx.MessageSid ?? ctx.MessageSidFirst ?? ctx.MessageSidLast;
        const content = typeof ctx.BodyForCommands === "string"
            ? ctx.BodyForCommands
            : typeof ctx.RawBody === "string"
                ? ctx.RawBody
                : typeof ctx.Body === "string"
                    ? ctx.Body
                    : "";
        const channelId = (ctx.OriginatingChannel ?? ctx.Surface ?? ctx.Provider ?? "").toLowerCase();
        const conversationId = ctx.OriginatingTo ?? ctx.To ?? ctx.From ?? undefined;
        void hookRunner
            .runMessageReceived({
            from: ctx.From ?? "",
            content,
            timestamp,
            metadata: {
                to: ctx.To,
                provider: ctx.Provider,
                surface: ctx.Surface,
                threadId: ctx.MessageThreadId,
                originatingChannel: ctx.OriginatingChannel,
                originatingTo: ctx.OriginatingTo,
                messageId: messageIdForHook,
                senderId: ctx.SenderId,
                senderName: ctx.SenderName,
                senderUsername: ctx.SenderUsername,
                senderE164: ctx.SenderE164,
            },
        }, {
            channelId,
            accountId: ctx.AccountId,
            conversationId,
        })
            .catch((err) => {
            logVerbose(`dispatch-from-config: message_received hook failed: ${String(err)}`);
        });
    }
    // Check if we should route replies to originating channel instead of dispatcher.
    // Only route when the originating channel is DIFFERENT from the current surface.
    // This handles cross-provider routing (e.g., message from Telegram being processed
    // by a shared session that's currently on Slack) while preserving normal dispatcher
    // flow when the provider handles its own messages.
    //
    // Debug: `pnpm test src/auto-reply/reply/dispatch-from-config.test.ts`
    const originatingChannel = ctx.OriginatingChannel;
    const originatingTo = ctx.OriginatingTo;
    const currentSurface = (ctx.Surface ?? ctx.Provider)?.toLowerCase();
    const shouldRouteToOriginating = isRoutableChannel(originatingChannel) && originatingTo && originatingChannel !== currentSurface;
    const ttsChannel = shouldRouteToOriginating ? originatingChannel : currentSurface;
    /**
     * Helper to send a payload via route-reply (async).
     * Only used when actually routing to a different provider.
     * Note: Only called when shouldRouteToOriginating is true, so
     * originatingChannel and originatingTo are guaranteed to be defined.
     */
    const sendPayloadAsync = async (payload, abortSignal, mirror) => {
        // TypeScript doesn't narrow these from the shouldRouteToOriginating check,
        // but they're guaranteed non-null when this function is called.
        if (!originatingChannel || !originatingTo)
            return;
        if (abortSignal?.aborted)
            return;
        const result = await routeReply({
            payload,
            channel: originatingChannel,
            to: originatingTo,
            sessionKey: ctx.SessionKey,
            accountId: ctx.AccountId,
            threadId: ctx.MessageThreadId,
            cfg,
            abortSignal,
            mirror,
        });
        if (!result.ok) {
            logVerbose(`dispatch-from-config: route-reply failed: ${result.error ?? "unknown error"}`);
        }
    };
    markProcessing();
    try {
        const fastAbort = await tryFastAbortFromMessage({ ctx, cfg });
        if (fastAbort.handled) {
            const payload = {
                text: formatAbortReplyText(fastAbort.stoppedSubagents),
            };
            let queuedFinal = false;
            let routedFinalCount = 0;
            if (shouldRouteToOriginating && originatingChannel && originatingTo) {
                const result = await routeReply({
                    payload,
                    channel: originatingChannel,
                    to: originatingTo,
                    sessionKey: ctx.SessionKey,
                    accountId: ctx.AccountId,
                    threadId: ctx.MessageThreadId,
                    cfg,
                });
                queuedFinal = result.ok;
                if (result.ok)
                    routedFinalCount += 1;
                if (!result.ok) {
                    logVerbose(`dispatch-from-config: route-reply (abort) failed: ${result.error ?? "unknown error"}`);
                }
            }
            else {
                queuedFinal = dispatcher.sendFinalReply(payload);
            }
            await dispatcher.waitForIdle();
            const counts = dispatcher.getQueuedCounts();
            counts.final += routedFinalCount;
            recordProcessed("completed", { reason: "fast_abort" });
            markIdle("message_completed");
            return { queuedFinal, counts };
        }
        const replyResult = await (params.replyResolver ?? getReplyFromConfig)(ctx, {
            ...params.replyOptions,
            disableBlockStreaming: ttsWillFire || params.replyOptions?.disableBlockStreaming,
            // Don't provide onBlockReply when TTS will fire - we need the full final payload for synthesis
            onBlockReply: ttsWillFire ? undefined : (payload, context) => {
                const run = async () => {
                    const ttsPayload = await maybeApplyTtsToPayload({
                        payload,
                        cfg,
                        channel: ttsChannel,
                        kind: "block",
                        inboundAudio,
                        ttsAuto: sessionTtsAuto,
                    });
                    if (shouldRouteToOriginating) {
                        await sendPayloadAsync(ttsPayload, context?.abortSignal, false);
                    }
                    else {
                        dispatcher.sendBlockReply(ttsPayload);
                    }
                };
                return run();
            },
        }, cfg);
        const replies = replyResult ? (Array.isArray(replyResult) ? replyResult : [replyResult]) : [];
        let queuedFinal = false;
        let routedFinalCount = 0;
        for (const reply of replies) {
            const ttsReply = await maybeApplyTtsToPayload({
                payload: reply,
                cfg,
                channel: ttsChannel,
                kind: "final",
                inboundAudio,
                ttsAuto: sessionTtsAuto,
            });
            if (shouldRouteToOriginating && originatingChannel && originatingTo) {
                // Route final reply to originating channel.
                const result = await routeReply({
                    payload: ttsReply,
                    channel: originatingChannel,
                    to: originatingTo,
                    sessionKey: ctx.SessionKey,
                    accountId: ctx.AccountId,
                    threadId: ctx.MessageThreadId,
                    cfg,
                });
                if (!result.ok) {
                    logVerbose(`dispatch-from-config: route-reply (final) failed: ${result.error ?? "unknown error"}`);
                }
                queuedFinal = result.ok || queuedFinal;
                if (result.ok)
                    routedFinalCount += 1;
            }
            else {
                queuedFinal = dispatcher.sendFinalReply(ttsReply) || queuedFinal;
            }
        }
        await dispatcher.waitForIdle();
        const counts = dispatcher.getQueuedCounts();
        counts.final += routedFinalCount;
        recordProcessed("completed");
        markIdle("message_completed");
        return { queuedFinal, counts };
    }
    catch (err) {
        recordProcessed("error", { error: String(err) });
        markIdle("message_error");
        throw err;
    }
}
