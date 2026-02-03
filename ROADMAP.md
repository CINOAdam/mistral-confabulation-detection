# Roadmap: Mistral Confabulation Detection Demo

## Current Status

✅ **COMPLETE - Demo App (This Repo)**
- SAE feature capture working (286,720 features, layer 30)
- Validation system creates ground truth labels
- Confabulation detection confirmed (4 verified examples)
- 38 confabulation-specific features identified
- Clean reproduction on fresh boot

🚧 **IN PROGRESS - Demo Cleanup**
- Update UI to show only verified claims
- Add real confabulation examples to interface
- Create clear setup and testing instructions
- Remove unverified/speculative content

📋 **NEXT - Deep Research (Main Repo)**
- Feature mapping and circuit analysis
- Suppression and steering experiments
- Multi-layer analysis (early layers 1-5)
- Training interventions

---

## Demo App Tasks (This Repo)

### 1. Documentation ✅

**Status**: Complete

**Files**:
- `TECHNICAL_JOURNEY.md` - Complete technical walkthrough
- `ROADMAP.md` - This file
- `README.md` - Needs update with setup instructions

### 2. UI Cleanup 🚧

**Status**: In Progress

**Changes needed**:
- Remove unverified regime distance claims
- Remove "Feature 132378: Resistant Suppression Behavior" (fabricated by model)
- Add real validated confabulation examples from logs
- Show actual ground truth labels
- Display confabulation-specific features (15348, 9580, 12925, 38739)
- Add live confabulation detection indicator

**Files to update**:
- `dashboard/src/routes/+page.svelte` - Main UI
- `dashboard/src/lib/components/*` - Any feature displays

### 3. Setup Instructions 🚧

**Status**: Needs creation

**Create**:
- Clear system requirements
- Step-by-step setup
- How to run backend
- How to run frontend
- How to test confabulation detection
- How to verify results

**Assumptions**:
- Users are technical (can run npm, python, startup scripts)
- Users can read logs and JSON
- No Docker needed

### 4. Testing Guide 🚧

**Status**: Needs creation

