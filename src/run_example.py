import json
import os

from legal_media_tagger import InfraiImageClient, MatterMedia, tag_media


def main() -> None:
    item = MatterMedia(
        image=os.environ.get("DEMO_IMAGE", "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII="),
        filename="signed-contract.png",
        matter_type="signed_document_delivery",
    )
    result = tag_media(item, InfraiImageClient())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
