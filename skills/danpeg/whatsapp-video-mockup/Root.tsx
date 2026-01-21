import "./index.css";
import { Composition } from "remotion";
import { MyComposition } from "./Composition";
import { WhatsAppDemo } from "./WhatsAppVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MyComp"
        component={MyComposition}
        durationInFrames={1350}
        fps={30}
        width={1280}
        height={720}
      />
      <Composition
        id="WhatsAppDemo"
        component={WhatsAppDemo}
        durationInFrames={540}
        fps={30}
        width={1080}
        height={1350}
      />
    </>
  );
};