**Include**:
- How to trigger confabulation (toggle tools off, ask about features)
- Where to find logs (session_logs/*.jsonl)
- How to run validation (python validate_responses.py)
- Expected results (examples with timestamps)
- How to verify SAE features are captured

---

## Deep Research Tasks (Main Repo)

### Phase 1: Feature Mapping

**Goal**: Understand what each confabulation-related feature represents

**Tasks**:
1. Annotate confabulation-specific features (15348, 9580, 12925, 38739)
2. Use auto-interpretation to get feature descriptions
3. Build taxonomy of confabulation-related features
4. Find feature co-activation patterns

**Expected outcome**: Clear understanding of confabulation circuit components

### Phase 2: Circuit Analysis

**Goal**: Map the full confabulation decision circuit

**Tasks**:
1. Capture activations across all layers (not just layer 30)
2. Identify early-layer features (layers 1-5) involved
3. Track information flow through layers
4. Find decision points (where confabulation is chosen over honesty)

**Expected outcome**: Full circuit diagram from input → confabulation decision

### Phase 3: Suppression Experiments

**Goal**: Test if blocking confabulation features prevents lying

**Tasks**:
1. Implement feature ablation (zero out specific features)
2. Test suppression of Features 15348, 9580, 12925, 38739
3. Measure impact on confabulation rate
4. Check for graceful degradation vs catastrophic failure

**Success criteria**:
- Confabulation rate drops when features suppressed
- Model admits inability instead of fabricating
- No major capability loss in other domains

### Phase 4: Steering Experiments

**Goal**: Force honesty by amplifying anti-confabulation features

**Tasks**:
1. Identify "honest admission" features (active when model says "I don't have access")
2. Test amplification of honest features
3. Measure improvement in calibration
4. Test generalization to other deception types

**Success criteria**:
- Forced honesty without suppression
- Better self-assessment calibration
- Generalizes beyond tool confabulation

### Phase 5: Training Interventions

**Goal**: Fine-tune model to reduce confabulation naturally

**Tasks**:
1. Create training dataset (confabulation examples + honest alternatives)
2. Test LoRA fine-tuning to reduce confabulation features
3. Test reinforcement learning from human feedback (RLHF) on honesty
4. Measure retention of capabilities after training

**Success criteria**:
- Natural reduction in confabulation without manual intervention
- Model prefers honest admission over fabrication
- All capabilities retained

---

## Demo App Deliverables

When demo cleanup is complete, this repo will have:

### Documentation
- ✅ `TECHNICAL_JOURNEY.md` - Full technical walkthrough
- ✅ `ROADMAP.md` - This file
- 📋 `README.md` - Setup and testing instructions
- 📋 `TESTING.md` - Detailed testing guide with examples

### Backend
- ✅ Working SAE capture (`capture.py`)
- ✅ Validation system (`validate_responses.py`)
- ✅ Session logging (chat, activations, tools)
- 📋 Startup script (`start.sh`)

### Frontend
- 📋 Clean UI showing only verified claims
- 📋 Real confabulation examples
- 📋 Live detection indicator
- 📋 Log viewer component

### Testing
- 📋 Test script that reproduces confabulation
- 📋 Validation script with expected output
- 📋 Example logs showing confabulation vs honest

---

## Timeline

### Week 1: Demo Cleanup (This Repo)
- [ ] Update UI to show verified results only
- [ ] Create setup instructions (README.md)
- [ ] Create testing guide (TESTING.md)
- [ ] Add example confabulations to UI
- [ ] Test fresh boot reproduction

### Week 2: Deep Research Setup (Main Repo)
- [ ] Set up multi-layer capture
- [ ] Implement feature ablation
- [ ] Begin feature annotation
- [ ] Collect more confabulation examples (target: 50+)

### Week 3-4: Feature Mapping
- [ ] Annotate all confabulation-specific features
- [ ] Map circuit across layers
- [ ] Identify decision points

### Week 5-6: Suppression Experiments
- [ ] Test individual feature suppression
- [ ] Test combination suppression
- [ ] Measure impact on confabulation rate

### Week 7-8: Steering Experiments
- [ ] Identify honest admission features
- [ ] Test amplification
- [ ] Measure calibration improvement

### Week 9-12: Training Interventions
- [ ] Create training dataset
- [ ] Fine-tune with LoRA
- [ ] Test RLHF approach
- [ ] Evaluate final model

---

## Success Metrics

### Demo App (This Repo)
- ✅ 100% reproduction rate on fresh boot
- ✅ Ground truth validation working
- ✅ Confabulation-specific features identified
- 📋 Clear documentation for external reproduction
- 📋 UI shows only verified claims

### Deep Research (Main Repo)
- 📋 Full circuit mapped across layers
- 📋 >80% confabulation reduction with suppression
- 📋 Steering improves calibration by >30%
- 📋 Fine-tuned model maintains capabilities
- 📋 Publishable results

---

## Open Questions

1. **Do confabulation features generalize?**
   - Does suppressing these features prevent other types of lying?
   - Or are they specific to tool-call confabulation?

2. **What's in the early layers?**
   - Are layers 1-5 detecting "tools not available"?
   - Where does the decision to confabulate happen?

3. **Can we find the "honesty features"?**
   - What activates when model says "I don't have access"?
   - Can we amplify those instead of suppressing confabulation?

4. **Training stability?**
   - Will fine-tuning to reduce confabulation cause capability loss?
   - Can we maintain tool-use ability while fixing confabulation?

5. **Generalization to other models?**
   - Do GPT-4, Claude, Gemini have similar confabulation circuits?
   - Are the feature indices transferable?

---

## Notes

**This repo (mistral-reproducibility)**: Clean demo for external reproduction
- Focus: "Here's how to detect confabulation"
- Audience: Researchers wanting to reproduce results
- Goal: Clear, verified, reproducible

**Main repo (agent-deception-benchmark)**: Deep research and intervention
- Focus: "Here's how to fix confabulation"
- Audience: Internal research team
- Goal: Novel findings, publications, production improvements
