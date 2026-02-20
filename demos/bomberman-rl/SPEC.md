# Bomberman RL Agent Demo — Spec

## Source Repos
GitHub: `bomberman_game` + `bomberman_rl_RBN` (clone both into `../project-refs/` for reference)

## What It Does
Visitor watches a trained RL agent play Bomberman. Can select between different training checkpoints to see the agent's learning progression.

## Tech
- **Model**: Trained policy network exported to ONNX
- **Framework**: Streamlit app on port 8504
- **Estimated model size**: 10-50 MB (RL policies are small)
- **Nginx route**: `/demo/bomberman` → proxy to `:8504`

## UI Requirements
- Game visualization: rendered grid showing agent, enemies, bombs, walls
- Checkpoint selector: slider or dropdown to pick training stage (early/mid/late)
- Play/pause/step controls
- Stats overlay: score, steps survived, bombs placed
- Training curves chart: reward over episodes
- Brief explanation of the RL approach (state representation, reward shaping)

## Rendering Approach (decide after reviewing source repos)

### Option A: Matplotlib animation in Streamlit (simpler)
- Pre-render game episodes as frame sequences
- Animate in Streamlit with st.image updates
- Lower fidelity but much simpler

### Option B: Browser-rendered game (cooler, harder)
- Lightweight JS canvas renderer in frontend
- WebSocket or API to get agent actions from Pi
- Real-time feel

### Option C: Pre-recorded GIFs/videos with live stats
- Record episodes at different checkpoints
- Display as video with synchronized stats
- Easiest, still effective

## Pi Constraints
- RL policy inference is fast (<1ms per step), main cost is rendering
- Pre-compute episodes if using Option A or C
- Rate limit: max 2 concurrent viewers

## Integration
- Frontend `ProjectCard` for bomberman-rl links to `/demo/bomberman`
- Nginx proxies `/demo/bomberman` to Streamlit on `:8504`
- systemd service: `portfolio-demo-bomberman.service`
