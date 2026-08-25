# UXL Evaluator Dashboard

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

Production deployment is managed with OpenAI Sites. `.openai/hosting.json` binds this directory to its existing Sites project. Publish the exact validated `uxlfoundation/skills` Git commit through the Sites version and deployment workflow; do not create a second Sites project.

## Evidence model

- Git commit: immutable evaluator source revision.
- Runner lane: declared hardware and software execution environment.
- Hardware provenance: device interface, Level Zero visibility, and toolchain metadata.
- Harbor result: task reward and retained job artifact.
- Dashboard: sanitized, human-readable summary linked back to reviewable source.
