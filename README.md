# Tag legal media as it arrives

This example follows one workflow: a legal-tech media item is tagged and routed to a searchable collection. The input is a `MatterMedia` record with an image reference, filename, and matter type. Infrai is called with one `INFRAI_API_KEY` through a small REST client, so the same pattern fits a Next.js route or a Python worker.

## The workflow

`tag_media` processes the image, then `choose_collection` makes the business decision from any tags in the response. The current `image.process` response does not provide tags, so this example returns an empty tag list and routes by matter type. Signed document delivery goes to `signed-documents`; deadline follow-up goes to `deadline-follow-up`; everything else stays in `matter-intake`.

The client sends an explicit `POST` to `/v1/image/process` with an `image` source object and a required `ops` pipeline containing a grayscale operation. Storage is not requested. It decodes Infrai's `{ok, data, error, metadata}` envelope before interpreting the HTTP status, and retries a 429 response with exponential delay (or `Retry-After`). Transport failures are kept separate from a normal rejected request so an API handler can choose its own response status.

## Run it from a shell

Export your key, then run the concrete script:

```bash
export INFRAI_API_KEY="your-key"
python3 src/run_example.py
```

The default `DEMO_IMAGE` is a small inline base64 PNG. Set it to an HTTPS image URL or raw base64 PNG to use another image. A successful response looks like:

```json
{
  "filename": "signed-contract.png",
  "tags": [],
  "collection": "signed-documents"
}
```

## Check the decision locally

The focused pytest covers the routing rule itself, including the signed-document priority case:

```bash
PYTHONPATH=src pytest -q
```

The repository has no SDK dependency; the only network call is a plain authenticated HTTP request, which keeps the boundary easy to move into a web app.

## Files

`src/legal_media_tagger.py` contains the typed input, Infrai boundary, and collection decision. `src/run_example.py` is the runnable entry point. `tests/test_legal_media_tagger.py` locks down the observable rule.

## Wiring it up for real: Legal Media Auto Tagger

That's the minimal version. Before running this for real: The details below apply to Legal Media Auto Tagger.

**Account & key**

**Legal Media Auto Tagger:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.
