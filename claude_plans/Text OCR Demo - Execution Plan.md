# Phase 2: Text OCR Demo — Execution Plan

## Context

The portfolio has a working foundation (React frontend, FastAPI backend, Nginx, systemd, deploy script). Phase 2 adds the first interactive ML demo — a handwritten text line recognizer built from the `Text_OCR` project. The original model is a CNN+BiLSTM with CTC loss trained on IAM Handwriting Dataset. It recognizes pre-segmented handwritten text lines (no detection/bounding boxes). We'll export it to ONNX, build a Streamlit demo, and integrate it into the portfolio infrastructure.

**Key decisions made:**
- Line recognition only (honest about model capabilities)
- ONNX Runtime (not raw PyTorch — lighter on Pi)
- Git LFS for model artifacts
- Text OCR detailed, other phases outlined

---

## Working Principles

### uv-First Python Management
- **All** Python projects use `uv` exclusively — never pip, never conda, never manual venv
- Each demo gets its own `pyproject.toml` managed by `uv`
- Commands: `uv sync` (install deps), `uv add <pkg>` (add dep), `uv run <cmd>` (execute in venv)
- `uv sync --group dev` to include test dependencies
- Always commit `uv.lock` after dependency changes
- Demo venvs are local: `cd demos/text-ocr && uv sync` creates `.venv/` in that directory
- On Pi deployment: `uv sync --frozen` (no resolution, just install from lockfile)

### Test-Driven Development
Every step writes tests BEFORE or alongside implementation. No step is complete until its tests pass.
- **Step 1 (ONNX export)**: Built-in validation asserting PyTorch vs ONNX output parity
- **Step 2 (Inference wrapper)**: `tests/test_model.py` — unit tests for preprocessing, CTC decode, end-to-end predict
- **Step 4 (Streamlit app)**: `tests/test_app.py` — smoke tests for app structure and asset integrity
- Test runner: `cd demos/text-ocr && uv run pytest tests/ -v`
- `pytest` goes in `[project.optional-dependencies.dev]`
- Gate: all tests must pass before proceeding to the next step

### Multi-Agent Parallel Workflow
Use Claude Code's specialized sub-agents (`backend-dev`, `frontend-dev`, `devops`, `design`) for concurrent development. Launch multiple agents in a single message when their tasks are independent.

| Agent | Role in Phase 2 |
|-------|-----------------|
| **backend-dev** | ONNX export script, inference wrapper (`model.py`), all Python tests |
| **frontend-dev** | Verify `ProjectCard` renders `demo_url` as working link to `/demo/ocr` |
| **devops** | Nginx location block, systemd service file, deploy script extensions |
| **design** | Streamlit app UI layout, color theme, component arrangement |

**Parallelization opportunities** (launch concurrently in single messages):
- Steps 1-2 (ML/Python work) and Step 5 (infra) have zero dependencies — run `backend-dev` and `devops` agents in parallel
- In Step 4, launch `design` agent for UI layout while `backend-dev` implements `app.py`
- After all code is written, launch `frontend-dev` to verify the ProjectCard link works

### Frontend Skill
For any frontend UI work (React components, pages, Tailwind styling), use the `/frontend-design` skill from the claude-code plugin. This skill generates production-grade, polished interfaces. Invoke it for:
- Designing the project detail page if adding `/projects/:slug` route
- Updating `ProjectCard` to properly render demo links
- Any new React components or pages

### CLAUDE.md Updates
After Phase 2 is complete, update `CLAUDE.md` to add:
- `demos/` directory structure and per-demo conventions
- Demo-specific commands: `cd demos/<name> && uv sync && uv run streamlit run app.py`
- Demo test commands: `cd demos/<name> && uv sync --group dev && uv run pytest tests/ -v`
- Streamlit + Nginx integration pattern (`--server.baseUrlPath`, WebSocket upgrade headers)
- Git LFS usage for `.onnx` model files
- Updated architecture diagram including demo apps

