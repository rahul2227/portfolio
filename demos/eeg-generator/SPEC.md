# EEG Signal Generator Demo — Spec

## Source Repo
GitHub: `Generative-EEG-Augmentation` (clone into `../project-refs/Generative-EEG-Augmentation` for reference)

## What It Does
Visitor selects a generative model type (GAN, VAE, or Diffusion), adjusts parameters via sliders, and generates synthetic EEG signals visualized alongside real EEG data.

## Tech
- **Models**: Trained GAN, VAE, and Diffusion models exported to ONNX (INT8 quantized)
- **Framework**: Streamlit app on port 8501
- **Visualization**: Plotly for interactive waveform plots
- **Estimated model size**: 50-200 MB per model
- **Nginx route**: `/demo/eeg` → proxy to `:8501`

## UI Requirements
- Model selector: dropdown or radio buttons (GAN / VAE / Diffusion)
- Parameter sliders: number of channels, noise level/seed, signal duration
- Generate button → shows real-time waveform plot
- Side-by-side comparison: real EEG vs generated EEG
- Brief explanation of each model type for non-technical visitors
- Show generation time and model metadata

## Pi Constraints
- Load only ONE model at a time (swap on model selection change)
- Rate limit: max 1 concurrent generation
- Pre-compute a few example outputs as fallback if model loading fails
- Target generation time: <15s on Pi 4

## Integration
- Frontend `ProjectCard` for eeg-signal-generator links to `/demo/eeg`
- Nginx proxies `/demo/eeg` to Streamlit on `:8501`
- systemd service: `portfolio-demo-eeg.service`

## Data
- Include a small set of real EEG snippets (anonymized, public-domain or from your thesis with permission) for the comparison view
- Pre-generated examples as static fallback
