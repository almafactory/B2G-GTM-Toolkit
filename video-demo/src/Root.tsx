import {Composition} from "remotion";
import {DemoVideo} from "./DemoVideo";
import "./styles.css";

export const Root = () => {
  return (
    <Composition
      id="GovBridgeDemo"
      component={DemoVideo}
      durationInFrames={5400}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