Also update `.claude/project-status.md` to mark Phase 2 complete and record decisions.

---

## Step 1: ONNX Export Script + Model Conversion

**Run on Mac only. One-time operation. Agent: `backend-dev`.**

### Source model details (verified from code)
- **Architecture**: `OCRModel` in `project_refs/Text_OCR/models/ocr_LSTM.py`
  - `CNNFeatureExtractor`: 4 conv blocks (1->64->128->256->512), each Conv2d(k=3,p=1) + BN + ReLU + MaxPool2d(2,2)
  - `CNNToRNN`: reshapes [B, 512, H/16, W/16] -> [W/16, B, 512 * H/16] = [W/16, B, 4096]
  - `BidirectionalLSTM`: nn.LSTM(input=4096, hidden=256, layers=2, bidirectional=True) -> nn.Linear(512, 82)
  - `LogSoftmax(dim=2)` at the end
- **Output shape**: [W/16, batch_size, 82] (log probabilities over 82-char vocab)
- **Weights**: `project_refs/Text_OCR/models/LSTM/best_model_LSTM.pth` (46 MB, PyTorch state_dict)
- **Vocab**: `project_refs/Text_OCR/data_preprocessing/mappings_LSTM.json` (82 chars, idx_to_char + char_to_idx)

### ONNX export caveats (verified from source)
1. **`CNNToRNN.forward` contains `assert height == expected_height`** — this will fail during ONNX tracing. The export script must define a modified `CNNToRNN` class with the assert removed.
2. **BiLSTM export**: PyTorch's ONNX exporter supports `nn.LSTM(bidirectional=True)` on opset >= 14. Use opset 17.
3. **Dynamic width axis**: Input is [B, 1, 128, W], output is [W/16, B, 82]. Both width dimensions must be dynamic.
4. **LogSoftmax**: Supported natively in ONNX.

### Create `demos/text-ocr/scripts/export_onnx.py`
1. Define model architecture classes (copy from source, remove the `assert` in `CNNToRNN`)
2. Load weights from `project_refs/Text_OCR/models/LSTM/best_model_LSTM.pth`
3. Export via `torch.onnx.export()`:
   - `opset_version=17`
   - `input_names=["image"]`, `output_names=["logits"]`
   - `dynamic_axes={"image": {0: "batch", 3: "width"}, "logits": {0: "seq_len", 1: "batch"}}`
4. Quantize to INT8: `onnxruntime.quantization.quantize_dynamic(model_path, output_path, weight_type=QuantType.QInt8)`
5. **Validation (built-in test)**:
   - Run 3 dummy inputs of different widths (512, 1024, 2048) through both PyTorch and ONNX
   - Assert `np.allclose(pytorch_output, onnx_output, atol=1e-4)` for each
   - Print validation results with max absolute difference
6. Output: `demos/text-ocr/models/ocr_lstm_int8.onnx`

### Copy mappings
Copy `project_refs/Text_OCR/data_preprocessing/mappings_LSTM.json` -> `demos/text-ocr/models/mappings.json`

### Set up Git LFS
Create `.gitattributes` at repo root:
```
demos/**/models/*.onnx filter=lfs diff=lfs merge=lfs -text
```
Run: `git lfs install && git lfs track "demos/**/models/*.onnx"`

### Dependencies (export-only, not needed at runtime)
In `pyproject.toml` under `[project.optional-dependencies]`:
```toml
export = ["torch>=2.1", "onnx>=1.15", "onnxruntime>=1.17"]
```
Install: `cd demos/text-ocr && uv sync --group export`

---

## Step 2: Inference Wrapper + Tests (TDD)

**Agent: `backend-dev`. Depends on Step 1 (needs the ONNX model file).**

### Write tests first: `demos/text-ocr/tests/test_model.py`

