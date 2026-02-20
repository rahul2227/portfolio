"""
Export the OCR LSTM model to ONNX format and quantize to INT8.

Run from the demos/text-ocr/ directory:
    python scripts/export_onnx.py

Outputs:
    models/ocr_lstm.onnx        — full-precision ONNX (intermediate)
    models/ocr_lstm_int8.onnx   — INT8 quantized ONNX (final)
"""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
import torch.nn as nn
from onnxruntime.quantization import QuantType, quantize_dynamic

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# Script lives at demos/text-ocr/scripts/export_onnx.py
# Repo root is three levels up.
SCRIPT_DIR = Path(__file__).resolve().parent
DEMO_DIR = SCRIPT_DIR.parent                        # demos/text-ocr/
REPO_ROOT = DEMO_DIR.parent.parent                  # repo root

WEIGHTS_PATH = (
    REPO_ROOT
    / "project_refs"
    / "Text_OCR"
    / "models"
    / "LSTM"
    / "best_model_LSTM.pth"
)
SOURCE_MAPPINGS = (
    REPO_ROOT
    / "project_refs"
    / "Text_OCR"
    / "data_preprocessing"
    / "mappings_LSTM.json"
)

MODELS_DIR = DEMO_DIR / "models"
ONNX_PATH = MODELS_DIR / "ocr_lstm.onnx"
ONNX_INT8_PATH = MODELS_DIR / "ocr_lstm_int8.onnx"
MAPPINGS_DEST = MODELS_DIR / "mappings.json"

# ---------------------------------------------------------------------------
# Model hyper-parameters (must match training configuration)
# ---------------------------------------------------------------------------

FIXED_HEIGHT: int = 128
MAX_WIDTH: int = 2048
NUM_CLASSES: int = 82
HIDDEN_SIZE: int = 256
NUM_LSTM_LAYERS: int = 2
DROPOUT: float = 0.1
NUM_POOLING_LAYERS: int = 4

# ---------------------------------------------------------------------------
# Model architecture — copied inline so this script is self-contained.
# NOTE: The assert on height in CNNToRNN.forward has been removed because
#       ONNX tracing does not support Python asserts on dynamic tensor shapes.
# ---------------------------------------------------------------------------


