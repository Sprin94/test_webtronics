from httpx import AsyncClient
from httpx import Response

from app.utils.check_email import check_email


async def test_check_activate_user_if_valid_email(mocker, user_crud, not_active_user):

    response_mock = mocker.Mock(spec=Response)
    response_mock.status_code = 200
    response_mock.json.return_value = {'data': {'status': 'valid'}}

    async def get_mock(url, params, timeout):
        return response_mock

    mocker.patch.object(AsyncClient, 'get', side_effect=get_mock)

    await check_email(not_active_user.email, user_crud)
    user = await user_crud.get_by_id(not_active_user.id)
    assert user.is_active


async def test_check_activate_user_if_invalid_email(mocker, user_crud, not_active_user):

    response_mock = mocker.Mock(spec=Response)
    response_mock.status_code = 200
    response_mock.json.return_value = {'data': {'status': 'invalid'}}

    async def get_mock(url, params, timeout):
        return response_mock

    mocker.patch.object(AsyncClient, 'get', side_effect=get_mock)

    await check_email(not_active_user.email, user_crud)
    user = await user_crud.get_by_id(not_active_user.id)
    assert not user.is_active
