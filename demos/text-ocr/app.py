"""Handwritten Text Recognition — Streamlit demo app."""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Handwritten Text Recognition",
    page_icon="✍️",
    layout="wide",
)

st.markdown(
    '<a href="/projects/text-ocr" style="color: #a1a1aa; text-decoration: none; font-size: 0.875rem;">'
    "&larr; Back to Project</a>",
    unsafe_allow_html=True,
)

# Sidebar — model card
with st.sidebar:
    st.header("Model Card")
    st.markdown(
        "| Property | Value |\n|---|---|\n"
        "| Architecture | CNN + BiLSTM + CTC |\n"
        "| Training data | IAM Handwriting Dataset |\n"
        "| Vocabulary | 82 characters |\n"
        "| Model size | ~12 MB (INT8 ONNX) |\n"
        "| Inference | ~2s on Raspberry Pi 4 |"
    )
    with st.expander("How CTC Decoding Works"):
        st.markdown(
            "Connectionist Temporal Classification (CTC) lets the model output a "
            "sequence without knowing the alignment between input frames and output "
            "characters. At each time step the network predicts a distribution over "
            "all characters plus a *blank* token. Greedy decoding picks the most "
            "likely token per step, collapses consecutive duplicates, and removes "
            "blanks — producing the final string."
        )
    with st.expander("Limitations"):
        st.markdown(
            "- Processes a **single text line** at a time — no paragraph support.\n"
            "- **English only** — trained on the IAM Handwriting dataset.\n"
            "- Best results on **IAM-style** cursive/print handwriting.\n"
            "- No text detection — input must be cropped to one line."
        )


@st.cache_resource
def load_model():  # type: ignore[return]
    from model import OCRInference

    return OCRInference(
        model_path="models/ocr_lstm_int8.onnx",
        mappings_path="models/mappings.json",
    )


def render_results(
    text: str,
    confidences: list[float],
    elapsed_ms: float,
    step_images: list[Image.Image],
) -> None:
    """Display OCR results: predicted text, per-character confidence, and timing."""
    st.subheader("Result")
    st.markdown(
        f'<p style="font-family:monospace;font-size:1.6rem;letter-spacing:0.05em;">'
        f"{text}</p>",
        unsafe_allow_html=True,
    )
    if confidences and text:
        spans: list[str] = []
        for char, conf in zip(text, confidences):
            colour = "#22c55e" if conf >= 0.8 else ("#eab308" if conf >= 0.5 else "#ef4444")
            display = char if char != " " else "&nbsp;"
            spans.append(
                f'<span style="background:{colour};color:#0f172a;padding:2px 3px;'
                f'border-radius:3px;font-family:monospace;">{display}</span>'
            )
        st.markdown(" ".join(spans), unsafe_allow_html=True)
        avg_conf = sum(confidences) / len(confidences)
        st.markdown(
            f"**Average confidence:** {avg_conf:.1%} &nbsp;|&nbsp; "
            f"**Inference time:** {elapsed_ms:.0f} ms",
            unsafe_allow_html=True,
        )
    else:
        st.info("No characters recognised.")
    with st.expander("Preprocessing Pipeline"):
        cols = st.columns(len(step_images))
        for col, img, label in zip(cols, step_images, ["Grayscale", "Resized", "Padded"]):
            col.image(img, caption=label, use_container_width=True)


def _run_inference(image: Image.Image) -> None:
    """Run OCR and persist results in session state."""
    model = load_model()
    tensor, step_images = model.preprocess(image)
    start = time.perf_counter()
    logits = model.session.run(None, {"image": tensor})[0]
    elapsed_ms = (time.perf_counter() - start) * 1000
    text, confidences = model._ctc_decode_with_confidence(logits)
    st.session_state["ocr_result"] = {
        "text": text,
        "confidences": confidences,
        "elapsed_ms": elapsed_ms,
        "step_images": step_images,
    }


# Three tabs
tab_upload, tab_draw, tab_samples = st.tabs(["📤 Upload", "✏️ Draw", "🖼️ Try Samples"])

with tab_upload:
    st.markdown("Upload a cropped single-line handwriting image (JPG or PNG, max 5 MB).")
    uploaded = st.file_uploader(
        "Choose an image", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )
    if uploaded is not None:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded image", use_container_width=True)
        if st.button("Recognize", key="btn_upload"):
            with st.spinner("Running OCR..."):
                _run_inference(image)

with tab_draw:
    st.markdown("Draw a single line of handwritten text on the canvas below.")
    try:
        from streamlit_drawable_canvas import st_canvas

        canvas_result = st_canvas(
            fill_color="rgba(0,0,0,0)",
            stroke_width=4,
            stroke_color="#FFFFFF",
            background_color="#1e293b",
            height=150,
            width=700,
            drawing_mode="freedraw",
            key="canvas",
        )
        if st.button("Recognize", key="btn_draw"):
            if canvas_result.image_data is not None:
                rgba = canvas_result.image_data.astype(np.uint8)
                image = Image.fromarray(rgba, "RGBA").convert("RGB")
                with st.spinner("Running OCR..."):
                    _run_inference(image)
            else:
                st.warning("Draw something on the canvas first.")
    except ImportError:
        st.error("streamlit-drawable-canvas is not installed.")

with tab_samples:
    samples_path = Path("assets/samples.json")
    if samples_path.exists():
        with samples_path.open() as f:
            samples: list[dict] = json.load(f)
        for row_start in range(0, len(samples), 2):
            row_samples = samples[row_start : row_start + 2]
            cols = st.columns(len(row_samples))
            for col, sample in zip(cols, row_samples):
                img_path = Path("assets") / sample["file"]
                if img_path.exists():
                    col.image(str(img_path), use_container_width=True)
                col.markdown(f"*Expected:* `{sample['expected']}`")
                if col.button("Try this", key=f"sample_{sample['file']}"):
                    if img_path.exists():
                        with st.spinner("Running OCR..."):
                            _run_inference(Image.open(img_path).convert("RGB"))
                    else:
                        st.error(f"Image not found: {img_path}")
    else:
        st.error("assets/samples.json not found.")

# Render persisted results below tabs
if "ocr_result" in st.session_state:
    result = st.session_state["ocr_result"]
    st.divider()
    render_results(
        text=result["text"],
        confidences=result["confidences"],
        elapsed_ms=result["elapsed_ms"],
        step_images=result["step_images"],
    )
