import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
  Audio,
  staticFile,
} from "remotion";

// WhatsApp Dark Mode colors
const COLORS = {
  bg: "#0b141a",
  headerBg: "#1f2c34",
  outgoing: "#005c4b",
  incoming: "#1f2c34",
  text: "#e9edef",
  textSecondary: "#8696a0",
  green: "#00a884",
  blue: "#53bdeb",
  linkText: "#53bdeb",
};

// iPhone Frame - 4:5 aspect ratio for X feed
const IPhoneFrame = ({ children }: { children: React.ReactNode }) => {
  return (
    <div
      style={{
        width: 620,
        height: 1260,
        background: "#000",
        borderRadius: 55,
        padding: 12,
        boxShadow: "0 40px 120px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.06)",
        position: "relative",
      }}
    >
      {/* Dynamic Island */}
      <div
        style={{
          position: "absolute",
          top: 20,
          left: "50%",
          transform: "translateX(-50%)",
          width: 125,
          height: 35,
          background: "#000",
          borderRadius: 20,
          zIndex: 100,
        }}
      />
      {/* Screen */}
      <div
        style={{
          width: "100%",
          height: "100%",
          background: COLORS.bg,
          borderRadius: 45,
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {children}
      </div>
      {/* Home indicator */}
      <div
        style={{
          position: "absolute",
          bottom: 18,
          left: "50%",
          transform: "translateX(-50%)",
          width: 140,
          height: 5,
          background: "rgba(255,255,255,0.25)",
          borderRadius: 3,
        }}
      />
    </div>
  );
};

// Chat header - 2x fonts for 4:5
const ChatHeader = () => (
  <div
    style={{
      background: COLORS.headerBg,
      padding: "58px 20px 20px 20px",
      display: "flex",
      alignItems: "center",
      gap: 14,
    }}
  >
    <div style={{ color: COLORS.blue, fontSize: 44, fontWeight: 300 }}>‹</div>
    <div
      style={{
        width: 60,
        height: 60,
        borderRadius: "50%",
        background: "linear-gradient(135deg, #128C7E, #25D366)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: 36,
      }}
    >
      🐡
    </div>
    <div style={{ flex: 1 }}>
      <div style={{ color: COLORS.text, fontSize: 32, fontWeight: 600 }}>Pokey 🐡</div>
      <div style={{ color: COLORS.textSecondary, fontSize: 22 }}>online</div>
    </div>
    <div style={{ display: "flex", gap: 24, color: COLORS.textSecondary, fontSize: 32 }}>
      <span>📹</span>
      <span>📞</span>
    </div>
  </div>
);

// Message bubble - 2x fonts for 4:5
const Message = ({
  text,
  isOutgoing,
  time,
  delay = 0,
  showCheck = true,
}: {
  text: string;
  isOutgoing: boolean;
  time: string;
  delay?: number;
  showCheck?: boolean;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 15, stiffness: 150 },
  });

  const scale = interpolate(progress, [0, 1], [0.3, 1]);
  const opacity = interpolate(progress, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
  const translateY = interpolate(progress, [0, 1], [20, 0]);

  if (frame < delay) return null;

  // Process text for code blocks and bold
  const renderText = (t: string) => {
    const parts = t.split(/(`[^`]+`)/g);
    return parts.map((part, i) => {
      if (part.startsWith("`") && part.endsWith("`")) {
        return (
          <span
            key={i}
            style={{
              background: "rgba(0,0,0,0.35)",
              padding: "4px 10px",
              borderRadius: 6,
              fontFamily: "SF Mono, Monaco, monospace",
              fontSize: "0.88em",
            }}
          >
            {part.slice(1, -1)}
          </span>
        );
      }
      const boldParts = part.split(/(\*\*[^*]+\*\*)/g);
      return boldParts.map((bp, j) => {
        if (bp.startsWith("**") && bp.endsWith("**")) {
          return <strong key={`${i}-${j}`}>{bp.slice(2, -2)}</strong>;
        }
        return bp;
      });
    });
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isOutgoing ? "flex-end" : "flex-start",
        padding: "6px 16px",
        transform: `scale(${scale}) translateY(${translateY}px)`,
        opacity,
        transformOrigin: isOutgoing ? "bottom right" : "bottom left",
      }}
    >
      <div
        style={{
          background: isOutgoing ? COLORS.outgoing : COLORS.incoming,
          borderRadius: 18,
          padding: "14px 16px",
          maxWidth: "88%",
          boxShadow: "0 1px 2px rgba(0,0,0,0.2)",
        }}
      >
        {!isOutgoing && (
          <div style={{ color: COLORS.green, fontSize: 28, marginBottom: 6 }}>[🐡]</div>
        )}
        <div
          style={{
            color: COLORS.text,
            fontSize: 34,
            lineHeight: 1.35,
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          {renderText(text)}
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            alignItems: "center",
            gap: 6,
            marginTop: 8,
          }}
        >
          <span style={{ color: COLORS.textSecondary, fontSize: 22 }}>{time}</span>
          {isOutgoing && showCheck && (
            <span style={{ color: COLORS.blue, fontSize: 24 }}>✓✓</span>
          )}
        </div>
      </div>
    </div>
  );
};

// Typing indicator - 2x for 4:5
const TypingIndicator = ({ delay = 0, duration = 60 }: { delay?: number; duration?: number }) => {
  const frame = useCurrentFrame();

  if (frame < delay || frame > delay + duration) return null;

  const bounce1 = Math.sin((frame - delay) * 0.5) * 5;
  const bounce2 = Math.sin((frame - delay) * 0.5 + 1) * 5;
  const bounce3 = Math.sin((frame - delay) * 0.5 + 2) * 5;

  const opacity = interpolate(
    frame - delay,
    [0, 8, duration - 8, duration],
    [0, 1, 1, 0],
    { extrapolateRight: "clamp" }
  );

  return (
    <div style={{ display: "flex", justifyContent: "flex-start", padding: "6px 16px", opacity }}>
      <div
        style={{
          background: COLORS.incoming,
          borderRadius: 18,
          padding: "20px 26px",
          display: "flex",
          gap: 8,
        }}
      >
        <div
          style={{
            width: 14,
            height: 14,
            borderRadius: "50%",
            background: COLORS.textSecondary,
            transform: `translateY(${bounce1}px)`,
          }}
        />
        <div
          style={{
            width: 14,
            height: 14,
            borderRadius: "50%",
            background: COLORS.textSecondary,
            transform: `translateY(${bounce2}px)`,
          }}
        />
        <div
          style={{
            width: 14,
            height: 14,
            borderRadius: "50%",
            background: COLORS.textSecondary,
            transform: `translateY(${bounce3}px)`,
          }}
        />
      </div>
    </div>
  );
};

// Chat messages with auto-scroll
const ChatMessages = () => {
  const frame = useCurrentFrame();
  
  // Scroll up as messages accumulate (start scrolling after message 3)
  const scrollStart = 220;
  const scrollAmount = interpolate(
    frame,
    [scrollStart, scrollStart + 60, 340, 400, 440, 500],
    [0, 80, 80, 200, 200, 320],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        paddingTop: 12,
        paddingBottom: 50,
        gap: 5,
        overflowY: "hidden",
        position: "relative",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 5,
          transform: `translateY(-${scrollAmount}px)`,
          transition: "transform 0.3s ease-out",
        }}
      >
        {/* Dan asks to save as skill */}
        <Message
          text="Can we save this as a template so I can easily create similar videos in the future?"
          isOutgoing={true}
          time="9:18 AM"
          delay={20}
          showCheck={true}
        />

        {/* Pokey typing */}
        <TypingIndicator delay={80} duration={50} />

        {/* Pokey responds */}
        <Message
          text="Great question! Let me create a reusable skill for WhatsApp videos..."
          isOutgoing={false}
          time="9:18 AM"
          delay={130}
        />

        {/* Pokey typing again */}
        <TypingIndicator delay={190} duration={55} />

        {/* Success message */}
        <Message
          text={`✅ **Skill saved!**

\`~/clawd/skills/whatsapp-video/\`

Includes template, docs, and render script. Just tell me what conversation to show and I'll generate the video.`}
          isOutgoing={false}
          time="9:19 AM"
          delay={245}
        />

        {/* Dan's follow-up */}
        <Message
          text="How do I share this skill with others? 🤔"
          isOutgoing={true}
          time="9:21 AM"
          delay={340}
          showCheck={true}
        />

        {/* Pokey typing */}
        <TypingIndicator delay={400} duration={40} />

        {/* Pokey's answer */}
        <Message
          text="Publish it to ClawdHub! 🚀"
          isOutgoing={false}
          time="9:21 AM"
          delay={440}
        />
      </div>
    </div>
  );
};

// End card - scaled for 4:5
const EndCard = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 12 } });
  const opacity = interpolate(frame, [0, 20], [0, 1]);

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(180deg, #075e54 0%, #128c7e 50%, #25d366 100%)",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div style={{ textAlign: "center", transform: `scale(${scale})`, opacity }}>
        <div style={{ fontSize: 80, marginBottom: 25 }}>🧩</div>
        <div
          style={{
            color: "white",
            fontSize: 42,
            fontWeight: "bold",
            marginBottom: 20,
            textShadow: "0 4px 20px rgba(0,0,0,0.3)",
          }}
        >
          Skill Created
        </div>
        <div style={{ color: "rgba(255,255,255,0.95)", fontSize: 24, marginBottom: 10, lineHeight: 1.4 }}>
          Reusable WhatsApp video template
        </div>
        <div style={{ color: "rgba(255,255,255,0.95)", fontSize: 24, marginBottom: 35, lineHeight: 1.4 }}>
          saved to Clawdbot skills
        </div>
        <div style={{ color: "rgba(255,255,255,0.7)", fontSize: 22, marginTop: 20 }}>
          @danpeguine
        </div>
        <div style={{ color: "rgba(255,255,255,0.6)", fontSize: 18, marginTop: 8 }}>
          clawdbot.com
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Main chat screen
const ChatScreen = () => {
  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(180deg, #0f1a2e 0%, #162447 50%, #1f4068 100%)",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div>
        <IPhoneFrame>
          {/* Background pattern */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              opacity: 0.04,
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M20 20v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            }}
          />

          {/* Header */}
          <ChatHeader />

          {/* Chat messages container with auto-scroll */}
          <ChatMessages />
        </IPhoneFrame>
      </div>

      {/* Sound effects */}
      <Sequence from={20}>
        <Audio src={staticFile("sounds/pop.mp3")} startFrom={0} volume={0.6} />
      </Sequence>
      <Sequence from={130}>
        <Audio src={staticFile("sounds/pop.mp3")} startFrom={0} volume={0.5} />
      </Sequence>
      <Sequence from={245}>
        <Audio src={staticFile("sounds/pop.mp3")} startFrom={0} volume={0.6} />
      </Sequence>
      <Sequence from={340}>
        <Audio src={staticFile("sounds/send.mp3")} startFrom={0} volume={0.5} />
      </Sequence>
      <Sequence from={440}>
        <Audio src={staticFile("sounds/pop.mp3")} startFrom={0} volume={0.6} />
      </Sequence>
    </AbsoluteFill>
  );
};

// Main composition
export const WhatsAppDemo = () => {
  return (
    <AbsoluteFill>
      {/* Chat only - no outro */}
      <ChatScreen />
    </AbsoluteFill>
  );
};
