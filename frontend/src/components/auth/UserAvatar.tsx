import type { User } from "./AuthModal";
import { API } from "../../modules/shared/studioApi";

// One avatar renderer keeps sidebar and header photos consistent with the account settings upload.
export default function UserAvatar({ user, size = 32 }: { user: User; size?: number }) {
  const src = user.photo_url?.startsWith("/api/auth/avatars/")
    ? API.replace(/\/api$/, "") + user.photo_url
    : user.photo_url?.startsWith("https://") ? user.photo_url : undefined;
  return <span className="avatar workspace-avatar" style={{ width: size, height: size, position: "relative", overflow: "hidden", flexShrink: 0, display: "inline-grid", placeItems: "center", verticalAlign: "middle" }}>
    <span>{user.initials}</span>
    {src && <img key={src} src={src} alt="" referrerPolicy="no-referrer" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }} onError={(event) => { event.currentTarget.style.display = "none"; }} />}
  </span>;
}
