export default function FileTree({
  files,
  current,
  onSelect,
  prefix = "",
}: {
  files: string[];
  current: string;
  onSelect: (f: string) => void;
  prefix?: string;
}) {
  const groups = new Map<string, string[]>();
  const leaves: string[] = [];
  for (const file of files) {
    const rest = file.slice(prefix.length);
    const slash = rest.indexOf("/");
    if (slash < 0) leaves.push(file);
    else {
      const group = rest.slice(0, slash);
      groups.set(group, [...(groups.get(group) || []), file]);
    }
  }
  return (
    <>
      {[...groups].map(([group, items]) => (
        <details open key={group}>
          <summary>▱ {group}</summary>
          <div className="folder-contents">
            <FileTree
              files={items}
              current={current}
              onSelect={onSelect}
              prefix={prefix + group + "/"}
            />
          </div>
        </details>
      ))}
      {leaves.map((f) => (
        <button
          className={f === current ? "chosen" : ""}
          key={f}
          onClick={() => onSelect(f)}
        >
          <span>⌑</span>
          {f.slice(prefix.length)}
        </button>
      ))}
    </>
  );
}
