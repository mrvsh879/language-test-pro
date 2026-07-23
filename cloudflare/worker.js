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
  const locales = {
    cs: "cs-CZ",
    de: "de-DE",
    it: "it-IT",
    pl: "pl-PL",
    sk: "sk-SK",
    fr: "fr-FR",
    ro: "ro-RO",
    en: "en-US",
  };

  return locales[language] || locales.cs;
}

function cleanPrompt(language) {
  const prompts = {
    cs: [
      "Přepiš pouze skutečně slyšitelná česká slova.",
      "Mluvčího neopravuj.",
      "Nedoplňuj vynechaná slova.",
      "Nejasná slova nehádej podle kontextu věty.",
    ],
    de: [
      "Transkribiere ausschließlich die tatsächlich hörbaren deutschen Wörter.",
      "Korrigiere den Sprecher nicht.",
      "Ergänze keine fehlenden Wörter.",
      "Wenn ein Wort undeutlich ist, errate es nicht anhand des Satzkontexts.",
    ],
    it: [
      "Trascrivi esclusivamente le parole italiane realmente udibili.",
      "Non correggere il parlante.",
      "Non aggiungere parole mancanti.",
      "Non indovinare le parole poco chiare dal contesto della frase.",
    ],
    pl: [
      "Zapisz wyłącznie rzeczywiście słyszalne polskie słowa.",
      "Nie poprawiaj osoby mówiącej.",
      "Nie dodawaj pominiętych słów.",
      "Nie zgaduj niewyraźnych słów na podstawie kontekstu zdania.",
    ],
    sk: [
      "Prepíš iba skutočne počuteľné slovenské slová.",
      "Hovoriaceho neopravuj.",
      "Nedopĺňaj vynechané slová.",
      "Nejasné slová nehádaj podľa kontextu vety.",
    ],
    fr: [
      "Transcris uniquement les mots français réellement audibles.",
      "Ne corrige pas la personne qui parle.",
      "N'ajoute aucun mot omis.",
      "Ne devine pas les mots peu clairs à partir du contexte de la phrase.",
    ],
    ro: [
      "Transcrie numai cuvintele românești care se aud efectiv.",
      "Nu corecta vorbitorul.",
      "Nu adăuga cuvinte omise.",
      "Nu ghici cuvintele neclare din contextul propoziției.",
    ],
    en: [
      "Transcribe only the English words that are actually audible.",
      "Do not correct the speaker.",
      "Do not add omitted words.",
      "Do not guess unclear words from the sentence context.",
    ],
  };

  return (prompts[language] || prompts.cs).join(" ");
}

function guidedPrompt(referenceText, language) {
  const prompts = {
    cs: [
      "Osoba se pokouší přečíst následující český text.",
      "Přepiš stále pouze to, co je skutečně slyšet.",
      "Text slouží jen k upřesnění nejasných míst.",
      `Očekávaný text: ${referenceText}`,
    ],
    de: [
      "Die Person versucht, den folgenden deutschen Text vorzulesen.",
      "Transkribiere weiterhin nur das tatsächlich Hörbare.",
      "Der Text dient nur zur Klärung undeutlicher Stellen.",
      `Erwarteter Text: ${referenceText}`,
    ],
    it: [
      "La persona sta cercando di leggere ad alta voce il seguente testo italiano.",
      "Trascrivi comunque soltanto ciò che è realmente udibile.",
      "Il testo serve solo a chiarire eventuali passaggi poco chiari.",
      `Testo previsto: ${referenceText}`,
    ],
    pl: [
      "Osoba próbuje przeczytać na głos poniższy polski tekst.",
      "Nadal zapisuj wyłącznie to, co rzeczywiście słychać.",
      "Tekst służy tylko do wyjaśnienia niewyraźnych fragmentów.",
      `Tekst oczekiwany: ${referenceText}`,
    ],
    sk: [
      "Osoba sa pokúša nahlas prečítať nasledujúci slovenský text.",
      "Stále prepíš iba to, čo je skutočne počuť.",
      "Text slúži len na objasnenie nejasných miest.",
      `Očakávaný text: ${referenceText}`,
    ],
    fr: [
      "La personne essaie de lire à voix haute le texte français suivant.",
      "Transcris toujours uniquement ce qui est réellement audible.",
      "Le texte sert seulement à clarifier les passages peu nets.",
      `Texte attendu : ${referenceText}`,
    ],
    ro: [
      "Persoana încearcă să citească cu voce tare următorul text în limba română.",
      "Transcrie în continuare numai ceea ce se aude efectiv.",
      "Textul servește doar la clarificarea fragmentelor neclare.",
      `Text așteptat: ${referenceText}`,
    ],
    en: [
      "The person is trying to read the following English text aloud.",
      "Continue to transcribe only what is actually audible.",
      "The text is provided only to clarify unclear passages.",
      `Expected text: ${referenceText}`,
    ],
  };

  return (prompts[language] || prompts.cs).join(" ");
}

