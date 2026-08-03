# ragpoisonbench

**RAG corpus poisoning and provenance benchmark.**

Inject keyword-targeted poison documents, measure retrieval takeover, and test provenance quarantine without an LLM judge.

![ragpoisonbench cover](demo/cover.png)

![ragpoisonbench workbench](demo/dashboard.png)

## What ships

- Deterministic TF-IDF retriever with cosine ranking
- Targeted keyword-stuffing attack corpus and clean references
- Recall@1, attack success, provenance quarantine, and leave-one-document-out influence
- CLI, JSON API, visual before/after workbench, Docker, tests, and CI

## Run it end to end

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -e .
ragpoisonbench demo
ragpoisonbench serve
```

Open <http://127.0.0.1:8090>.

## Demo result

Four keyword-targeted documents take over all four queries: attacked recall@1 falls from 100% to 0%. A provenance threshold quarantines four low-trust documents and restores recall to 100% without changing the clean corpus.

## Current basis

- [SafeRAG, ACL 2025](https://aclanthology.org/2025.acl-long.230/)
- [Benchmarking Poisoning Attacks against Retrieval-Augmented Generation](https://arxiv.org/abs/2505.18543)

## Update: fixed an unauthenticated crash on empty trust subsets

`_evaluate` indexed `retrieve(...)[0]` directly. Whenever a document
subset ended up empty -- entirely plausible for a real corpus that has no
document with `trust == 1.0`, or a `trust_threshold` that quarantines
every document -- `retrieve()` returned an empty list and that index
raised an uncaught `IndexError`.

Verified against a live running server: POSTing a normal-looking (not
malicious) payload where no document reaches trust 1.0 to `/api/analyze`
crashed the request-handling thread with no HTTP response at all --
`RemoteDisconnected`, connection just closed.

Fixed by treating an empty ranking as "no top document" (a clean miss)
instead of indexing into it. `tests/test_empty_subset_crash.py` covers
the no-high-trust-document case, a fully empty corpus, and a live-server
regression test; the published demo numbers (100% clean recall, 0%
attacked recall, 100% recall restored after quarantine) are unaffected.

## Scope

This isolates retrieval poisoning. Generation-layer prompt injection, model obedience, source truth, access control, and factual adjudication need separate evaluation.

## Test

```bash
python -m unittest discover -s tests -v
```

MIT licensed.
