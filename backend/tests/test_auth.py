def test_health_and_status(client):
    assert client.get("/health").json()["status"] == "ok"
    features = client.get("/api/status").json()["features"]
    assert features == {"ai": False, "spotify": False, "email": False}


def test_register_login_me(client):
    r = client.post("/api/auth/register",
                    json={"email": "Geo@Test.com", "username": "geo_77", "password": "motdepasse1"})
    assert r.status_code == 201
    token = r.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
    assert me["email"] == "geo@test.com"
    assert me["username"] == "geo_77"

    # login is case-insensitive on email
    r = client.post("/api/auth/login", json={"email": "GEO@test.com", "password": "motdepasse1"})
    assert r.status_code == 200

    r = client.post("/api/auth/login", json={"email": "geo@test.com", "password": "wrong-password"})
    assert r.status_code == 401


def test_register_conflicts(client):
    client.post("/api/auth/register",
                json={"email": "dup@test.com", "username": "dup_user", "password": "password123"})
    r = client.post("/api/auth/register",
                    json={"email": "DUP@test.com", "username": "other", "password": "password123"})
    assert r.status_code == 400 and "email" in r.json()["detail"]
    r = client.post("/api/auth/register",
                    json={"email": "new@test.com", "username": "DUP_USER", "password": "password123"})
    assert r.status_code == 400 and "username" in r.json()["detail"]


def test_register_validation(client):
    r = client.post("/api/auth/register", json={"email": "bad", "username": "ab", "password": "123"})
    assert r.status_code == 422
    fields = {e["loc"][-1] for e in r.json()["detail"]}
    assert fields == {"email", "username", "password"}


def test_invalid_token(client):
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer nope"}).status_code == 401


def test_password_reset_flow(client, caplog):
    client.post("/api/auth/register",
                json={"email": "reset@test.com", "username": "reset_me", "password": "oldpassword"})
    with caplog.at_level("WARNING"):
        r = client.post("/api/auth/forgot-password", json={"email": "reset@test.com"})
    assert r.status_code == 200
    # No email service configured -> link is logged
    line = next(m for m in caplog.messages if "reset-password?token=" in m)
    token = line.split("token=")[1].split()[0]

    r = client.post("/api/auth/reset-password", json={"token": token, "new_password": "newpassword"})
    assert r.status_code == 200
    assert client.post("/api/auth/login",
                       json={"email": "reset@test.com", "password": "newpassword"}).status_code == 200
    # token is single-use
    r = client.post("/api/auth/reset-password", json={"token": token, "new_password": "another1"})
    assert r.status_code == 400


def test_forgot_password_unknown_email(client):
    r = client.post("/api/auth/forgot-password", json={"email": "nobody@test.com"})
    assert r.status_code == 200


def test_delete_account(client, auth):
    client.post("/api/mood/analyze", json={"text": "I'm happy"}, headers=auth)
    assert client.delete("/api/auth/me", headers=auth).status_code == 204
    assert client.get("/api/auth/me", headers=auth).status_code == 401
