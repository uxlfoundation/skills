# UXL Skills Evaluator Dashboard

Public-facing control-room view for the UXL Foundation skills evaluator. It shows the current skill and Harbor-task inventory, available execution lanes, the evidence chain for the Windows/WSL Intel GPU lane, and the project definition of done.

The dashboard intentionally exposes only sanitized summary evidence. Raw Harbor job records, machine provenance, and runner logs remain in the private runner-control repository or on the operator workstation.

## Run locally

Requires Node.js 22.13 or newer.

From `evaluation/dashboard` in the `uxlfoundation/skills` checkout:

```powershell
npm ci
npm run dev
```

The default local URL is `http://localhost:3000/`.

## Validate

```powershell
npm run lint
npm test
```

`npm test` performs a production build and checks the rendered dashboard contract.

## Deployment

The public dashboard is published at <https://uxlfoundation.github.io/skills/> with GitHub Pages. The repository workflow builds this directory on a GitHub-hosted runner, verifies the static export, and deploys it after changes reach `main`. Pull requests run the same build and checks without publishing.

Pages receives only `dist/client`. Keep raw Harbor records, runner logs, credentials, and unsanitized machine provenance out of the dashboard source and public build.

The navigation and footer use the official color icon from the [UXL Foundation artwork repository](https://github.com/uxlfoundation/artwork/blob/main/foundation/uxl-foundation-icon-color.svg). UXL marks remain subject to the Linux Foundation trademark policy referenced by that repository.

## Evidence model

- Git commit: immutable evaluator source revision.
- Runner lane: declared hardware and software execution environment.
- Hardware provenance: device interface, Level Zero visibility, and toolchain metadata.
- Harbor result: task reward and retained job artifact.
- Dashboard: sanitized, human-readable summary linked back to reviewable source.
