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
    import importlib
    spec = importlib.util.find_spec("app")
    assert spec is not None
