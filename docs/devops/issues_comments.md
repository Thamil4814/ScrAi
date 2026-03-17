# Issues And Comments

## 2026-03-17 I

- The architect manifest service uses the OpenAI Agents SDK against an OpenAI-compatible endpoint when `PYSCRAI_ARCHITECT_BASE_URL` and `PYSCRAI_ARCHITECT_MODEL` are configured, with optional `PYSCRAI_ARCHITECT_API_KEY`; otherwise it falls back to a deterministic heuristic adapter so local development and tests remain stable.

