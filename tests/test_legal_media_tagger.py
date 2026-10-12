from legal_media_tagger import InfraiImageClient, choose_collection


def test_signed_documents_take_priority_for_search_collection():
    tags = ["signature", "document", "contract"]
    assert choose_collection("matter_intake", tags) == "signed-documents"
    assert choose_collection("deadline_follow_up", ["calendar"]) == "deadline-follow-up"


def test_image_request_uses_process_contract():
    client = InfraiImageClient(api_key="test")
    calls = []
    client._request = lambda method, path, payload: calls.append((method, path, payload)) or {"data": {}}
    assert client.tag("iVBORw0KGgo=") == []
    assert calls == [("POST", "/v1/image/process", {
        "image": {"base64": "iVBORw0KGgo="}, "ops": [{"op": "grayscale"}]
    })]
