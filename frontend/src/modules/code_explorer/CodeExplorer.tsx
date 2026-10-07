import FileTree from "./FileTree";
import Prism from "prismjs";
import EditorModule from "react-simple-code-editor";
const Editor =
  (
    EditorModule as unknown as {
      default?: typeof EditorModule;
    }
  ).default ?? EditorModule;
import "prismjs/components/prism-jsx";
import "prismjs/components/prism-json";
import "prismjs/themes/prism.css";
import { request } from "../shared/studioApi";
import type { StudioContext } from "../shared/useStudioController";
// Module 15 - Code Explorer: browses generated files, saves edits, shows requirement links and rebuilds edited source.
export default function CodeExplorer({
  project,
  setTab,
  busy,
  files,
  file,
  setFile,
  code,
  setCode,
  dirty,
  setDirty,
  setFocusedRequirement,
  setNotice,
  active,
  endpoint,
  action,
  accept,
}: Pick<
  StudioContext,
  | "project"
  | "setTab"
  | "busy"
  | "files"
  | "file"
  | "setFile"
  | "code"
  | "setCode"
  | "dirty"
  | "setDirty"
  | "setFocusedRequirement"
  | "setNotice"
  | "active"
  | "current"
  | "endpoint"
  | "action"
  | "accept"
>) {
  if (!project) return null;
  return (
    <section className="panel code-panel">
      <div className="panel-title">
        <div>
          <h2>Source explorer</h2>
          <small className="subtle">
            {dirty ? "Unsaved edits" : file} · JSX / JSON / JavaScript
          </small>
        </div>
        <div className="button-row">
          <button
            className="secondary"
            disabled={!dirty || active || busy}
            onClick={() =>
              action(async () => {
                accept(
                  await request(
                    endpoint("/file?path=" + encodeURIComponent(file)),
                    "PUT",
                    { content: code },
                  ),
                );
                setDirty(false);
                setNotice("Source saved. Rebuild to refresh the preview.");
              })
            }
          >
            Save file
          </button>
          <button
            className="primary"
            disabled={dirty || active || busy || !files.length}
            onClick={() =>
              action(async () => {
                accept(await request(endpoint("/rebuild"), "POST"));
                setTab("Preview");
              })
            }
          >
            Rebuild source ↗
          </button>
        </div>
      </div>
      <div className="button-row" aria-label="Requirements linked to this file">
        {project.traceability
          .filter((link) => link.files.includes(file))
          .map((link) => (
            <button
              key={link.requirement}
              className="id-badge"
              onClick={() => {
                if (dirty && !confirm("Discard unsaved file edits?")) return;
                setDirty(false);
                setFocusedRequirement(link.requirement);
                setTab("Requirements");
              }}
            >
              {link.requirement} · {link.page}
            </button>
          ))}
        {!project.traceability.some((link) => link.files.includes(file)) && (
          <small className="subtle">
            No requirement link recorded for this file.
          </small>
        )}
      </div>
      <div className="code-layout">
        <div className="file-tree">
          <FileTree
            files={files}
            current={file}
            onSelect={(f) => {
              if (dirty && !confirm("Discard unsaved file edits?")) return;
              setFile(f);
            }}
          />
        </div>
        <Editor
          className="source-editor"
          textareaId="source-code"
          value={code}
          disabled={active}
          onValueChange={(value) => {
            setCode(value);
            setDirty(true);
          }}
          highlight={(value) =>
            Prism.highlight(
              value,
              Prism.languages[file.endsWith(".json") ? "json" : "jsx"],
              "jsx",
            )
          }
          padding={18}
          style={{
            fontFamily: "Consolas, monospace",
            fontSize: 11,
            minHeight: 600,
          }}
        />
      </div>
      {!files.length && <p>Generate the project to explore its source.</p>}
    </section>
  );
}
