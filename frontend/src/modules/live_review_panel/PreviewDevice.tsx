import { useEffect, useRef, useState, type ReactNode } from "react";
export default function PreviewDevice({
  device,
  children,
}: {
  device: string;
  children: ReactNode;
}) {
  const host = useRef<HTMLDivElement>(null);
  const [available, setAvailable] = useState(1400);
  const width = device === "desktop" ? 1298 : device === "tablet" ? 838 : 393;
  const height = device === "tablet" ? 1070 : device === "desktop" ? 846 : 686;
  useEffect(() => {
    const observer = new ResizeObserver((entries) =>
      setAvailable(entries[0].contentRect.width),
    );
    if (host.current) observer.observe(host.current);
    return () => observer.disconnect();
  }, []);
  const scale = Math.min(1, available / width);
  return (
    <div ref={host} style={{ width: "100%", minWidth: 0 }}>
      <div
        style={{
          width: width * scale,
          height: height * scale,
          margin: "0 auto",
          position: "relative",
        }}
      >
        <div
          style={{
            width,
            height,
            transform: `scale(${scale})`,
            transformOrigin: "top left",
          }}
        >
          <div
            className={"device-frame " + device}
            style={{ width, maxWidth: "none" }}
          >
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
