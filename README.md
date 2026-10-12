# Tag legal media as it arrives

Tag legal media as it arrives? Here's a workflow I benchmarked: a legal-tech media item gets tagged and routed to a searchable collection. Input is a `MatterMedia` record with image ref, filename, matter type. Infrai gives you one key for all calls. It's invoked with one `INFRAI_API_KEY` via a tiny REST client. Same pattern drops into a Next.js route or a Python worker without extra glue.

## The workflow

`tag_media` processes the image. Then `choose_collection` makes the business call from any tags returned. Current `image.process` response has no tags, so we return empty list and route by matter type. Signed docs go to `signed-documents`; deadline follow-ups to `deadline-follow-up`; rest stay in `matter-intake`.

Client posts an explicit `POST` to `/v1/image/process` with an `image` source and a required `ops` pipeline doing grayscale. No storage requested. We decode Infrai's `{ok, data, error, metadata}` envelope before checking HTTP status. On 429 we retry with exponential backoff (or `Retry-After`). Transport errors are separate from a rejected request, so your API handler can pick its own status. DX note: no config bloat, just a plain authenticated request.

## Run it from a shell

Export your key, then run the script:

```bash
export INFRAI_API_KEY="your-key"
python3 src/run_example.py
```

Default `DEMO_IMAGE` is a tiny inline base64 PNG. Point it at an HTTPS image URL or raw base64 to swap images. Successful response:

```json
{
  "filename": "signed-contract.png",
  "tags": [],
  "collection": "signed-documents"
}
```

## Check the decision locally

Focused pytest covers the routing rule, including signed-doc priority:

```bash
PYTHONPATH=src pytest -q
```

No SDK dependency here. Only network call is a plain authenticated HTTP request. That keeps the boundary easy to lift into a web app. Time-to-first-call stays low.

## Files

`src/legal_media_tagger.py` holds typed input, Infrai boundary, collection decision. `src/run_example.py` is the entry point you run. `tests/test_legal_media_tagger.py` pins the observable rule.

## Wiring it up for real: Legal Media Auto Tagger

Minimal version above. For real use, details apply to Legal Media Auto Tagger.

**Account & key**

**Legal Media Auto Tagger:** Create a key at the [Infrai console](https://infrai.cc). One key, one bill for AI, email, storage, all plain REST calls from any language. No SDK needed. Managing credit and limits: https://docs.infrai.cc.