function normalizeText(text, language = "cs") {
  return String(text || "")
    .toLocaleLowerCase(localeFor(language))
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function wordsFrom(text, language) {
  const normalized = normalizeText(text, language);
  return normalized ? normalized.split(" ").filter(Boolean) : [];
}

function levenshtein(a, b) {
  const previous = Array.from({ length: b.length + 1 }, (_, index) => index);
  const current = new Array(b.length + 1);

  for (let i = 1; i <= a.length; i++) {
    current[0] = i;

    for (let j = 1; j <= b.length; j++) {
      const substitutionCost = a[i - 1] === b[j - 1] ? 0 : 1;

      current[j] = Math.min(
        current[j - 1] + 1,
        previous[j] + 1,
        previous[j - 1] + substitutionCost,
      );
    }

    for (let j = 0; j <= b.length; j++) {
      previous[j] = current[j];
    }
  }

  return previous[b.length];
}

function characterSimilarity(first, second, language) {
  const a = normalizeText(first, language);
  const b = normalizeText(second, language);

  if (!a || !b) return 0;

  const distance = levenshtein(a, b);
  return clamp(
    Math.round((1 - distance / Math.max(a.length, b.length)) * 100),
    0,
    100,
  );
}

/**
 * Выравнивает эталонные и распознанные слова.
 *
 * Результат:
 * - matches — правильные слова;
 * - substitutions — заменённые слова;
 * - deletions — пропущенные слова;
 * - insertions — добавленные слова.
 */
function alignWords(reference, transcript, language) {
  const expected = wordsFrom(reference, language);
  const actual = wordsFrom(transcript, language);

  const rows = expected.length + 1;
  const columns = actual.length + 1;

  const dp = Array.from({ length: rows }, () =>
    Array.from({ length: columns }, () => ({
      cost: 0,
      operation: null,
    })),
  );

  for (let i = 1; i < rows; i++) {
    dp[i][0] = {
      cost: i,
      operation: "delete",
    };
  }

  for (let j = 1; j < columns; j++) {
    dp[0][j] = {
      cost: j,
      operation: "insert",
    };
  }

  for (let i = 1; i < rows; i++) {
    for (let j = 1; j < columns; j++) {
      const same = expected[i - 1] === actual[j - 1];

      const variants = [
        {
          cost: dp[i - 1][j - 1].cost + (same ? 0 : 1),
          operation: same ? "match" : "substitute",
        },
        {
          cost: dp[i - 1][j].cost + 1,
          operation: "delete",
        },
        {
          cost: dp[i][j - 1].cost + 1,
          operation: "insert",
        },
      ];

      variants.sort((left, right) => left.cost - right.cost);
      dp[i][j] = variants[0];
    }
  }

  const operations = [];
  let i = expected.length;
  let j = actual.length;

  while (i > 0 || j > 0) {
    const operation = dp[i][j].operation;

    if (operation === "match") {
      operations.push({
        type: "match",
        expected: expected[i - 1],
        actual: actual[j - 1],
      });
      i--;
      j--;
    } else if (operation === "substitute") {
      operations.push({
        type: "substitution",
        expected: expected[i - 1],
        actual: actual[j - 1],
      });
      i--;
      j--;
    } else if (operation === "delete") {
      operations.push({
        type: "deletion",
        expected: expected[i - 1],
        actual: null,
      });
      i--;
    } else if (operation === "insert") {
      operations.push({
        type: "insertion",
        expected: null,
        actual: actual[j - 1],
      });
      j--;
    } else {
      break;
    }
  }

  operations.reverse();

  const matches = operations.filter(item => item.type === "match");
  const substitutions = operations.filter(
    item => item.type === "substitution",
  );
  const deletions = operations.filter(item => item.type === "deletion");
  const insertions = operations.filter(item => item.type === "insertion");

  return {
    expectedWords: expected.length,
    actualWords: actual.length,
    matches: matches.length,
    substitutions,
    deletions,
    insertions,
    operations,
  };
}

function calculateWordScores(alignment) {
  if (!alignment.expectedWords) {
    return {
      wordAccuracy: 0,
      completeness: 0,
    };
  }

  /*
   * Word accuracy:
   * учитывает совпадения, замены, пропуски и лишние слова.
   */
  const totalErrors =
    alignment.substitutions.length +
    alignment.deletions.length +
    alignment.insertions.length;

  const wordAccuracy = clamp(
    Math.round(
      (1 - totalErrors / Math.max(
        alignment.expectedWords,
        alignment.actualWords,
        1,
      )) * 100,
    ),
    0,
    100,
  );

  /*
   * Completeness:
   * сколько эталонных слов было действительно правильно распознано.
   *
   * Замена слова не считается прочитанным правильным словом.
   */
  const completeness = clamp(
    Math.round(
      (alignment.matches / alignment.expectedWords) * 100,
    ),
    0,
    100,
  );

  return {
    wordAccuracy,
    completeness,
  };
}

function paceScore(reference, durationSec, level, language) {
  const words = wordsFrom(reference, language).length;
  const seconds = Number(durationSec || 0);

  if (!words || seconds < 1) {
    return {
      score: 0,
      wpm: 0,
      status: "invalid",
    };
  }

  const wpm = (words / seconds) * 60;

  const ranges = {
    A1: [45, 100],
    A2: [50, 110],
    B1: [55, 120],
    B2: [60, 130],
    C1: [65, 140],
    C2: [70, 145],
  };

  const [idealMin, idealMax] = ranges[level] || ranges.B1;

  if (wpm >= idealMin && wpm <= idealMax) {
    return {
      score: 100,
      wpm: Math.round(wpm),
      status: "normal",
    };
  }

  const distance = wpm < idealMin
    ? idealMin - wpm
    : wpm - idealMax;

  return {
    score: clamp(Math.round(100 - distance * 1.8), 25, 100),
    wpm: Math.round(wpm),
    status: wpm < idealMin ? "slow" : "fast",
  };
}

function confidenceScore(logprobs) {
  if (!Array.isArray(logprobs) || !logprobs.length) return 60;

  const values = logprobs
    .map(item => Number(item?.logprob))
    .filter(Number.isFinite);

  if (!values.length) return 60;

  /*
   * Отбрасываем часть крайних значений, чтобы одно очень неуверенное
   * служебное слово не уничтожало всю оценку.
   */
  values.sort((a, b) => a - b);

  const trimCount = values.length >= 10
    ? Math.floor(values.length * 0.1)
    : 0;

  const trimmed = trimCount
    ? values.slice(trimCount, values.length - trimCount)
    : values;

  const average =
    trimmed.reduce((sum, value) => sum + value, 0) /
    trimmed.length;

  return clamp(
    Math.round(Math.exp(average) * 100),
    0,
    100,
  );
}

function criticalWordPenalty(alignment) {
  /*
   * Числа и отрицания особенно важны:
   * 15 вместо 50 или nicht вместо jetzt могут менять весь смысл.
   */
  const criticalWords = new Set([
    "nicht",
    "kein",
    "keine",
    "keinen",
    "niemals",
    "ne",
    "není",
    "nebyl",
    "nikdy",
    "non",
    "nessun",
    "nessuna",
    "nessuno",
    "mai",
    "nie",
    "żaden",
    "żadna",
    "nigdy",
    "nie",
    "žiadny",
    "žiadna",
    "nikdy",
    "ne",
    "pas",
    "aucun",
    "aucune",
    "jamais",
    "nu",
    "niciun",
    "nicio",
    "niciodată",
    "not",
    "no",
    "never",
  ]);

  let penalty = 0;

  for (const item of [
    ...alignment.substitutions,
    ...alignment.deletions,
  ]) {
    const expected = String(item.expected || "");

    if (
      criticalWords.has(expected) ||
      /\d/.test(expected)
    ) {
      penalty += 5;
    }
  }

  return clamp(penalty, 0, 15);
}

function buildFeedback({
  wordAccuracy,
  completeness,
  recognitionConfidence,
  stability,
  pace,
  alignment,
}) {
  const issues = [];

  if (completeness < 60) {
    issues.push("Прочитана только часть заданного текста.");
  }

  if (wordAccuracy < 70) {
    issues.push("Несколько слов были пропущены, заменены или добавлены.");
  }

  if (stability < 70) {
    issues.push(
      "Расшифровка заметно меняется после добавления эталонной подсказки: часть речи звучит неоднозначно.",
    );
  }

  if (recognitionConfidence < 60) {
    issues.push(
      "Система распознаёт некоторые фрагменты с низкой уверенностью.",
    );
  }

  if (pace.status === "slow") {
    issues.push("Темп чтения значительно медленнее ожидаемого.");
  }

  if (pace.status === "fast") {
    issues.push("Темп чтения слишком быстрый, слова могут проглатываться.");
  }

  if (!issues.length) {
    issues.push(
      "Текст прочитан достаточно полно, стабильно и понятно.",
    );
  }

  return {
    issues,
    omittedWords: alignment.deletions
      .slice(0, 10)
      .map(item => item.expected),
    substitutedWords: alignment.substitutions
      .slice(0, 10)
      .map(item => ({
        expected: item.expected,
        heard: item.actual,
      })),
    addedWords: alignment.insertions
      .slice(0, 10)
      .map(item => item.actual),
  };
}

async function transcribeAudio({
  audioBuffer,
  extension,
  mimeType,
  language,
  prompt,
  apiKey,
}) {
  const transcriptionForm = new FormData();

  transcriptionForm.append(
    "file",
    new File(
      [audioBuffer],
      `reading.${extension}`,
      { type: mimeType || "audio/webm" },
    ),
  );

  transcriptionForm.append(
    "model",
    "gpt-4o-mini-transcribe",
  );

  transcriptionForm.append("language", language);
  transcriptionForm.append("response_format", "json");
  transcriptionForm.append("include[]", "logprobs");
  transcriptionForm.append("temperature", "0");

  if (prompt) {
    transcriptionForm.append("prompt", prompt);
  }

  const response = await fetch(
    "https://api.openai.com/v1/audio/transcriptions",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
      },
      body: transcriptionForm,
    },
  );

  if (!response.ok) {
    const details = await response.text();
    throw new Error(
      `Transcription failed: ${response.status} ${details}`,
    );
  }

  return response.json();
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(),
      });
    }

    const url = new URL(request.url);

    if (
      request.method !== "POST" ||
      url.pathname !== "/analyze-reading"
    ) {
      return json({
        status: "ok",
        service: "language-test-api",
        endpoint: "/analyze-reading",
        languages: ["cs", "de", "it", "pl", "sk", "fr", "ro", "en"],
        scoringVersion: "2.2-multilingual",
      });
    }

    let objectKey = null;

    try {
      if (!env.OPENAI_API_KEY) {
        return json(
          { error: "OPENAI_API_KEY is not configured" },
          500,
        );
      }

      if (!env.RECORDINGS) {
        return json(
          { error: "R2 binding RECORDINGS is not configured" },
          500,
        );
      }

      const formData = await request.formData();

      const audio = formData.get("audio");
      const candidateId = String(
        formData.get("candidateId") || "anonymous",
      );
      const sessionId = String(
        formData.get("sessionId") || crypto.randomUUID(),
      );
      const questionId = String(
        formData.get("questionId") || "unknown",
      );
      const referenceText = String(
        formData.get("referenceText") || "",
      );
      const level = String(
        formData.get("level") || "A2",
      ).toUpperCase();
      const durationSec = Number(
        formData.get("durationSec") || 0,
      );
      const requestedLanguage = String(
        formData.get("language") || "cs",
      ).toLowerCase();

      const language = ["cs", "de", "it", "pl", "sk", "fr", "ro", "en"].includes(requestedLanguage)
        ? requestedLanguage
        : "cs";

      if (!(audio instanceof File)) {
        return json(
          { error: "Audio file is required" },
          400,
        );
      }

      if (!referenceText.trim()) {
        return json(
          { error: "Reference text is required" },
          400,
        );
      }

      if (durationSec < 3 || audio.size < 1500) {
        return json(
          { error: "Recording is empty or too short" },
          400,
        );
      }

      if (audio.size > 10 * 1024 * 1024) {
        return json(
          { error: "Audio file is too large" },
          413,
        );
      }

      const safe = value =>
        String(value).replace(/[^a-zA-Z0-9_-]/g, "_");

      const extension = audio.type.includes("ogg")
        ? "ogg"
        : audio.type.includes("mp4")
          ? "mp4"
          : "webm";

      objectKey =
        `recordings/${safe(candidateId)}/` +
        `${safe(sessionId)}/` +
        `${safe(questionId)}-${Date.now()}.${extension}`;

      const audioBuffer = await audio.arrayBuffer();

      await env.RECORDINGS.put(objectKey, audioBuffer, {
        httpMetadata: {
          contentType: audio.type || "audio/webm",
        },
        customMetadata: {
          candidateId,
          sessionId,
          questionId,
          level,
          language,
          durationSec: String(durationSec),
          scoringVersion: "2.2-multilingual",
        },
      });

      /*
       * 1. Основная расшифровка без полного правильного текста.
       */
      const cleanTranscription = await transcribeAudio({
        audioBuffer,
        extension,
        mimeType: audio.type,
        language,
        prompt: cleanPrompt(language),
        apiKey: env.OPENAI_API_KEY,
      });

      const transcript = String(
        cleanTranscription.text || "",
      ).trim();

      if (!transcript) {
        await env.RECORDINGS.delete(objectKey);

        return json(
          {
            error:
              "No speech was recognized. Please record again.",
          },
          422,
        );
      }

      /*
       * 2. Контрольная расшифровка с эталоном.
       */
      const guidedTranscription = await transcribeAudio({
        audioBuffer,
        extension,
        mimeType: audio.type,
        language,
        prompt: guidedPrompt(referenceText, language),
        apiKey: env.OPENAI_API_KEY,
      });

      const guidedTranscript = String(
        guidedTranscription.text || "",
      ).trim();

      const alignment = alignWords(
        referenceText,
        transcript,
        language,
      );

      const {
        wordAccuracy,
        completeness,
      } = calculateWordScores(alignment);

      /*
       * Совместимость со старым интерфейсом.
       */
      const textMatch = wordAccuracy;

      const recognitionConfidence = confidenceScore(
        cleanTranscription.logprobs,
      );

      /*
       * Чем ближе чистая и подсказанная расшифровки,
       * тем стабильнее и понятнее запись.
       */
      const stability = guidedTranscript
        ? characterSimilarity(
            transcript,
            guidedTranscript,
            language,
          )
        : recognitionConfidence;

      const pace = paceScore(
        referenceText,
        durationSec,
        level,
        language,
      );

      const penalty = criticalWordPenalty(alignment);

      /*
       * Новая формула:
       *
       * 35% — правильность слов;
       * 20% — полнота;
       * 20% — понятность без эталона;
       * 10% — стабильность двух распознаваний;
       * 10% — темп;
       * 5%  — базовая техническая надёжность.
       *
       * Последние 5% пока основаны на факте успешного
       * распознавания и достаточной длительности.
       */
      const technicalQuality =
        durationSec >= 3 && transcript ? 100 : 0;

      let overall = Math.round(
        wordAccuracy * 0.35 +
        completeness * 0.20 +
        recognitionConfidence * 0.20 +
        stability * 0.10 +
        pace.score * 0.10 +
        technicalQuality * 0.05 -
        penalty,
      );

      /*
       * Защита от завышения при неполном чтении.
       */
      if (completeness < 40) {
        overall = Math.min(overall, 35);
      } else if (completeness < 60) {
        overall = Math.min(overall, 50);
      } else if (completeness < 75) {
        overall = Math.min(overall, 70);
      }

      /*
       * Если чистое распознавание очень неуверенное,
       * нельзя выдавать почти идеальный результат.
       */
      if (recognitionConfidence < 45) {
        overall = Math.min(overall, 60);
      }

      if (stability < 50) {
        overall = Math.min(overall, 65);
      }

      overall = clamp(overall, 0, 96);

      const feedback = buildFeedback({
        wordAccuracy,
        completeness,
        recognitionConfidence,
        stability,
        pace,
        alignment,
      });

      const needsRetry =
        completeness < 40 ||
        recognitionConfidence < 30 ||
        !transcript;

      return json({
        success: true,
        language,
        recordingKey: objectKey,

        /*
         * Главная честная расшифровка — без полного эталона.
         */
        transcript,

        /*
         * Контрольную расшифровку можно хранить в отчёте,
         * но кандидату необязательно показывать.
         */
        guidedTranscript,

        scores: {
          overall,

          /*
           * Старые поля сохранены.
           */
          textMatch,
          completeness,
          recognitionConfidence,
          pace: pace.score,
          wordsPerMinute: pace.wpm,

          /*
           * Новые подробные поля.
           */
          wordAccuracy,
          intelligibility: recognitionConfidence,
          transcriptionStability: stability,
          technicalQuality,
          paceStatus: pace.status,
          criticalWordPenalty: penalty,
        },

        wordAnalysis: {
          expectedWords: alignment.expectedWords,
          recognizedWords: alignment.actualWords,
          correctlyMatchedWords: alignment.matches,
          substitutions: alignment.substitutions,
          omissions: alignment.deletions,
          additions: alignment.insertions,
        },

        feedback,
        needsRetry,
        scoringVersion: "2.2-multilingual",

        note:
          "Automated reading accuracy and intelligibility estimate. " +
          "It does not provide certified phoneme-level pronunciation assessment.",
      });
    } catch (error) {
      /*
       * Удаляем запись только при полном техническом сбое.
       */
      if (objectKey && env.RECORDINGS) {
        try {
          await env.RECORDINGS.delete(objectKey);
        } catch {
          // Не скрываем основную ошибку.
        }
      }

      return json(
        {
          error: "Internal server error",
          details:
            error instanceof Error
              ? error.message
              : String(error),
        },
        500,
      );
    }
  },
};
