// Behavioral contract checks in an isolated JS context. No filesystem/network imports.
import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
const require=createRequire(new URL('../frontend/package.json',import.meta.url));
const {transformSync}=require('esbuild');
export function validate(source){
 const code=transformSync(source,{loader:'jsx',format:'cjs',target:'es2020'}).code;
 const context=vm.createContext({module:{exports:{}},exports:{},require:(name)=>{
   if(name==='react')return {createElement:(type,props,...children)=>({type,props:props||{},children}),useState:(init)=>[init,()=>{}],useEffect:()=>{}};
   if(name==='react-native')return {View:'View',Text:'Text',Pressable:'Pressable',Image:'Image',StyleSheet:{create:x=>x}};
  throw new Error('Unsupported import: '+name);
 }},{codeGeneration:{strings:false,wasm:false},microtaskMode:'afterEvaluate'});
 vm.runInContext(code,context,{timeout:1000});
 const checks=[];
 for(const [dark,horizontal] of [[false,false],[true,true]]){
  const tests=`
   (()=>{
    let opens=0,adds=0;
    const product={name:'Contract item',price:2490,icon:'★',category:'Test'};
    const C=module.exports.default;
    if(typeof C!=='function')throw Error('Missing default component');
    const tree=C({product,primary:'#7254cc',dark:${dark},horizontal:${horizontal},onOpen:()=>opens++,onAdd:()=>adds++});
    const nodes=[];const visit=x=>{if(x&&typeof x==='object'){nodes.push(x);(x.children||[]).flat(Infinity).forEach(visit);}};visit(tree);
    const text=x=>x==null?'':Array.isArray(x)?x.map(text).join(''):typeof x==='object'?text(x.children):String(x);
    if(!text(tree).includes('Contract item'))throw Error('Missing product name');
    if(!text(tree).replaceAll(',','').includes('2490'))throw Error('Missing product price');
    const open=nodes.find(n=>n.type==='Pressable'&&n.props.accessibilityLabel==='View Contract item');
    const add=nodes.find(n=>n.type==='Pressable'&&n.props.accessibilityLabel==='Add Contract item to bag');
    if(!open||!add)throw Error('Missing accessible buttons');
    open.props.onPress();add.props.onPress();
    if(opens!==1||adds!==1)throw Error('Button callback failed');
    return {dark:${dark},horizontal:${horizontal},render:true,price:true,open:true,add:true};
   })()
  `;
  checks.push(vm.runInContext(tests,context,{timeout:1000}));
 }
 return {passed:true,checks,note:'Known ProductCard contract only; browser/native validation remains separate.'};
}
if(process.argv[2]){try{console.log(JSON.stringify(validate(fs.readFileSync(process.argv[2],'utf8'))));}catch(e){console.log(JSON.stringify({passed:false,error:e.message}));process.exitCode=1;}}
