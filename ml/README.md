# Denarixx ML Research Engine

This directory is portable Python code for the first D0 vertical slice. It does
not depend on Replit. The tiny development experiment uses an authored local
corpus, a character tokenizer, and a configurable causal transformer implemented
directly in PyTorch. Optional GPU support is detected at runtime.

Run a smoke experiment with:

```bash
python ml/run_experiment.py --max-steps 20 --seed 42 --checkpoint-dir /tmp/d0-checkpoints --run-id local
```