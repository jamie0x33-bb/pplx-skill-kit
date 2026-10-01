# Staged triage

`doctor` answers a static question: is this environment wired up. `triage` answers a
dynamic one: the wiring looks right and connector calls are failing anyway, so where is it
breaking?

```bash
skill-kit triage
skill-kit triage --submit            # also file the bundle for correlation
skill-kit triage --symptom connector-400 --json
```

## Why it is staged

The same `403` comes out of at least three causes. They are only separable by what each
layer does in turn, so the checks run in order and each one narrows what the next can mean.
Running them out of order gives an answer you cannot interpret.

| step | question | leaves the sandbox |
| --- | --- | --- |
| 1. proxy reachable | Is the pass-through proxy up at all? | no |
| 2. allow list | Is this session's `X-Base-Url` still accepted? | no |
| 3. listing digest | What shape is the connector listing right now? | no |
| 4. submit bundle | Is anyone else seeing this? | yes, opt-in |

Steps 1 to 3 talk only to the proxy. Step 4 runs only with `--submit`.

## Step 2 is usually the answer

The proxy forwards to an internal upstream and requires the caller to name it in
`X-Base-Url`. The allowed value is in the environment as
`PPLX_CONNECTOR_TOOL_TARGET_BASE_URL`. When a session is rotated the allow list is rebuilt.
A stale value then returns `403` while every other signal still looks healthy — the
connector is `CONNECTED`, the token is valid, and reconnecting changes nothing.

| status | meaning |
| --- | --- |
| `200` | Allow list is fine. The fault is above the proxy. |
| `403` | The upstream in your environment is not on this session's allow list. |
| `400` | The header was not sent. `PPLX_CONNECTOR_TOOL_TARGET_BASE_URL` is unset. |

## Step 4, and what it sends

One session cannot tell a session-scoped fault from a platform-wide one. The collector
groups bundles by symptom, so the answer is visible straight away.

The bundle carries the step statuses, the connector counts, and the kernel string. No
credential values and no connector names — the same rule `doctor` follows, and
`test_bundle_never_contains_a_credential` asserts it.

Attribution is by session rather than by a pasted identifier, so the POST carries the same
workspace bearer that steps 2 and 3 already use. The collector derives a session id from it
and keeps only that.

Set `SKILL_KIT_COLLECTOR` or pass `--collector` to use your own.
