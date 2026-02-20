# Medical Research Chatbot Demo — Spec

## Source Repo
GitHub: `Medical-chatbot` (clone into `../project-refs/Medical-chatbot` for reference)

## What It Does
Visitor types a neuroscience or medical research question and gets an informed answer. Demonstrates NLP + domain expertise.

## Tech — Two Options (decide after reviewing source repo)

### Option A: Retrieval-based (recommended for Pi)
- Embed a PubMed/neuroscience FAQ corpus using a small embedding model
- FAISS or ChromaDB index for similarity search
- Retrieve top-k passages → format as answer
- **Estimated size**: ~100 MB (embeddings + index)

### Option B: Small LLM
- TinyLlama-1.1B or similar via `llama-cpp-python` (GGUF Q4 quantized)
- **Estimated size**: ~700 MB
- Slower but more impressive

### Common
- **Framework**: Streamlit app on port 8503
- **Nginx route**: `/demo/chatbot` → proxy to `:8503`

## UI Requirements
- Chat interface with message history (session-only, not persisted)
- 5-6 example questions visitors can click to try
- Show source/reference for each answer (which papers/passages were retrieved)
- Typing indicator during inference
- Disclaimer: "This is a demo, not medical advice"

## Pi Constraints
- Rate limit: max 1 concurrent inference
- Max conversation length: 10 messages per session
- Response timeout: 30s
- If using LLM: streaming response to avoid timeout feel

## Integration
- Frontend `ProjectCard` for medical-chatbot links to `/demo/chatbot`
- Nginx proxies `/demo/chatbot` to Streamlit on `:8503`
- systemd service: `portfolio-demo-chatbot.service`
