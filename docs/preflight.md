# Preflight reports

`skill-kit doctor` resolves the connector environment and reports what it found.
Attaching one to an issue turns "connectors don't work" into something actionable.

The report contains:

- resolved public and target base URLs for each service pair
- whether each pair is complete
- 12-character SHA-256 fingerprints of the credentials, never their values
- skill-kit version, Python version, platform

See <https://pplx-skill-kit.vercel.app/docs/preflight> for the collector side.
