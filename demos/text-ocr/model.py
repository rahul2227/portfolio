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
