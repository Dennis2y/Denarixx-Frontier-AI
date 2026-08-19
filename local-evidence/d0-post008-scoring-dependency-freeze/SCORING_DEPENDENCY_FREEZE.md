# DENARIXX D0-POST-008
## Scoring Dependency Freeze

Stage: D0-POST-008

Status: SCORING DEPENDENCIES FROZEN

This freeze binds the exact artifacts permitted for a
future separately authorized POST-008 formal evaluation.

### Sealed formal dataset

ml/data/d0_post008_formal.jsonl

SHA-256:

78ff74ea7103c52cee382cd87879a30bc1f9b65c16a800249c322303fa63d95b

Rows: 40

### Accepted baseline

local-checkpoints/d0-post003-capability-seed42.pt

SHA-256:

3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

### Retained candidate

local-checkpoints/d0-post005-development-seed42-step120.pt

SHA-256:

4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9

### Dependency adapter

ml/evaluation/d0_post008_dependencies.py

SHA-256:

50fd911f8e29286999d65af6e390be049e5729c31f808b298d3809373b21d128

### Adjudicator

ml/evaluation/d0_post008_adjudicator.py

SHA-256:

92d2d803be8d481caccf7cbf5a7758738094459d5ba8095ca95662e0cd427c0c

### Compatibility validator

ml/evaluation/d0_post008_compatibility.py

SHA-256:

63408b13e1cc832b74d68c7feffae6035194d68adc43978bb6061fd23b19cac7

### Execution harness

ml/evaluation/d0_post008_execution_harness.py

SHA-256:

f5268a25b034b4c69d980ae372ed5c632546b50725723feea73f0eeab572ea59

### Required future scoring topology

1. The sealed formal dataset identity must be verified.
2. The accepted baseline identity must be verified.
3. The retained candidate identity must be verified.
4. Exactly the same in-memory sealed rows must be supplied
   to baseline and candidate scoring.
5. The baseline must be scored first.
6. The baseline result must be persisted before candidate
   scoring begins.
7. The candidate must then be scored.
8. The candidate result must be persisted before comparison.
9. Adjudication must use the persisted baseline and candidate
   results.
10. Formal data must not be used for candidate selection.

### Execution state at freeze

- checkpoint bytes hashed: YES
- checkpoint deserialized: NO
- checkpoint metadata inspected: NO
- model instantiated: NO
- model inference executed: NO
- model scoring executed: NO
- training executed: NO
- formal exposure started: NO
- formal execution enabled: NO
- formal execution authorized: NO

This artifact freezes dependencies only.

It does NOT authorize formal exposure or checkpoint scoring.