```python
import numpy as np
import pytest
from PIL import Image
from model import OCRInference

@pytest.fixture
def ocr_model():
    return OCRInference(
        model_path="models/ocr_lstm_int8.onnx",
        mappings_path="models/mappings.json",
    )

class TestPreprocessing:
    def test_grayscale_conversion(self, ocr_model):
        """RGB image input produces single-channel output."""
        rgb_image = Image.new("RGB", (400, 60), color=(128, 128, 128))
        tensor, _ = ocr_model.preprocess(rgb_image)
        assert tensor.shape[1] == 1  # single channel

    def test_height_resize(self, ocr_model):
        """Output height is always 128px."""
        image = Image.new("L", (400, 60))
        tensor, _ = ocr_model.preprocess(image)
        assert tensor.shape[2] == 128

    def test_aspect_ratio_maintained(self, ocr_model):
        """Width scales proportionally with height resize."""
        image = Image.new("L", (400, 64))  # aspect = 6.25
        tensor, _ = ocr_model.preprocess(image)
        expected_width = int(400 * (128 / 64))
        assert tensor.shape[3] == expected_width

    def test_max_width_capped(self, ocr_model):
        """Images wider than 2048px after resize get capped."""
        image = Image.new("L", (5000, 128))
        tensor, _ = ocr_model.preprocess(image)
        assert tensor.shape[3] <= 2048

    def test_normalization_range(self, ocr_model):
        """Pixel values are in [0, 1] range."""
        image = Image.new("L", (200, 40), color=200)
        tensor, _ = ocr_model.preprocess(image)
        assert tensor.min() >= 0.0
        assert tensor.max() <= 1.0

    def test_output_shape(self, ocr_model):
        """Output tensor has shape (1, 1, 128, width)."""
        image = Image.new("L", (300, 50))
        tensor, _ = ocr_model.preprocess(image)
        assert tensor.shape[0] == 1  # batch
        assert tensor.shape[1] == 1  # channel
        assert tensor.shape[2] == 128  # height

    def test_step_images_returned(self, ocr_model):
        """Preprocessing returns intermediate step images for visualization."""
        image = Image.new("RGB", (300, 50))
        _, step_images = ocr_model.preprocess(image)
        assert len(step_images) >= 3  # grayscale, resized, padded


class TestCTCDecode:
    def test_blank_removal(self, ocr_model):
        """Blank tokens (idx 0) are removed from output."""
        # Simulate logits where most timesteps predict blank (0)
        # but a few predict actual characters
        logits = np.full((10, 1, 82), -10.0, dtype=np.float32)
        logits[3, 0, 5] = 0.0   # char at idx 5
        logits[:, 0, 0] = -1.0  # blanks have moderate probability
        logits[3, 0, 0] = -10.0 # except at position 3
        text, confidences = ocr_model._ctc_decode_with_confidence(logits)
        assert "<PAD>" not in text

    def test_consecutive_collapse(self, ocr_model):
        """Repeated consecutive non-blank chars are collapsed to one."""
        logits = np.full((6, 1, 82), -10.0, dtype=np.float32)
        char_idx = 5
        for t in range(6):
            logits[t, 0, char_idx] = 0.0  # same char at every timestep
        text, _ = ocr_model._ctc_decode_with_confidence(logits)
        assert len(text) == 1  # collapsed to single character

    def test_confidence_range(self, ocr_model):
        """All confidence values are between 0 and 1."""
        logits = np.random.randn(20, 1, 82).astype(np.float32)
        _, confidences = ocr_model._ctc_decode_with_confidence(logits)
        for c in confidences:
            assert 0.0 <= c <= 1.0

    def test_empty_on_all_blanks(self, ocr_model):
        """All-blank logits produce empty string."""
        logits = np.full((10, 1, 82), -10.0, dtype=np.float32)
        logits[:, 0, 0] = 0.0  # blank wins at every step
        text, confidences = ocr_model._ctc_decode_with_confidence(logits)
        assert text == ""
        assert len(confidences) == 0


class TestEndToEnd:
    def test_predict_returns_expected_types(self, ocr_model):
        """predict() returns (str, list[float], float)."""
        image = Image.new("L", (400, 60), color=128)
        text, confidences, elapsed_ms = ocr_model.predict(image)
        assert isinstance(text, str)
        assert isinstance(confidences, list)
        assert isinstance(elapsed_ms, float)
        assert elapsed_ms > 0

    def test_predict_on_sample_image(self, ocr_model):
        """Smoke test: sample image produces non-empty prediction."""
        # Use a real sample if available, else a synthetic image
        image = Image.new("L", (600, 80), color=200)
        text, confidences, _ = ocr_model.predict(image)
        assert isinstance(text, str)  # may or may not be empty on blank image

    def test_inference_time_reasonable(self, ocr_model):
        """Inference takes less than 10 seconds on Mac CPU."""
        image = Image.new("L", (800, 128), color=128)
        _, _, elapsed_ms = ocr_model.predict(image)
        assert elapsed_ms < 10000  # 10 seconds
```

