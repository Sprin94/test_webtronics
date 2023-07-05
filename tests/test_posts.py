import pytest

from fastapi import status


def test_get_post(client, user_2_post):
    response = client.get('/posts/1')
    assert status.HTTP_200_OK == response.status_code
    data = response.json()
    assert user_2_post.title == data.get('title')
    assert user_2_post.text == data.get('text')


def test_create_post(auth_client):
    data = {
        'text': 'test_1',
        'title': 'title_test',
    }
    response = auth_client.post('/posts', json=data)
    assert status.HTTP_201_CREATED == response.status_code
    response_data = response.json()
    assert data.get('title') == response_data.get('title')
    assert data.get('text') == response_data.get('text')


@pytest.mark.parametrize(
        'payload',
        (
            {'title': 'test'},
            {'text': 'test'},
        )
)
def test_create_post_wrong_payload(auth_client, payload):
    response = auth_client.post('/posts', json=payload)
    assert status.HTTP_422_UNPROCESSABLE_ENTITY == response.status_code


@pytest.mark.parametrize(
        ('value', 'status_code'),
        ((-1, 200), (1, 200), (0, 422), (-2, 422))
)
def test_likes(auth_client, user_2_post, value, status_code):
    response = auth_client.post(
        f'/posts/{user_2_post.id}/likes',
        json={'value': value}
    )
    assert status_code == response.status_code


def test_likes_your_posts(auth_client):
    data = {
        'text': 'test_1',
        'title': 'title_test',
    }
    response = auth_client.post('/posts', json=data)
    assert status.HTTP_201_CREATED == response.status_code
    response_data = response.json()
    response = auth_client.post(
        f'/posts/{response_data.get("id")}/likes',
        json={'value': -1}
    )
    assert status.HTTP_400_BAD_REQUEST == response.status_code


def test_likes_delete(auth_client, user_2_post):
    response = auth_client.post(
        f'/posts/{user_2_post.id}/likes',
        json={'value': 1}
    )
    assert status.HTTP_200_OK == response.status_code
    response = auth_client.delete(
        f'/posts/{user_2_post.id}/likes',
    )
    assert status.HTTP_204_NO_CONTENT == response.status_code


def test_update_post(auth_client):
    data = {
        'text': 'test_1',
        'title': 'title_test',
    }
    response = auth_client.post('/posts', json=data)
    assert status.HTTP_201_CREATED == response.status_code
    response_data = response.json()
    response = auth_client.patch(
        f'/posts/{response_data.get("id")}',
        json={'text': 'new'}
    )
    assert response.status_code == status.HTTP_200_OK
    response = auth_client.get(f'/posts/{response_data.get("id")}')
    assert response.status_code == status.HTTP_200_OK
    assert 'new' == response.json().get('text')
