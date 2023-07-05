import pytest

from fastapi import status

@pytest.mark.parametrize(
    ('username', 'email', 'password', 'status'),
    (
        (
            'leo',
            'leod@test.org',
            'leodpass',
            201,
        ),
        (
            'tess',
            'not_email',
            'tesspass',
            422,
        ),
    ),
)
def test_create_user(username, email, password, status, client):
    response = client.post(
        '/sign-up',
        json={
            'username': username,
            'email': email,
            'password': password,
        },
    )
    assert status == response.status_code


@pytest.mark.parametrize(
    ('username', 'password', 'status'),
    (
        ('user', 'user', 200),
        ('bad_user', 'user', 400),
    ),
)
def test_get_token(username, password, status, user, client):
    data = {'username': username, 'password': password}
    response = client.post('/token', data=data)
    assert status == response.status_code


def test_get_users_list_without_auth(client):
    response = client.get('/users')
    assert status.HTTP_401_UNAUTHORIZED == response.status_code


def test_get_users_list_with_auth(auth_client):
    response = auth_client.get('/users')
    assert status.HTTP_200_OK == response.status_code
