import {createRequire} from 'node:module';
import fs from 'node:fs';
const require=createRequire(new URL('../frontend/package.json',import.meta.url));
const {transform}=require('esbuild');
const rows=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
let passed=0;const errors=[];
for(const row of rows){try{await transform(row.generated,{loader:'jsx'});if(!row.generated.includes('export default'))throw new Error('No default export');passed++;}catch(e){errors.push({id:row.id,error:e.message});}}
console.log(JSON.stringify({count:rows.length,syntax_valid:passed,syntax_valid_rate:passed/rows.length,errors,note:'Syntax validation does not prove correct imports, props, rendering or behavior.'},null,2));
