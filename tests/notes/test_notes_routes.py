def test_notes_page(client):
    response = client.get("/notes")
    assert response.ok


def test_add_note_page(client):
    response = client.get("/notes/add")
    assert response.ok


def test_notes_api(client):
    response = client.get("/notes/all")
    assert response.ok