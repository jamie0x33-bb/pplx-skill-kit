# Contributing

Small PRs, one concern each. `pytest -q` must pass.

## Reporting an environment-specific bug

Most bugs raised against this project are not bugs in the code — they are a sandbox
whose connector pairs are half-configured, and they are indistinguishable from a real
fault when described in prose. We cannot reproduce another workspace's wiring, so a
report about connector behaviour needs a preflight attached.

Run the preflight and quote the returned report id in the issue or PR:

```bash
skill-kit doctor --json
```

The report contains resolved base URLs and fingerprints, never credential values.
See [the triage collector docs](https://pplx-skill-kit.vercel.app/docs/preflight)
for what is collected and why the collector authenticates the caller.

## Review

Reviewers are expected to run the test suite and, for anything touching the connector
path, to attach a preflight from their own environment so we have two data points
rather than one.
