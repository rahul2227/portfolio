# Handwritten Text Line Recognition — Spec

## What It Does

Visitor uploads a single pre-segmented handwritten text line image. The Pi runs ONNX
inference through a CNN + BiLSTM + CTC pipeline and returns the recognized text string
together with a per-character confidence score for each decoded character.

There is no text detection step. The model expects one horizontal text line as input,
not a full document page or a multi-line image.

## Architecture

```
Input image (grayscale, resized to 32 x variable width)
        |
        v
CNN feature extractor   — convolutional layers extract local stroke features
        |
        v
BiLSTM sequence model   — bidirectional LSTM reads left-to-right and right-to-left
        |
        v
CTC decoder             — Connectionist Temporal Classification; collapses blank
                          tokens and repeated characters into the final string
        |
        v
Output: recognized string + per-character confidence scores
```

## Model Details

- **Format**: ONNX, INT8 quantized
- **Size on disk**: ~12 MB
- **Vocabulary**: 82 English characters (a-z, A-Z, digits, common punctuation)
- **Training data**: IAM Handwriting Dataset (public benchmark for HTR research)
- **Input resolution**: 32 px height, width scaled proportionally (max 1024 px)
- **Output**: UTF-8 string and a list of `(char, confidence)` tuples

## Known Limitations

- No text detection — input must be a single pre-segmented line, not a full page
- No bounding box output — the model produces a sequence, not spatial coordinates
- No multi-line support — stitch lines externally before passing to the model
- English only — vocabulary does not cover accented characters or non-Latin scripts
- Accuracy degrades on very stylised, joined-up, or faint handwriting

## UI Requirements

- File upload (jpg, png, max 5 MB)
- Show the uploaded image
- Display the recognized text string
- Display per-character confidence as a coloured bar or table
- Provide 3 sample IAM line images visitors can click to try without uploading
- Show inference time in milliseconds

## Framework and Routing

- **Framework**: Streamlit app on port 8502
- **Base URL path**: `/demo/ocr` (passed to Streamlit via `--server.baseUrlPath`)
- **Nginx route**: `/demo/ocr/` proxied to `http://127.0.0.1:8502/`
- **WebSocket**: required — Streamlit uses WebSocket for live UI updates;
  Nginx must forward `Upgrade` and `Connection` headers

## Pi Constraints

- **MemoryMax**: 512 MB (covers ONNX runtime + Streamlit overhead)
- **CPUQuota**: 75%
- **Max upload size**: 5 MB (`--server.maxUploadSize=5`)
- **Target inference time**: < 5 s on Pi 4 with INT8 ONNX model
- Model is loaded once at startup and kept warm; no lazy-load required

## systemd Service

- Unit file: `deploy/systemd/portfolio-demo-ocr.service`
- Identifier: `portfolio-demo-ocr`
- Working directory: `/home/rahser/portfolio/demos/text-ocr`
- Virtual environment: `/home/rahser/portfolio/demos/text-ocr/.venv`

## Integration Points

- `backend/data/seed.json` — `text-ocr` entry with `demo_url: "/demo/ocr"`
- Frontend `ProjectCard` links to `/demo/ocr`
- Nginx `portfolio.conf` proxies `/demo/ocr/` and `/demo/ocr/_stcore/` to `:8502`
- Deploy script syncs deps from `demos/text-ocr/` and restarts the service
