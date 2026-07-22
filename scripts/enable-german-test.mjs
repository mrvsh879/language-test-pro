import fs from 'node:fs/promises';

const path='app.js';
let app=await fs.readFile(path,'utf8');

function replaceOnce(oldText,newText,label){
  if(!app.includes(oldText)) throw new Error(`${label} not found`);
  app=app.replace(oldText,newText);
}

replaceOnce(
"if(lang==='cs'){for(const file of ['cs-listening.json','cs-speaking.json']){const x=await fetch(`./data/${file}`,{cache:'no-store'});if(x.ok)qs.push(...(await x.json()).questions)}}",
"if(['cs','de'].includes(lang)){for(const file of [`${lang}-listening.json`,`${lang}-speaking.json`]){const x=await fetch(`./data/${file}`,{cache:'no-store'});if(x.ok)qs.push(...(await x.json()).questions)}}",
'language module loader');

replaceOnce(
"if(state.candidate.language==='cs'){state.queue.push(...shuffle(state.bank.filter(q=>q.skill==='listening'&&['A1','A2'].includes(q.level))).slice(0,4));state.queue.push(...shuffle(state.bank.filter(q=>q.skill==='speaking'&&['A1','A2'].includes(q.level))).slice(0,2))}",
"if(['cs','de'].includes(state.candidate.language)){state.queue.push(...shuffle(state.bank.filter(q=>q.skill==='listening'&&['A1','A2'].includes(q.level))).slice(0,4));state.queue.push(...shuffle(state.bank.filter(q=>q.skill==='speaking'&&['A1','A2'].includes(q.level))).slice(0,2))}",
'route extras');

replaceOnce(
"<span>${esc(t('playsLeft'))}: <b>${left}</b> · AI Czech MP3</span>",
"<span>${esc(t('playsLeft'))}: <b>${left}</b> · AI ${esc(LANGUAGES[state.candidate?.language]||'')} MP3</span>",
'audio label');

replaceOnce(
"const a=new Audio(`./audio/cs/${q.id}.mp3`);",
"const a=new Audio(`./audio/${state.candidate.language}/${q.id}.mp3`);",
'audio path');

replaceOnce(
"fd.append('level',q.level);",
"fd.append('level',q.level);fd.append('language',state.candidate.language);",
'worker language field');

await fs.writeFile(path,app);
console.log('German test integration enabled');
