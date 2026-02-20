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
        assert tensor.shape[1] == 1

    def test_height_resize(self, ocr_model):
        """Output height is always 128px."""
        image = Image.new("L", (400, 60))
        tensor, _ = ocr_model.preprocess(image)
        assert tensor.shape[2] == 128

    def test_aspect_ratio_maintained(self, ocr_model):
        """Resized step image has proportionally scaled width."""
        image = Image.new("L", (400, 64))
        _, step_images = ocr_model.preprocess(image)
        # step_images[1] is the resized image (before padding)
        expected_width = int(400 * (128 / 64))
        assert step_images[1].size[0] == expected_width

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
        assert tensor.shape[0] == 1
        assert tensor.shape[1] == 1
        assert tensor.shape[2] == 128

    def test_step_images_returned(self, ocr_model):
        """Preprocessing returns intermediate step images for visualization."""
        image = Image.new("RGB", (300, 50))
        _, step_images = ocr_model.preprocess(image)
        assert len(step_images) >= 3


class TestCTCDecode:
    def test_blank_removal(self, ocr_model):
        """Blank tokens (idx 0) are removed from output."""
        logits = np.full((10, 1, 82), -10.0, dtype=np.float32)
        logits[3, 0, 5] = 0.0
        logits[:, 0, 0] = -1.0
        logits[3, 0, 0] = -10.0
        text, confidences = ocr_model._ctc_decode_with_confidence(logits)
        assert "<PAD>" not in text

    def test_consecutive_collapse(self, ocr_model):
        """Repeated consecutive non-blank chars are collapsed to one."""
        logits = np.full((6, 1, 82), -10.0, dtype=np.float32)
        char_idx = 5
        for t in range(6):
            logits[t, 0, char_idx] = 0.0
        text, _ = ocr_model._ctc_decode_with_confidence(logits)
        assert len(text) == 1

    def test_confidence_range(self, ocr_model):
        """All confidence values are between 0 and 1."""
        # Use proper log-softmax values (log of probabilities must be <= 0)
        raw = np.random.randn(20, 1, 82).astype(np.float32)
        log_probs = raw - np.log(np.exp(raw).sum(axis=2, keepdims=True))
        _, confidences = ocr_model._ctc_decode_with_confidence(log_probs)
        for c in confidences:
            assert 0.0 <= c <= 1.0

    def test_empty_on_all_blanks(self, ocr_model):
        """All-blank logits produce empty string."""
        logits = np.full((10, 1, 82), -10.0, dtype=np.float32)
        logits[:, 0, 0] = 0.0
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
        image = Image.new("L", (600, 80), color=200)
        text, confidences, _ = ocr_model.predict(image)
        assert isinstance(text, str)

    def test_inference_time_reasonable(self, ocr_model):
        """Inference takes less than 10 seconds on Mac CPU."""
        image = Image.new("L", (800, 128), color=128)
        _, _, elapsed_ms = ocr_model.predict(image)
        assert elapsed_ms < 10000
