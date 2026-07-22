import fs from 'node:fs/promises';

const path='cloudflare/worker.js';
let code=await fs.readFile(path,'utf8');

function replaceOnce(oldText,newText,label){
  if(!code.includes(oldText)) throw new Error(`${label} not found`);
  code=code.replace(oldText,newText);
}

replaceOnce(
'function normalizeText(text) {\n  return String(text || "")\n    .toLocaleLowerCase("cs-CZ")',
'function normalizeText(text, locale = "cs-CZ") {\n  return String(text || "")\n    .toLocaleLowerCase(locale)',
'normalize locale');

replaceOnce('function textMatchScore(reference, transcript) {\n  const expected = normalizeText(reference);\n  const actual = normalizeText(transcript);','function textMatchScore(reference, transcript, locale) {\n  const expected = normalizeText(reference, locale);\n  const actual = normalizeText(transcript, locale);','text match locale');
replaceOnce('function completenessScore(reference, transcript) {\n  const expectedWords = normalizeText(reference).split(" ").filter(Boolean).length;\n  const actualWords = normalizeText(transcript).split(" ").filter(Boolean).length;','function completenessScore(reference, transcript, locale) {\n  const expectedWords = normalizeText(reference, locale).split(" ").filter(Boolean).length;\n  const actualWords = normalizeText(transcript, locale).split(" ").filter(Boolean).length;','completeness locale');
replaceOnce('function paceScore(reference, durationSec, level) {\n  const words = normalizeText(reference).split(" ").filter(Boolean).length;','function paceScore(reference, durationSec, level, locale) {\n  const words = normalizeText(reference, locale).split(" ").filter(Boolean).length;','pace locale');
replaceOnce('const durationSec = Number(formData.get("durationSec") || 0);','const durationSec = Number(formData.get("durationSec") || 0);\n       const language = String(formData.get("language") || "cs");\n       const supportedLanguages = { cs: { locale: "cs-CZ", name: "Czech" }, de: { locale: "de-DE", name: "German" } };\n       const languageConfig = supportedLanguages[language] || supportedLanguages.cs;','language form field');
replaceOnce('transcriptionForm.append("language", "cs");','transcriptionForm.append("language", language);','transcription language');
replaceOnce('transcriptionForm.append("prompt", `The speaker is reading this Czech text aloud: ${referenceText}`);','transcriptionForm.append("prompt", `The speaker is reading this ${languageConfig.name} text aloud: ${referenceText}`);','transcription prompt');
replaceOnce('const textMatch = textMatchScore(referenceText, transcript);\n       const completeness = completenessScore(referenceText, transcript);','const textMatch = textMatchScore(referenceText, transcript, languageConfig.locale);\n       const completeness = completenessScore(referenceText, transcript, languageConfig.locale);','score locales');
replaceOnce('const pace = paceScore(referenceText, durationSec, level);','const pace = paceScore(referenceText, durationSec, level, languageConfig.locale);','pace call');
replaceOnce('customMetadata: { candidateId, sessionId, questionId, level, durationSec: String(durationSec) },','customMetadata: { candidateId, sessionId, questionId, level, language, durationSec: String(durationSec) },','recording metadata');

await fs.writeFile(path,code);
console.log('Worker now supports Czech and German');