### Then implement: `demos/text-ocr/model.py`

```python
import json
import time
import numpy as np
import onnxruntime as ort
from PIL import Image


class OCRInference:
    """Handwritten text line recognition using ONNX Runtime."""

    def __init__(self, model_path: str, mappings_path: str) -> None:
        self.session = ort.InferenceSession(
            model_path, providers=["CPUExecutionProvider"]
        )
        with open(mappings_path) as f:
            mappings = json.load(f)
        self.idx_to_char: dict[int, str] = {
            int(k): v for k, v in mappings["idx_to_char"].items()
        }
        self.blank_idx = 0  # <PAD> is the CTC blank token
        self.fixed_height: int = mappings["fixed_height"]  # 128
        self.max_width: int = mappings["max_width"]  # 2048

    def preprocess(self, image: Image.Image) -> tuple[np.ndarray, list[Image.Image]]:
        """Convert input image to model-ready tensor. Returns (tensor, step_images)."""
        step_images: list[Image.Image] = []

        # 1. Grayscale
        gray = image.convert("L")
        step_images.append(gray.copy())

        # 2. Resize height to 128, maintain aspect ratio
        w, h = gray.size
        new_h = self.fixed_height
        new_w = int(w * (new_h / h))
        resized = gray.resize((new_w, new_h), Image.LANCZOS)
        step_images.append(resized.copy())

        # 3. Cap or pad width
        if new_w > self.max_width:
            resized = resized.resize((self.max_width, new_h), Image.LANCZOS)
            new_w = self.max_width
        arr = np.array(resized, dtype=np.float32) / 255.0
        if new_w < self.max_width:
            padded = np.zeros((new_h, self.max_width), dtype=np.float32)
            padded[:, :new_w] = arr
            arr = padded
        step_images.append(Image.fromarray((arr * 255).astype(np.uint8)))

        # 4. Shape: (1, 1, 128, width)
        tensor = arr[np.newaxis, np.newaxis, :, :]
        return tensor, step_images

    def predict(self, image: Image.Image) -> tuple[str, list[float], float]:
        """Run full inference pipeline. Returns (text, per_char_confidences, elapsed_ms)."""
        tensor, _ = self.preprocess(image)
        start = time.perf_counter()
        logits = self.session.run(None, {"image": tensor})[0]
        elapsed_ms = (time.perf_counter() - start) * 1000
        text, confidences = self._ctc_decode_with_confidence(logits)
        return text, confidences, elapsed_ms

    def _ctc_decode_with_confidence(
        self, logits: np.ndarray
    ) -> tuple[str, list[float]]:
        """
        Greedy CTC decode with per-character confidence extraction.
        logits shape: (seq_len, batch=1, num_classes) — log-softmax output.
        """
        logits_2d = logits[:, 0, :]  # (seq_len, num_classes)
        pred_indices = np.argmax(logits_2d, axis=1)  # (seq_len,)
        probs = np.exp(logits_2d)  # convert log-probs to probs

        chars: list[str] = []
        confidences: list[float] = []
        prev_idx = -1
        for t, idx in enumerate(pred_indices):
            if idx == self.blank_idx:
                prev_idx = idx
                continue
            if idx == prev_idx:
                continue  # collapse consecutive duplicates
            char = self.idx_to_char.get(int(idx), "")
            if char and char not in ("<PAD>", "<UNK>"):
                chars.append(char)
                confidences.append(float(probs[t, idx]))
            prev_idx = idx

        return "".join(chars), confidences
```

