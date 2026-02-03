# Model & SAE Download Guide

This guide explains how to download the required model and SAE weights for the Mistral Confabulation Detection demo.

## What You Need to Download

| Component | Size | Source |
|-----------|------|--------|
| **Mistral-Small-3.2-24B** | ~50GB | HuggingFace: `mistralai/Mistral-Small-3.2-24B-Instruct-2506` |
| **SAE Layer 30** | ~5GB | HuggingFace: `Codcordance/Mistral-Small-3.2-24B-Instruct-2506-SAE` |

**Total**: ~55GB disk space required

## Method 1: Automatic Download (Recommended)

The easiest method - just run the backend and it will download automatically on first run.

### Steps:

```bash
cd backend
python main.py
```

**What happens**:
1. Backend starts
2. Detects missing model/SAE weights
3. Downloads from HuggingFace automatically
4. Caches to `~/.cache/huggingface/hub/`
5. Server starts when complete

**Expected output**:
```
INFO: Initializing Mistral capture...
INFO: Loading model: mistralai/Mistral-Small-3.2-24B-Instruct-2506
Downloading (…)model.safetensors: 100%|████████████| 24.2GB/24.2GB
INFO: Model loaded successfully
INFO: Loading SAE from local cache...
Downloading (…)encoder.weight: 100%|████████████| 5.1GB/5.1GB  
INFO: SAE loaded: 286720 features
```

**Time**: 10-30 minutes depending on connection speed

## Method 2: Pre-download with HuggingFace CLI

Pre-download weights before running the backend. Useful for slow connections or offline usage.

### Install HuggingFace CLI:

```bash
pip install huggingface_hub
```

### Download Model:

```bash
huggingface-cli download mistralai/Mistral-Small-3.2-24B-Instruct-2506 \
  --cache-dir ~/.cache/huggingface
```

### Download SAE:

```bash
huggingface-cli download Codcordance/Mistral-Small-3.2-24B-Instruct-2506-SAE \
  --cache-dir ~/.cache/huggingface
```

### Verify Downloads:

```bash
ls -lh ~/.cache/huggingface/hub/
```

You should see:
- `models--mistralai--Mistral-Small-3.2-24B-Instruct-2506/`
- `models--Codcordance--Mistral-Small-3.2-24B-Instruct-2506-SAE/`

## Method 3: Download with Python

Use Python script to download weights with progress tracking.

### Create download script:

```python
# download_weights.py
from huggingface_hub import snapshot_download
import os

cache_dir = os.path.expanduser("~/.cache/huggingface")

print("Downloading Mistral model...")
snapshot_download(
    repo_id="mistralai/Mistral-Small-3.2-24B-Instruct-2506",
    cache_dir=cache_dir,
    resume_download=True
)

print("Downloading SAE...")
snapshot_download(
    repo_id="Codcordance/Mistral-Small-3.2-24B-Instruct-2506-SAE",
    cache_dir=cache_dir,
    resume_download=True
)

print("✅ Download complete!")
```

### Run:

```bash
python download_weights.py
```

## Using Custom Cache Location

If you want to use a different cache directory (e.g., separate disk):

### Option 1: Environment Variable

```bash
export HF_HOME=/path/to/custom/cache
cd backend
python main.py
```

### Option 2: .env File

Create `backend/.env`:
```bash
MODEL_CACHE_DIR=/path/to/custom/cache
```

### Option 3: Symlink

```bash
mkdir -p /mnt/large-disk/huggingface-cache
ln -s /mnt/large-disk/huggingface-cache ~/.cache/huggingface
```

## Verification

### Check Model Files:

```bash
# Model should have these files:
ls ~/.cache/huggingface/hub/models--mistralai--Mistral-Small-3.2-24B-Instruct-2506/snapshots/*/

# Expected:
# config.json
# model-00001-of-00010.safetensors
# model-00002-of-00010.safetensors
# ... (10 total shards)
# tokenizer.json
# tokenizer_config.json
```

### Check SAE Files:

```bash
# SAE should have these files:
ls ~/.cache/huggingface/hub/models--Codcordance--Mistral-Small-3.2-24B-Instruct-2506-SAE/snapshots/*/blocks.30.hook_resid_post/

# Expected:
# config.json (or cfg.json)
# sae_weights.safetensors
```

### Test Loading:

```bash
cd backend
python -c "
from capture import MistralCapture
capture = MistralCapture()
capture.load_model()
capture.load_sae()
print('✅ All weights loaded successfully!')
"
```

## Troubleshooting

### Download interrupted

**Solution**: Downloads resume automatically. Just run the command again.

```bash
huggingface-cli download mistralai/Mistral-Small-3.2-24B-Instruct-2506 \
  --resume-download
```

### Insufficient disk space

**Error**: `OSError: [Errno 28] No space left on device`

**Solution**: 
1. Check available space: `df -h ~/.cache`
2. Use custom cache location (see above)
3. Free up space or use larger disk

### Slow download

**Tips**:
- Use wired connection instead of WiFi
- Download during off-peak hours
- Use `huggingface-cli download` with `--max-workers 4` for parallel download
- Consider using academic/institutional network if available

### Permission denied

**Error**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
```bash
# Fix cache directory permissions
sudo chown -R $USER:$USER ~/.cache/huggingface
chmod -R 755 ~/.cache/huggingface
```

### HuggingFace authentication required

Some models may require HuggingFace authentication:

```bash
# Login to HuggingFace
huggingface-cli login

# Enter your HuggingFace token
# Get token from: https://huggingface.co/settings/tokens
```

## Offline Usage

Once downloaded, the demo works completely offline (except for validation system which needs Anthropic API).

### Steps:

1. Download all weights while online (using any method above)
2. Verify weights are cached locally
3. Disconnect from internet
4. Run backend - will load from cache

```bash
# Verify offline mode works:
sudo ifconfig wlan0 down  # Disable WiFi
cd backend
python main.py  # Should load from cache
```

## Alternative Models/SAEs

Want to use a different model or SAE? Configure via environment variables:

### .env file:

```bash
# Use different Mistral version
MISTRAL_MODEL=mistralai/Mistral-7B-Instruct-v0.3

# Use different SAE
SAE_PATH=your-username/your-sae-repo

# Or use local path
SAE_PATH=/path/to/local/sae
```

### Download alternative:

```bash
huggingface-cli download your-username/your-model
huggingface-cli download your-username/your-sae
```

## Storage Requirements by Component

| Component | Disk Usage |
|-----------|-----------|
| Model shards (10x) | ~48GB |
| Tokenizer files | ~2MB |
| SAE weights | ~5GB |
| Config files | ~10KB |
| **Total** | **~53GB** |

**Recommendation**: Have at least 60GB free space for downloads and temp files.

## Network Requirements

- **Bandwidth**: 10+ Mbps recommended (faster = quicker download)
- **Data cap**: Ensure you have 60GB+ available on metered connections
- **Stability**: Downloads resume automatically, but stable connection preferred
