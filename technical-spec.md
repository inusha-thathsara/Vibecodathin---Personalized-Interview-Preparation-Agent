# Technical Specification

> **Author Note**: I am Inusha Gunasekara, a solo competitor in Vobecodathon hackathon.

This document defines the API contract and submission requirements for the AI Interview Agent.

---

# HTTP Endpoint

Your agent must expose a single endpoint:

```
POST /api/interview
```

No authentication is required.

The endpoint must maintain interview state using the provided `sessionId`.

---

# Interview Flow

## 1. Start Interview

The first request initializes a new interview session.

```json
POST /api/interview

{
  "sessionId": "abc-123",
  "candidate": { ...candidate.json }
}
```

### Expected Response

```json
{
  "reply": "Welcome. Let's begin your interview.",
  "done": false,
  "meta": {
    "phase": "INTRO",
    "primary_questions": 1,
    "days_covered": [7],
    "current_day": 7,
    "current_title": "Embeddings Explained",
    "llm_provider": "ollama",
    "llm_model": "gemma3:1b",
    "llm_latency_ms": 420.5
  }
}
```

---

## 2. Conversation Turn & Early Termination

Every subsequent request contains the candidate's latest response.

```json
POST /api/interview

{
  "sessionId": "abc-123",
  "message": "I used vector embeddings and cosine similarity to index domain documents."
}
```

To request early termination of an ongoing interview, send `endEarly: true`:

```json
POST /api/interview

{
  "sessionId": "abc-123",
  "endEarly": true
}
```

### Expected Response (Active Interview)

```json
{
  "reply": "Can you explain how metadata filtering operates alongside HNSW indexing?",
  "done": false,
  "meta": { ... }
}
```

---

## 3. End Interview

When the interview is complete (or ended early), return `done: true` with structured feedback:

```json
{
  "reply": "The technical interview was concluded. Evaluated performance across completed curriculum turns.",
  "done": true,
  "feedback": {
    "summary": "Candidate demonstrated strong foundational technical knowledge across vector embeddings and RAG architecture.",
    "strengths": [
      "Demonstrated solid grasp of concepts from Day 7",
      "Clear technical communication regarding vector similarity"
    ],
    "gaps": [
      "Requires further consolidation on Day 10 concepts"
    ],
    "next": [
      "Practice architecture design for multi-agent workflows",
      "Deepen hands-on testing on RAG retrieval optimization"
    ],
    "topic_scores": [
      {
        "day": 7,
        "title": "Embeddings Explained",
        "score": 8,
        "note": "Evaluated dense vector embeddings (OpenAI / Gemini), high-dimensional vector math, and Cosine vs L2 similarity metrics. Primary tools: Sentence Transformers, OpenAI Embeddings. Candidate demonstrated first-try mastery.",
        "tools": ["Sentence Transformers", "OpenAI Embeddings", "Scikit-learn"]
      }
    ],
    "evidence": [
      "Candidate: \"I used vector embeddings and cosine similarity to index domain documents...\""
    ]
  },
  "meta": { ... }
}
```

---

# Feedback Format

The final evaluation response includes:

| Field | Type | Description |
|--------|------|-------------|
| `summary` | `string` | Executive summary of candidate performance. |
| `strengths` | `string[]` | Specific areas of technical strength. |
| `gaps` | `string[]` | Identified knowledge gaps or struggle areas. |
| `next` | `string[]` | Actionable recommended next steps. |
| `topic_scores` | `object[]` | Day-by-day technical scores with descriptive notes and tool chips. |
| `evidence` | `string[]` | Quoted candidate statements supporting evaluation scores. |

---

# Zero-Response Safeguard

If an interview session is ended early before any candidate responses are submitted (0 answers), the agent outputs an honest `0/10 NOT EVALUATED` evaluation report:

- `summary`: Explains that the session ended before responses were submitted.
- `topic_scores`: Renders `score: 0`, status label `NOT EVALUATED`, progress fill `0%`, and note `"Session terminated early before candidate submitted any technical responses."`.

---

# Notes

- Use the supplied `sessionId` throughout the interview.
- The interview remains conversational across multiple requests.
- The system enforces a **Question Enforcement Filter** ensuring interview responses end with a concrete question mark `?`.
- Requires covering at least **8 primary questions across 4 distinct curriculum days** for natural completion.
