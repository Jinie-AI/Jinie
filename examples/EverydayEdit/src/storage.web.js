const KEY="jinie-a37ffab5a4334db6b0ddbe6de303b8e8";
export async function loadState(){try{return JSON.parse(localStorage.getItem(KEY)||'null');}catch{return null;}}
export async function saveState(value){try{localStorage.setItem(KEY,JSON.stringify(value));}catch{/* sandboxed preview has memory-only state */}}
