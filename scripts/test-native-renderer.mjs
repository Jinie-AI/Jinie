import fs from 'node:fs';
import vm from 'node:vm';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require=createRequire(new URL('../frontend/package.json',import.meta.url));
const {buildSync}=require('esbuild');
const code=buildSync({entryPoints:[fileURLToPath(new URL('../backend/studio/templates/AppView.jsx',import.meta.url))],bundle:true,write:false,format:'cjs',external:['react','react-native']}).outputFiles[0].text;
for(const platform of ['android','ios']){
 const React={createElement:(type,props,...children)=>({type,props,children}),createContext:()=>({Provider:'Provider'}),useContext:()=>({}),useEffect:()=>{},useState:init=>[init,()=>{}]};
 const native={Platform:{OS:platform,select:options=>options[platform]??options.default},StyleSheet:{create:x=>x},useColorScheme:()=> 'light',View:'View',Text:'Text',ScrollView:'ScrollView',Pressable:'Pressable',TextInput:'TextInput',Image:'Image'};
 const context=vm.createContext({module:{exports:{}},exports:{},window:{},require:name=>{if(name==='react')return React;if(name==='react-native')return native;throw Error(name);}});
 vm.runInContext(code,context,{timeout:1000});
 context.config={name:'Native check',primary:'#ffffff',secondary:'#ede5f7',theme:'light',font:'sans',bodyFont:'sans',layout:'grid',navigation:'bottom',business:'clothing',pages:['home','products'],products:[{id:'1',name:'Example',price:100,category:'Collection'}],screen_configs:{}};
 vm.runInContext('module.exports.default({config})',context,{timeout:1000});
 console.log(platform+' renderer starts without browser globals');
}