**Note on CTC decode**: The original `evaluation.py` does NOT properly implement CTC decoding — it just maps argmax indices to chars without collapsing consecutive duplicates or removing blanks. Our implementation fixes this.

**Run tests**: `cd demos/text-ocr && uv run pytest tests/test_model.py -v` — all must pass before proceeding.

---

## Step 3: Project Scaffolding

**Agent: `backend-dev`. Sequential after Step 2.**

### `demos/text-ocr/pyproject.toml`
```toml
[project]
name = "portfolio-demo-ocr"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "streamlit>=1.30",
    "onnxruntime>=1.17",
    "numpy>=1.26",
    "Pillow>=10.0",
    "streamlit-drawable-canvas>=0.9",
]

[project.optional-dependencies]
export = ["torch>=2.1", "onnx>=1.15"]
dev = ["pytest>=8.0"]
```

### `demos/text-ocr/.streamlit/config.toml`
```toml
[server]
headless = true
port = 8502
enableCORS = false
maxUploadSize = 5

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#6366f1"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#e2e8f0"
font = "sans serif"
```

### `demos/text-ocr/assets/`
- 4-5 sample handwriting line images (from IAM dataset or hand-photographed)
- `samples.json`: `[{"file": "sample_1.png", "expected": "the quick brown fox"}, ...]`
- These provide instant-try capability for visitors

### `demos/text-ocr/tests/__init__.py`
Empty file for pytest discovery.

---

## Step 4: Streamlit App + Tests

**Agents: `design` (UI layout) + `backend-dev` (implementation). Can run in parallel with Step 5.**

### Write tests first: `demos/text-ocr/tests/test_app.py`

```python
import json
import os
import pytest


def test_sample_images_exist():
    """All files referenced in samples.json exist on disk."""
    with open("assets/samples.json") as f:
        samples = json.load(f)
    for sample in samples:
        path = os.path.join("assets", sample["file"])
        assert os.path.exists(path), f"Missing sample image: {path}"


def test_model_files_exist():
    """ONNX model and mappings files exist."""
    assert os.path.exists("models/ocr_lstm_int8.onnx"), "ONNX model missing"
    assert os.path.exists("models/mappings.json"), "Mappings file missing"


def test_model_loads():
    """OCRInference initializes without error."""
    from model import OCRInference
    model = OCRInference(
        model_path="models/ocr_lstm_int8.onnx",
        mappings_path="models/mappings.json",
    )
    assert model.session is not None
    assert len(model.idx_to_char) == 82


def test_app_imports():
    """app.py can be imported without runtime errors."""
    # This catches import-time issues (missing deps, syntax errors)
    import importlib
    spec = importlib.util.find_spec("app")
    assert spec is not None
```

### Create `demos/text-ocr/app.py` (~180 lines)

**Sidebar:**
- Model card: architecture (CNN + BiLSTM + CTC), training data (IAM Handwriting Dataset), vocabulary (82 chars), model size (12 MB INT8 ONNX), inference time (~2s on Pi)
- "How CTC Decoding Works" expander with brief explanation
- "Limitations" expander: single text line only, English only, trained on IAM-style handwriting, no text detection

**Main area — 3 tabs:**
1. **Upload**: `st.file_uploader` accepting jpg/png, max 5MB. Shows uploaded image preview. "Recognize" button triggers inference.
2. **Draw**: `st_canvas` from `streamlit-drawable-canvas` — white stroke on dark background, approximately 600x128px. "Clear Canvas" and "Recognize" buttons.
3. **Try Samples**: Grid of clickable sample images loaded from `assets/samples.json`. Click triggers inference with that image. Show expected text alongside prediction.

