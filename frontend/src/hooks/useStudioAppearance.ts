import {useEffect, useState} from 'react';
import type {PointerEvent} from 'react';
type Theme='light'|'dark'|'system';
export function useStudioAppearance(){
 const [theme,setTheme]=useState<Theme>(()=>{try{const v=localStorage.getItem('jinie_studio_theme');return v==='light'||v==='dark'?v:'system';}catch{return 'system';}});
 const [motion,setMotion]=useState(()=>{try{return localStorage.getItem('jinie_studio_motion')!=='off';}catch{return true;}});
 const [systemDark,setSystemDark]=useState(()=>matchMedia('(prefers-color-scheme: dark)').matches);
 const [reduced,setReduced]=useState(()=>matchMedia('(prefers-reduced-motion: reduce)').matches);
 useEffect(()=>{const dark=matchMedia('(prefers-color-scheme: dark)'),reduce=matchMedia('(prefers-reduced-motion: reduce)');const d=()=>setSystemDark(dark.matches),r=()=>setReduced(reduce.matches);dark.addEventListener('change',d);reduce.addEventListener('change',r);return()=>{dark.removeEventListener('change',d);reduce.removeEventListener('change',r);};},[]);
 const resolved=theme==='system'?(systemDark?'dark':'light'):theme;
 useEffect(()=>{document.documentElement.dataset.studioTheme=resolved;document.documentElement.style.colorScheme=resolved;try{localStorage.setItem('jinie_studio_theme',theme);localStorage.setItem('jinie_studio_motion',motion?'on':'off');}catch{/* Private storage can be unavailable. */}},[theme,resolved,motion]);
 function move(e:PointerEvent<HTMLElement>){if(!motion||reduced||e.pointerType==='touch')return;const box=e.currentTarget.getBoundingClientRect();const x=Math.max(-1,Math.min(1,(e.clientX-box.left)/box.width*2-1));const y=Math.max(-1,Math.min(1,(e.clientY-box.top)/box.height*2-1));e.currentTarget.style.setProperty('--pointer-x',`${x*10}deg`);e.currentTarget.style.setProperty('--pointer-y',`${-y*7}deg`);e.currentTarget.style.setProperty('--glow-x',`${(x+1)*50}%`);e.currentTarget.style.setProperty('--glow-y',`${(y+1)*50}%`);}
 function reset(e:PointerEvent<HTMLElement>){e.currentTarget.style.setProperty('--pointer-x','0deg');e.currentTarget.style.setProperty('--pointer-y','0deg');}
 return {theme,setTheme,motion,setMotion,resolved,animated:motion&&!reduced,move,reset};
}
