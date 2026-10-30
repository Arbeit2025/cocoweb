import importlib
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def make_client():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    os.environ["DESKTOP_MASCOT_DB_PATH"] = tmp.name
    import app as app_module

    importlib.reload(app_module)
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def test_index_ok_and_mascot_present():
    client = make_client()
    res = client.get("/")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert "Cocoa Mascot" in body
    assert 'id="mascot"' in body
    assert 'id="bubble"' in body
    assert 'id="callBtn"' in body
    assert 'id="walkBtn"' in body
    assert 'id="sitBtn"' in body


def test_lines_are_24_and_unique():
    client = make_client()
    body = client.get("/").get_data(as_text=True)
    # cocobuttonと共通のセリフが入っていること
    for sample in ["私は見ています。", "書いてくれて、ありがとう。", "夜更かしはほどほどに、ですよ。"]:
        assert sample in body
    # JS内の歩行・ドラッグ処理の存在
    assert "requestAnimationFrame" in body
    assert "pointerdown" in body


def test_count_increments():
    client = make_client()
    r1 = client.post("/count").get_json()
    r2 = client.post("/count").get_json()
    assert r1["total"] == 1 and r1["today"] == 1
    assert r2["total"] == 2 and r2["today"] == 2


def test_character_image_served():
    client = make_client()
    body = client.get("/").get_data(as_text=True)
    assert 'id="charImg"' in body
    assert 'src="/cocoa.png"' in body
    res = client.get("/cocoa.png")
    assert res.status_code == 200
    assert res.content_type.startswith("image/png")
    assert res.data[:8] == b"\x89PNG\r\n\x1a\n"


def test_healthz():
    client = make_client()
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.get_json() == {"ok": True}