**Results section** (rendered below tabs after inference):
- Predicted text displayed in large monospace font
- Per-character confidence visualization: colored rectangles under each character (green >= 0.8, yellow 0.5-0.8, red < 0.5)
- Average confidence as a percentage
- Preprocessing pipeline visualization: 3 images in columns (Grayscale -> Resized -> Padded)
- Inference time in milliseconds

**Run all tests**: `cd demos/text-ocr && uv run pytest tests/ -v`

---

## Step 5: Infrastructure

**Agent: `devops`. Can run in parallel with Steps 1-4 (no dependencies).**

### Nginx — modify `deploy/nginx/portfolio.conf`
Insert before the SPA `location /` block:
```nginx
# Handwritten text recognition demo — Streamlit on port 8502
# Requires WebSocket upgrade headers for Streamlit's internal communication
location /demo/ocr/ {
    proxy_pass http://127.0.0.1:8502/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 60s;
    proxy_connect_timeout 5s;
}

# Streamlit internal static assets
location /demo/ocr/_stcore/ {
    proxy_pass http://127.0.0.1:8502/_stcore/;
}
```

**Critical**: Streamlit ExecStart must include `--server.baseUrlPath=/demo/ocr` so internal routing matches the nginx prefix.

### systemd — create `deploy/systemd/portfolio-demo-ocr.service`
Follow the `portfolio-backend.service` pattern exactly:
- `User=rahser`, `Group=rahser`
- `Restart=on-failure`, `RestartSec=5`
- `MemoryMax=512M`, `CPUQuota=75%`
- `ProtectHome=read-only`, `ProtectSystem=strict`, `NoNewPrivileges=true`, `PrivateTmp=true`
- `ReadWritePaths=/home/rahser/portfolio/demos/text-ocr`
- `WorkingDirectory=/home/rahser/portfolio/demos/text-ocr`
- `ExecStart=/home/rahser/portfolio/demos/text-ocr/.venv/bin/streamlit run app.py --server.port=8502 --server.headless=true --server.baseUrlPath=/demo/ocr --server.enableCORS=false --server.maxUploadSize=5`
- `StandardOutput=journal`, `SyslogIdentifier=portfolio-demo-ocr`

### Deploy script — extend `deploy/scripts/deploy.sh`
Add after existing backend sync:
```bash
# Step: Sync OCR demo dependencies
cd "${REPO_DIR}/demos/text-ocr" && uv sync --frozen
```
Add to service restart section:
```bash
sudo systemctl restart portfolio-demo-ocr
```
Add to health check section:
```bash
curl -sf http://127.0.0.1:8502/_stcore/health
```

### Update metadata files
- **`demos/text-ocr/SPEC.md`**: Rewrite to say "Handwritten Text Line Recognition" (not "OCR Pipeline"). Describe actual capabilities: single text line input, CNN+BiLSTM+CTC architecture, 82-char English vocab, per-character confidence. State limitations: no text detection, no bounding boxes, no multi-line support.
- **`backend/data/seed.json`**: Update the `text-ocr` entry — title to "Handwritten Text Recognition", description to mention CNN+BiLSTM, IAM dataset, ONNX Runtime, per-character confidence.
- **`frontend/src/components/ProjectCard.tsx`**: Verify `demo_url` renders as a working anchor tag pointing to `/demo/ocr`. Use the `/frontend-design` skill if changes are needed.

---

## Step 6: Integration Test + Documentation Updates

**Agent: main orchestrator. Sequential — requires all prior steps complete.**

### Full test suite
```bash
cd demos/text-ocr && uv run pytest tests/ -v
```
All tests must be green.

### Manual Streamlit testing
```bash
cd demos/text-ocr && uv run streamlit run app.py --server.port=8502
```
Verify in browser at `http://localhost:8502`:
- File upload works with a JPG/PNG of handwritten text
- Canvas drawing produces predictions
- All sample images load and produce results
- Confidence bars render with correct colors
- Preprocessing visualization shows 3 stages
- Inference time is displayed
- Sidebar content is accurate