class CNNFeatureExtractor(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.cnn = nn.Sequential(
            # Conv block 1
            nn.Conv2d(1, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # Conv block 2
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # Conv block 3
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # Conv block 4
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.cnn(x)


class CNNToRNN(nn.Module):
    """Reshape CNN spatial output into a sequence for the RNN.

    The assert on height present in the original source has been intentionally
    removed — ONNX tracing requires dynamic axes to flow without Python-level
    guard assertions.
    """

    def __init__(
        self,
        cnn_output_channels: int,
        fixed_height: int,
        num_pooling_layers: int = 4,
    ) -> None:
        super().__init__()
        self.fixed_height = fixed_height
        self.cnn_output_channels = cnn_output_channels
        self.num_pooling_layers = num_pooling_layers

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch_size, channels, height, width)
        batch_size, channels, height, width = x.size()

        # Permute to (width, batch_size, channels, height)
        x = x.permute(3, 0, 1, 2)
        # Flatten channels * height into the feature dimension
        x = x.contiguous().view(width, batch_size, channels * height)
        return x


class BidirectionalLSTM(nn.Module):
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        num_layers: int,
        num_classes: int,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            bidirectional=True,
            dropout=dropout,
        )
        self.fc = nn.Linear(hidden_size * 2, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (seq_len, batch_size, input_size)
        lstm_out, _ = self.lstm(x)          # (seq_len, batch_size, hidden_size * 2)
        logits = self.fc(lstm_out)          # (seq_len, batch_size, num_classes)
        return logits


class OCRModel(nn.Module):
    def __init__(
        self,
        fixed_height: int,
        fixed_width: int,
        num_classes: int,
        hidden_size: int = 256,
        num_lstm_layers: int = 2,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.cnn = CNNFeatureExtractor()
        self.cnn_to_rnn = CNNToRNN(
            cnn_output_channels=512,
            fixed_height=fixed_height,
        )
        self.rnn = BidirectionalLSTM(
            input_size=512 * (fixed_height // (2**NUM_POOLING_LAYERS)),
            hidden_size=hidden_size,
            num_layers=num_lstm_layers,
            num_classes=num_classes,
            dropout=dropout,
        )
        self.log_softmax = nn.LogSoftmax(dim=2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.cnn(x)          # (batch, 512, H', W')
        x = self.cnn_to_rnn(x)  # (W', batch, 512 * H')
        x = self.rnn(x)          # (W', batch, num_classes)
        x = self.log_softmax(x)  # (W', batch, num_classes)
        return x


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def build_model() -> OCRModel:
    """Instantiate OCRModel and load pre-trained weights."""
    print(f"Loading weights from: {WEIGHTS_PATH}")
    if not WEIGHTS_PATH.exists():
        raise FileNotFoundError(f"Weights file not found: {WEIGHTS_PATH}")

    model = OCRModel(
        fixed_height=FIXED_HEIGHT,
        fixed_width=MAX_WIDTH,
        num_classes=NUM_CLASSES,
        hidden_size=HIDDEN_SIZE,
        num_lstm_layers=NUM_LSTM_LAYERS,
        dropout=DROPOUT,
    )

    state_dict = torch.load(WEIGHTS_PATH, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()
    print("Weights loaded successfully.")
    return model


def export_onnx(model: OCRModel) -> None:
    """Trace and export the model to full-precision ONNX."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Dummy input: (batch=1, channels=1, height=128, width=512)
    dummy_input = torch.zeros(1, 1, FIXED_HEIGHT, 512)

    print(f"\nExporting ONNX model to: {ONNX_PATH}")
    torch.onnx.export(
        model,
        dummy_input,
        str(ONNX_PATH),
        opset_version=17,
        input_names=["image"],
        output_names=["logits"],
        dynamic_axes={
            "image": {0: "batch", 3: "width"},
            "logits": {0: "seq_len", 1: "batch"},
        },
        do_constant_folding=True,
        verbose=False,
        dynamo=False,
    )
    size_mb = ONNX_PATH.stat().st_size / (1024 * 1024)
    print(f"Full-precision ONNX export complete. File size: {size_mb:.1f} MB")


def quantize_int8() -> None:
    """Quantize the full-precision ONNX model to INT8."""
    print(f"\nQuantizing to INT8: {ONNX_INT8_PATH}")
    quantize_dynamic(
        str(ONNX_PATH),
        str(ONNX_INT8_PATH),
        weight_type=QuantType.QInt8,
    )
    size_mb = ONNX_INT8_PATH.stat().st_size / (1024 * 1024)
    print(f"INT8 quantization complete. File size: {size_mb:.1f} MB")


def validate(model: OCRModel) -> None:
    """Run 3 dummy inputs of different widths through PyTorch and ONNX.

    Asserts that outputs are numerically close (atol=1e-4) and prints the
    maximum absolute difference for each width.
    """
    print("\nValidating ONNX output against PyTorch...")

    session = ort.InferenceSession(
        str(ONNX_PATH),
        providers=["CPUExecutionProvider"],
    )

    test_widths = [512, 1024, 2048]

    for width in test_widths:
        dummy = torch.zeros(1, 1, FIXED_HEIGHT, width)

        with torch.no_grad():
            pt_output: np.ndarray = model(dummy).numpy()

        onnx_output: np.ndarray = session.run(
            ["logits"],
            {"image": dummy.numpy()},
        )[0]

        max_diff = float(np.max(np.abs(pt_output - onnx_output)))
        close = np.allclose(pt_output, onnx_output, atol=1e-4)

        status = "PASS" if close else "FAIL"
        print(
            f"  width={width:>4}  shape={list(onnx_output.shape)}"
            f"  max_abs_diff={max_diff:.6f}  [{status}]"
        )

        assert close, (
            f"ONNX output does not match PyTorch for width={width}. "
            f"Max absolute difference: {max_diff}"
        )

    print("All validation checks passed.")


def copy_mappings() -> None:
    """Copy the character mappings JSON to the demo models directory."""
    if not SOURCE_MAPPINGS.exists():
        raise FileNotFoundError(f"Mappings file not found: {SOURCE_MAPPINGS}")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_MAPPINGS, MAPPINGS_DEST)
    print(f"\nMappings copied to: {MAPPINGS_DEST}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 60)
    print("OCR LSTM — ONNX Export Pipeline")
    print("=" * 60)

    # 1. Copy character mappings
    copy_mappings()

    # 2. Build model and load weights
    model = build_model()

    # 3. Export to full-precision ONNX
    export_onnx(model)

    # 4. Validate ONNX output against PyTorch across multiple input widths
    validate(model)

    # 5. Quantize to INT8
    quantize_int8()

    print("\n" + "=" * 60)
    print("Export pipeline complete.")
    print(f"  Full-precision : {ONNX_PATH}")
    print(f"  INT8 quantized : {ONNX_INT8_PATH}")
    print(f"  Mappings       : {MAPPINGS_DEST}")
    print("=" * 60)
    print("\nThe intermediate full-precision ONNX file can be deleted")
    print("once you have verified the INT8 model in your application.")


if __name__ == "__main__":
    main()
