const ALLOWED_ORIGIN = "https://mrvsh879.github.io";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...corsHeaders(),
    },
  });
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function localeFor(language) {
  return language === "de" ? "de-DE" : "cs-CZ";
}

function languageName(language) {
  return language === "de" ? "German" : "Czech";
}

function normalizeText(text, language = "cs") {
  return String(text || "")
    .toLocaleLowerCase(localeFor(language))
    .replace(/[^\p{L}\p{N}\s]/gu, "")
    .replace(/\s+/g, " ")
    .trim();
}

function levenshtein(a, b) {
  const matrix = Array.from({ length: b.length + 1 }, (_, row) => [row]);
  for (let column = 0; column <= a.length; column++) matrix[0][column] = column;
  for (let row = 1; row <= b.length; row++) {
    for (let column = 1; column <= a.length; column++) {
      const cost = b[row - 1] === a[column - 1] ? 0 : 1;
      matrix[row][column] = Math.min(
        matrix[row - 1][column] + 1,
        matrix[row][column - 1] + 1,
        matrix[row - 1][column - 1] + cost,
      );
    }
  }
  return matrix[b.length][a.length];
}

function textMatchScore(reference, transcript, language) {
  const expected = normalizeText(reference, language);
  const actual = normalizeText(transcript, language);
  if (!expected || !actual) return 0;
  const distance = levenshtein(expected, actual);
  return clamp(Math.round((1 - distance / Math.max(expected.length, actual.length)) * 100), 0, 100);
}

function completenessScore(reference, transcript, language) {
  const expectedWords = normalizeText(reference, language).split(" ").filter(Boolean).length;
  const actualWords = normalizeText(transcript, language).split(" ").filter(Boolean).length;
  if (!expectedWords || !actualWords) return 0;
  return clamp(Math.round((Math.min(expectedWords, actualWords) / expectedWords) * 100), 0, 100);
}

function paceScore(reference, durationSec, level, language) {
  const words = normalizeText(reference, language).split(" ").filter(Boolean).length;
  const seconds = Number(durationSec || 0);
  if (!words || seconds < 1) return { score: 0, wpm: 0 };
  const wpm = (words / seconds) * 60;
  const idealMin = level === "A1" ? 50 : 60;
  const idealMax = level === "A1" ? 105 : 120;
  if (wpm >= idealMin && wpm <= idealMax) return { score: 100, wpm: Math.round(wpm) };
  const distance = wpm < idealMin ? idealMin - wpm : wpm - idealMax;
  return { score: clamp(Math.round(100 - distance * 2.2), 25, 100), wpm: Math.round(wpm) };
}

function confidenceScore(logprobs) {
  if (!Array.isArray(logprobs) || !logprobs.length) return 65;
  const values = logprobs.map(item => Number(item?.logprob)).filter(Number.isFinite);
  if (!values.length) return 65;
  const average = values.reduce((sum, value) => sum + value, 0) / values.length;
  return clamp(Math.round(Math.exp(average) * 100), 0, 100);
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    const url = new URL(request.url);
    if (request.method !== "POST" || url.pathname !== "/analyze-reading") {
      return json({
        status: "ok",
        service: "language-test-api",
        endpoint: "/analyze-reading",
        languages: ["cs", "de"],
      });
    }

    try {
      if (!env.OPENAI_API_KEY) return json({ error: "OPENAI_API_KEY is not configured" }, 500);
      if (!env.RECORDINGS) return json({ error: "R2 binding RECORDINGS is not configured" }, 500);

      const formData = await request.formData();
      const audio = formData.get("audio");
      const candidateId = String(formData.get("candidateId") || "anonymous");
      const sessionId = String(formData.get("sessionId") || crypto.randomUUID());
      const questionId = String(formData.get("questionId") || "unknown");
      const referenceText = String(formData.get("referenceText") || "");
      const level = String(formData.get("level") || "A2");
      const durationSec = Number(formData.get("durationSec") || 0);
      const requestedLanguage = String(formData.get("language") || "cs").toLowerCase();
      const language = ["cs", "de"].includes(requestedLanguage) ? requestedLanguage : "cs";

      if (!(audio instanceof File)) return json({ error: "Audio file is required" }, 400);
      if (!referenceText.trim()) return json({ error: "Reference text is required" }, 400);
      if (durationSec < 3 || audio.size < 1500) return json({ error: "Recording is empty or too short" }, 400);
      if (audio.size > 10 * 1024 * 1024) return json({ error: "Audio file is too large" }, 413);

      const safe = value => String(value).replace(/[^a-zA-Z0-9_-]/g, "_");
      const extension = audio.type.includes("ogg") ? "ogg" : audio.type.includes("mp4") ? "mp4" : "webm";
      const objectKey = `recordings/${safe(candidateId)}/${safe(sessionId)}/${safe(questionId)}-${Date.now()}.${extension}`;
      const audioBuffer = await audio.arrayBuffer();

      await env.RECORDINGS.put(objectKey, audioBuffer, {
        httpMetadata: { contentType: audio.type || "audio/webm" },
        customMetadata: {
          candidateId,
          sessionId,
          questionId,
          level,
          language,
          durationSec: String(durationSec),
        },
      });

      const transcriptionForm = new FormData();
      transcriptionForm.append("file", new File([audioBuffer], `reading.${extension}`, { type: audio.type || "audio/webm" }));
      transcriptionForm.append("model", "gpt-4o-mini-transcribe");
      transcriptionForm.append("language", language);
      transcriptionForm.append("response_format", "json");
      transcriptionForm.append("include[]", "logprobs");
      transcriptionForm.append("prompt", `The speaker is reading a ${languageName(language)} text aloud. Transcribe only what is actually audible. Reference text: ${referenceText}`);

      const transcriptionResponse = await fetch("https://api.openai.com/v1/audio/transcriptions", {
        method: "POST",
        headers: { Authorization: `Bearer ${env.OPENAI_API_KEY}` },
        body: transcriptionForm,
      });

      if (!transcriptionResponse.ok) {
        const details = await transcriptionResponse.text();
        await env.RECORDINGS.delete(objectKey);
        return json({ error: "Transcription failed", details }, 502);
      }

      const transcription = await transcriptionResponse.json();
      const transcript = String(transcription.text || "").trim();
      if (!transcript) {
        await env.RECORDINGS.delete(objectKey);
        return json({ error: "No speech was recognized. Please record again." }, 422);
      }

      const textMatch = textMatchScore(referenceText, transcript, language);
      const completeness = completenessScore(referenceText, transcript, language);
      const confidence = confidenceScore(transcription.logprobs);
      const pace = paceScore(referenceText, durationSec, level, language);
      const overall = clamp(Math.round(textMatch * 0.45 + completeness * 0.2 + confidence * 0.25 + pace.score * 0.1), 0, 96);

      return json({
        success: true,
        language,
        recordingKey: objectKey,
        transcript,
        scores: {
          overall,
          textMatch,
          completeness,
          recognitionConfidence: confidence,
          pace: pace.score,
          wordsPerMinute: pace.wpm,
        },
        note: "This is an automated intelligibility and reading-accuracy estimate, not a certified phonetic assessment.",
      });
    } catch (error) {
      return json({ error: "Internal server error", details: error instanceof Error ? error.message : String(error) }, 500);
    }
  },
};
