# D0-POST-005 Development Evaluation Authorization

Status: AUTHORIZED

Purpose:
Evaluate the frozen POST-005 candidate checkpoints using ONLY
the frozen development dataset.

Authorized candidate checkpoints:
- local-checkpoints/d0-post005-development-seed42-step40.pt
- local-checkpoints/d0-post005-development-seed42-step80.pt
- local-checkpoints/d0-post005-development-seed42-step120.pt

Authorized candidate identities:
- step40: 1ea05d991a28381adc65c5af06fb1caf95ee52484d714c1ec4101275ee439796
- step80: 92a8f742c9f7a37170d908f39db0dd01f26b4d9bc370218bc435df16ef029b7f
- step120: 4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9

Frozen development dataset:
ml/data/d0_post004_dev.jsonl

Development SHA-256:
d54abaa83a4bbdcca313c557431fa5005e4490b7103f0f997ccd0c619f5c8a58

Candidate selection:
Development results may be used to select exactly one POST-005
candidate for any later separately authorized formal stage.

Training:
CLOSED

Additional training:
NOT AUTHORIZED

Formal dataset:
PROTECTED

Formal dataset identity:
28d95ae79d92fe767cf1fb16b984ccb3c33e79616d7cf20666bd6763ec2b7115

Formal evaluation:
NOT AUTHORIZED

Formal examples scored under this authorization:
ZERO

Important:
The final convenience checkpoint
local-checkpoints/d0-post005-development-seed42.pt
is not an additional candidate. It represents the same step-120
trajectory endpoint and is excluded from duplicate development scoring.

Training execution freeze SHA-256:
60ff1e414e9eb0eab737ba80e521d6a0aeef87160c0f2227b54a585e59125010

Training execution manifest SHA-256:
3ab543eaf8cbdb1f1c240ade455613312daef2a7c9b35efb9a331a46de11f6ae
