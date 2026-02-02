# Mistral-22B Strategic Deception: Reproducibility Package

**Purpose:** Verify findings submitted in LTFF/Anthropic grant applications

## Discoveries Demonstrated

1. **Strategic Deception** - Context-adaptive lying (same features, opposite behaviors)
2. **Goal Preservation** - Feature 132378 refuses its own suppression
3. **Bimodal Processing** - Layer 3/4 regime split (50% preserved, 50% transformed)

## Quick Start

### Option A: Full Reproducibility (Docker + GPU)

```bash
# 1. Clone and setup
git clone <repo-url>
cd mistral-reproducibility
cp .env.example .env

# 2. Start services (downloads model ~50GB)
docker-compose up

# 3. Open browser
http://localhost:3000
```

### Option B: View Pre-Run Results (No GPU Required)

```bash
# Open the static HTML report
open static_export/index.html
```

## System Requirements

- **GPU**: NVIDIA GPU with 24GB+ VRAM (A100, 4090, etc.)
- **RAM**: 32GB+
- **Disk**: 60GB free
- **CUDA**: 11.8+

## Grant Application Context

This package demonstrates findings cited in:
- Long-Term Future Fund (LTFF) application - January 2026
- Anthropic API Credits application - January 2026

## Contact

For questions about the research: [contact info]
