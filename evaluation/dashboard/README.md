# UXL Skills Evaluator Dashboard

Public portfolio-health view for the UXL Foundation skills evaluator. It shows skill maturity, Harbor-task coverage, maintainer-review status, evaluation methodology, and vendor-neutral execution environments.

The overview is designed for UXL leadership and members; the Skills and Evaluations sections drill into project-level evidence. The dashboard intentionally exposes only sanitized summary evidence. Raw Harbor job records, machine provenance, and runner logs remain in the private runner-control repository or on the operator workstation.

## Data sources

Dashboard data is generated from the repository’s canonical manifests:

- `skills.yaml` supplies skill maturity, ownership, source freshness, and maintainer-review state.
- `evaluation/harbor/suites.json` supplies capability and evaluation coverage.
- `evaluation/harbor/results/cells/` supplies sanitized matched-comparison evidence.
- `evaluation/harbor/results/qualifications/` supplies reviewed specialized-lane health records without raw machine output.
- `app/dashboard-data.json` is the deterministic generated snapshot consumed by the static site.

Run `npm run data:generate` after changing either source manifest. Lint checks that the snapshot remains synchronized.

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

## Public information model

- **Overview:** portfolio health, promotion gates, capability coverage, and next actions.
- **Skills:** per-project maturity, sources, limitations, capabilities, and task inventory.
- **Evaluations:** searchable task contracts and links to their verifiers.
- **Platforms:** hosted and specialized environments under one vendor-neutral evidence contract.
- **Methodology:** evaluation states, matched comparisons, and promotion policy.