### Update `CLAUDE.md`
Add a new `## Demos` section:
```markdown
## Demos

Each demo lives in `demos/<name>/` with its own `pyproject.toml` managed by `uv`.

### Key Commands
- Install deps: `cd demos/<name> && uv sync`
- Run locally: `cd demos/<name> && uv run streamlit run app.py`
- Run tests: `cd demos/<name> && uv sync --group dev && uv run pytest tests/ -v`

### Architecture
- Streamlit apps proxied through Nginx with `--server.baseUrlPath=/demo/<name>`
- Each demo gets a systemd service (`deploy/systemd/portfolio-demo-<name>.service`)
- Model artifacts tracked via Git LFS (`.onnx` files — see `.gitattributes`)
- Nginx requires WebSocket upgrade headers for Streamlit

### Current Demos
| Demo | Port | Route | Status |
|------|------|-------|--------|
| Text OCR | 8502 | /demo/ocr | Active |
| EEG Generator | 8501 | /demo/eeg | Planned |
| Medical Chatbot | 8503 | /demo/chatbot | Planned |
| Bomberman RL | 8504 | /demo/bomberman | Planned |
```

### Update `.claude/project-status.md`
- Move Phase 2 items to "Completed" section
- Record decisions: ONNX INT8 quantization, proper CTC decode with confidence, no bounding boxes
- Note any issues for future phases

Once ready present this Pi Deployment points to the user as next steps.

### Pi deployment (when ready, ONLY TO BE DONE BY USER)
1. `git push` from Mac
2. On Pi: `git pull origin main`
3. `cd demos/text-ocr && uv sync --frozen`
4. Verify ONNX Runtime installed on aarch64: `uv run python -c "import onnxruntime; print(onnxruntime.get_device())"`
5. `sudo systemctl daemon-reload && sudo systemctl enable portfolio-demo-ocr && sudo systemctl start portfolio-demo-ocr`
6. `sudo systemctl status portfolio-demo-ocr` — confirm running
7. `sudo nginx -t && sudo systemctl reload nginx`
8. Test through cloudflared tunnel: visit `https://<domain>/demo/ocr`
9. `free -h` — verify RAM usage (~200-300MB for Streamlit + ONNX + model)

---

## Files Summary

| Action | File | Agent |
|--------|------|-------|
| Create | `demos/text-ocr/scripts/export_onnx.py` | backend-dev |
| Create | `demos/text-ocr/model.py` | backend-dev |
| Create | `demos/text-ocr/tests/__init__.py` | backend-dev |
| Create | `demos/text-ocr/tests/test_model.py` | backend-dev |
| Create | `demos/text-ocr/tests/test_app.py` | backend-dev |
| Create | `demos/text-ocr/app.py` | backend-dev + design |
| Create | `demos/text-ocr/pyproject.toml` | backend-dev |
| Create | `demos/text-ocr/.streamlit/config.toml` | backend-dev |
| Generate | `demos/text-ocr/models/ocr_lstm_int8.onnx` | backend-dev (export script) |
| Copy | `demos/text-ocr/models/mappings.json` | backend-dev |
| Create | `demos/text-ocr/assets/samples.json` + images | backend-dev |
| Create | `deploy/systemd/portfolio-demo-ocr.service` | devops |
| Create | `.gitattributes` | backend-dev |
| Modify | `deploy/nginx/portfolio.conf` | devops |
| Modify | `deploy/scripts/deploy.sh` | devops |
| Modify | `demos/text-ocr/SPEC.md` | backend-dev |
| Modify | `backend/data/seed.json` | backend-dev |
| Modify | `CLAUDE.md` | main |
| Modify | `.claude/project-status.md` | main |
| Verify | `frontend/src/components/ProjectCard.tsx` | frontend-dev |

---

## Agent Parallelization Map

