# AI Provider Architecture

The engine uses an abstract `AIProvider` protocol supporting multiple inference backends.

## Supported Providers

- **HuggingFaceProvider**: Connects to Hugging Face Inference endpoints. Configured via `HF_TOKEN` and `HF_MODEL`.
- **OpenAICompatibleProvider**: Works with OpenAI, Groq, Together, vLLM, DeepSeek. Configured via `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL`.
- **OllamaProvider**: Local model runner. Configured via `OLLAMA_BASE_URL` and `OLLAMA_MODEL`.
- **MockAIProvider**: Deterministic mock provider for offline development, local test suites, and zero-credential environments.

---

## Configuration via Environment Variables

Set `DEFAULT_AI_PROVIDER` in `.env`:
```env
DEFAULT_AI_PROVIDER=mock
# or: huggingface / openai / ollama
```
