export const API_BASE = "http://localhost:8000";

export const GROQ_MODELS = [
  { id: 'llama-3.3-70b-versatile',                   name: 'Llama 3.3 70B (Versátil)' },
  { id: 'llama-3.1-8b-instant',                      name: 'Llama 3.1 8B (Rápido)' },
  { id: 'meta-llama/llama-4-scout-17b-16e-instruct', name: 'Llama 4 Scout 17B' },
  { id: 'qwen/qwen3-32b',                            name: 'Qwen3 32B' },
] as const;

export const DEFAULT_MODEL = GROQ_MODELS[0].id;
