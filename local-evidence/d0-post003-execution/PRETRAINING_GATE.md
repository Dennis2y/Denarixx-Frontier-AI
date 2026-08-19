# D0-POST-003 Final Pre-Training Gate

Status:

READY FOR SINGLE AUTHORIZED TRAINING RUN

Research HEAD:

33826f5

Base checkpoint SHA-256:

31038f7801ae64f99aad4ec88e7aaa276917be9dec84ef0944b121578a36ca97

Capability dataset SHA-256:

af597165dba3f3c76672004759aa2fcc899f32b0eccd7737bebdaa94651242fe

Training split SHA-256:

0ccc376954deba3c013789cde803cf230ee894bb91a7d2afd5105f2d0ee481a2

Development split SHA-256:

dc7beefa2615b664438c445f5b13f6a579ddd2fff55b91420e7fc29e9c47c45b

LM retention corpus SHA-256:

936b53855c5fa65cc408fb0b29108966445215a474ccfcce7ae7fe9f41fcc072

Training policy SHA-256:

47102d47ce786c4048b2a90ac2ad130d9cff89ebe942e75b6c0ac602d94333c8

Manifest SHA-256:

376101635c7fa24faa03e3aba45aba9970782a50c32100148d90a523a5f94294

Runner SHA-256:

370b303025fa25204292627b9c2e6d7770521772814c914c2c67cc05cf539a8c

Focused tests SHA-256:

c069b2166d4d3a86989e4ce69efab25007708faed955f56fc699897c095fbaf2

Frozen optimization:

- AdamW
- learning rate 1e-4
- weight decay 0.01
- gradient clip norm 1.0
- retention lambda 0.25
- SFT batch size 4
- LM batch size 4
- global seed 42
- SFT generator seed 42
- LM generator seed 43
- exactly 20 optimizer steps
- candidate fixed at step 20
- fresh optimizer state
- no scheduler
- no warmup
- no early stopping
- no hyperparameter search
- no seed search
- no intermediate candidate selection

Development policy:

The frozen POST-003 development set has not been used
for gradient optimization and has not yet been observed.

Historical evaluation policy:

D0-EVAL-001 and D0-EVAL-002 V4 remain frozen historical
confirmation evaluations and are not candidate-selection
datasets for POST-003.

Authorization:

Exactly one POST-003 training run is authorized after
this gate.

The resulting step-20 checkpoint becomes the fixed
POST-003 candidate regardless of its observed result.
