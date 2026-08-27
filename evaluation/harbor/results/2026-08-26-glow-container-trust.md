# GLOW Container Trust Repair

Date: 2026-08-26

## Cause

Docker Desktop routes container traffic through its Windows proxy. Avast Web/Mail Shield replaces public HTTPS leaf certificates with its locally generated root, which Windows trusts but the pinned Debian and Python Linux images do not. An unverified TLS probe inside the pinned Python base image confirmed that PyPI's presented certificate was issued by `Avast Web/Mail Shield Root`.

## Repair

- Export only the approved root certificate's public data from the Windows root store.
- Store its PEM representation as base64 in the user-scoped `UXL_EXTRA_CA_CERT_B64` environment variable.
- Pass the optional value through task-local Compose build arguments.
- Install it with `update-ca-certificates` before `pip` or `git` accesses HTTPS.
- Leave the value empty on unaffected workstations and GitHub-hosted runners.

TLS verification stays enabled. The repair does not use `trusted-host`, `GIT_SSL_NO_VERIFY`, or an insecure registry.

## Verification

Focused job `uxl-ca-four-oracle-0826` reran the four images that previously failed:

- `onedal-conversion-cost-benchmark`
- `onedal-table-orientation-regression`
- `onednn-benchdnn-no-ref-memory`
- `onedpl-stable-ordering-contract`

Result: four trials, zero exceptions, reward 1.0 on all four.

Full job `uxl-oracle-smoke-ca-fixed` then ran the unchanged standard 35-task oracle set with four-way concurrency. Result: 35 trials, zero errors, and reward 1.0 on every trial. The local job directories remain ignored working evidence; this summary is the retained review record.
