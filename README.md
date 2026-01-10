# neferteto

Prototype implementation for the Senet project described in `PROJECT_REQUIREMENTS.md`.

## Getting started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python play.py
```

The pygame window alternates turns between a human-controlled Light player (click a highlighted token to apply the current roll) and an automated Dark opponent that picks simple heuristic moves. Special house behaviour and rebirth rules follow the simplified Kendall interpretation captured in `senet/board.py`.
