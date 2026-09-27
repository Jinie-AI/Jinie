import { useEffect, useRef } from "react";
export default function AcceptedScreen({
  page,
  config,
}: {
  page: string;
  config: Record<string, unknown>;
}) {
  const frame = useRef<HTMLIFrameElement>(null);
  const send = () =>
    frame.current?.contentWindow?.postMessage(
      { type: "jinie-screen-config", page, config },
      location.origin,
    );
  useEffect(() => {
    const sendConfig = () =>
      frame.current?.contentWindow?.postMessage(
        { type: "jinie-screen-config", page, config },
        location.origin,
      );
    const ready = (event: MessageEvent) => {
      if (
        event.source === frame.current?.contentWindow &&
        event.origin === location.origin &&
        event.data?.type === "jinie-screen-ready"
      )
        sendConfig();
    };
    window.addEventListener("message", ready);
    sendConfig();
    return () => window.removeEventListener("message", ready);
  }, [page, config]);
  return (
    <div className="accepted-screen-frame">
      <div className="device-top">
        <i />
        <span>YOUR APP · MOBILE</span>
        <i />
      </div>
      <iframe
        ref={frame}
        title={"Accepted " + page + " screen"}
        src="/screen-preview.html"
        onLoad={send}
      />
    </div>
  );
}
