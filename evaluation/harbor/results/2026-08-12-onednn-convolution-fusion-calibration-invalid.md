# Invalid oneDNN convolution-fusion calibration

Date: 2026-08-12

The first one-attempt three-arm calibration is excluded. All three agents produced a semantically valid alternative repair that used a dedicated `user_residual` memory object and reordered it into the primitive-selected destination. The verifier incorrectly required the exact oracle spelling `reorder(user_dst, conv_dst)`, exited before writing a reward file, and Harbor therefore reported three `RewardFileNotFoundError` exceptions.

Invalid jobs retained for audit:

- `harbor-jobs/onednn-fusion-calibration-20260812-noskill`
- `harbor-jobs/onednn-fusion-calibration-20260812-previous`
- `harbor-jobs/onednn-fusion-calibration-20260812-candidate`

The verifier was corrected to accept implementation-equivalent reorder sources, to rely on numerical public and hidden checks, and to initialize a zero-reward file before validation. These runs must not be used for skill quality or efficiency conclusions.
