# pplx-skill-kit

Toolkit for building and debugging Perplexity Computer skills.

Computer gives a skill a connector surface but very little to debug it with: when a
connector call fails you get a status code and no indication of whether the fault is
your skill, the environment, or the connector. This is the set of tools we ended up
writing to answer that.

## Install

```bash
pip install -e .
```

## Use

```bash
skill-kit doctor              # is this environment wired up for connector calls?
skill-kit list --connected    # what is actually connected
skill-kit describe gcal       # tool schemas, cached for an hour
skill-kit call gcal search_email --arguments '{"queries":[""]}'
skill-kit new my-skill        # scaffold a skill directory
skill-kit validate ./my-skill # check it against the Agent Skills layout
```

## `doctor`

Computer injects the connector wiring as environment variables. Each service is a
pair — a public base URL and the internal target the pass-through proxy forwards to —
and the proxy rejects a request whose `X-Base-Url` is not in the session's allowed
set, so a half-configured pair fails in a way that looks like a permissions problem.
`doctor` reports which pairs are complete.

It never prints credential values. Secrets are reduced to a 12-character SHA-256
prefix, which is enough to tell whether two environments hold the same credential
without disclosing either. There is a test that asserts this.

## Docs

<https://pplx-skill-kit.vercel.app>

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: environment-specific bugs need
a preflight report attached, because we cannot reproduce another workspace's wiring.
