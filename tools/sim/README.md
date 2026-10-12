# Engine reference (`tools/sim`)

`engine_reference.py` is the reference of `locator_engine` (CLAUDE.md §7): the Bayesian probability map of
`docs/research/sim/circle_prob_sim.py`, generalised from a rectangle to any rubble outline, and the golden
fixtures the Dart engine must reproduce (probabilities per 0.25 m cell within 1e-6, 50 % / 90 % areas
exactly).

```bash
/opt/homebrew/bin/python3.12 -m venv tools/sim/.venv
tools/sim/.venv/bin/pip install numpy==2.3.3 scipy==1.16.2
tools/sim/.venv/bin/python tools/sim/engine_reference.py ../packages/locator_engine/test/fixtures
```

A model or profile change updates this script, the fixtures and the Dart engine in the same change,
with a written justification.