```
             ┌─────────────────────────┐
             │ Step 1: ONNX Export      │
             │ [backend-dev agent]      │
             └────────────┬────────────┘
                          │
             ┌────────────▼────────────┐     ┌──────────────────────────┐
             │ Step 2: model.py + tests│     │ Step 5: Infrastructure   │
             │ [backend-dev agent]     │     │ [devops agent]           │
             └────────────┬────────────┘     │ nginx, systemd, deploy   │
                          │                  │ (NO dependency on 1-4)   │
             ┌────────────▼────────────┐     └──────────────────────────┘
             │ Step 3: Scaffolding     │
             │ pyproject, config, assets│
             └────────────┬────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
    ▼                     ▼                     ▼
┌──────────┐    ┌──────────────────┐   ┌────────────────┐
│ design   │    │ backend-dev      │   │ frontend-dev   │
│ agent:   │    │ agent:           │   │ agent:         │
│ UI layout│───▶│ app.py impl      │   │ ProjectCard    │
│ decisions│    │ + test_app.py    │   │ demo_url check │
└──────────┘    └────────┬─────────┘   └────────────────┘
                         │
             ┌───────────▼─────────────┐
             │ Step 6: Integration     │
             │ Full tests, CLAUDE.md,  │
             │ project-status.md       │
             │ [main orchestrator]     │
             └─────────────────────────┘
```

---

## Phases 3-7 Outline

### Phase 3: EEG Signal Generator (port 8501)
- Explore `project_refs/Generative-EEG-Augmentation/` for saved model weights (GAN, VAE, Diffusion)
- ONNX export: GAN generators are single forward passes (straightforward); diffusion models need the denoising loop in Python with only the U-Net exported as ONNX
- Streamlit app: model type selector, parameter sliders (channels, noise, duration), Plotly waveform visualization, real vs synthetic comparison
- Same infra pattern as OCR: systemd service, nginx block, deploy script extension
- TDD: test signal output shapes, frequency characteristics, ONNX model loading, Streamlit structure

### Phase 4: Medical Chatbot (port 8503)
- **Key decision**: retrieval-based (embeddings + FAISS, ~100MB) vs small LLM (TinyLlama Q4, ~700MB). Retrieval is safer for 4GB Pi RAM budget.
- If retrieval: pre-embed a PubMed/neuroscience corpus, store as FAISS index. Embedding model (~22MB ONNX, e.g., all-MiniLM-L6-v2). Query -> embed -> nearest neighbors -> format response.
- Streamlit chat UI using `st.chat_message` and `st.chat_input`, with curated example questions
- TDD: test retrieval accuracy, response formatting, edge cases (empty query, nonsense input)

### Phase 5: Bomberman RL (port 8504)
- **Key decision**: pre-recorded episodes vs live inference. Pre-recorded is simplest — RL policies are tiny but game rendering is CPU-heavy on headless Pi (no pygame display).
- Export policy network to ONNX (<5MB)
- Streamlit: animated game grid rendered as matplotlib frames, checkpoint selector (early/mid/late training), reward curves chart
- TDD: test policy network outputs valid actions, game state rendering, checkpoint loading

### Phase 6: Tier 2 Projects + Polish
- Add `/projects/:slug` detail page route in React frontend (use `/frontend-design` skill)
- Rich project pages: long description, architecture diagram (Mermaid), results gallery, GitHub links
- Expand `seed.json` with longer descriptions, `image_url`, `github_url` for all projects
- GitHub profile cleanup: archive forks, make tutorials private, pin top 6 repos

### Phase 7: Production Hardening
- Rate limiting via nginx `limit_req_zone` (shared across all demos)
- `/api/status` endpoint in FastAPI: systemd service states, RAM usage, per-demo last-request timestamps
- journald config: `MaxRetentionSec`, `SystemMaxUse` for log rotation
- Simple analytics: SQLite table recording page views and demo usage counts
- Load testing: verify behavior with multiple concurrent demo users
