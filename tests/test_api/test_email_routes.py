import pytest
from http import HTTPStatus

@pytest.mark.asyncio
async def test_verification_email_unauthorized(async_client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.post(
        f"/emails/test/verification/dummy",
        headers=headers
    )
    assert response.status_code == HTTPStatus.FORBIDDEN

@pytest.mark.asyncio
async def test_verification_email_not_found(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.post(
        f"/emails/test/verification/00000000-0000-0000-0000-000000000000",
        headers=headers
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

@pytest.mark.asyncio
async def test_verification_email_success(async_client, admin_token, unverified_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.post(
        f"/emails/test/verification/{str(unverified_user.id)}",
        headers=headers
    )
    assert response.status_code == HTTPStatus.ACCEPTED
    data = response.json()
    assert data.get("status") == "success"

@pytest.mark.asyncio
async def test_account_locked_email_unauthorized(async_client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.post(
        f"/emails/test/account-locked/dummy",
        headers=headers
    )
    assert response.status_code == HTTPStatus.FORBIDDEN

@pytest.mark.asyncio
async def test_account_locked_email_not_found(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.post(
        f"/emails/test/account-locked/00000000-0000-0000-0000-000000000000",
        headers=headers
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

@pytest.mark.asyncio
async def test_account_locked_email_success(async_client, admin_token, unverified_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.post(
        f"/emails/test/account-locked/{str(unverified_user.id)}",
        headers=headers
    )
    assert response.status_code == HTTPStatus.ACCEPTED
    data = response.json()
    assert data.get("status") == "success"

@pytest.mark.asyncio
async def test_role_upgrade_email_unauthorized(async_client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.post(
        f"/emails/test/role-upgrade/dummy/AUTHENTICATED/ADMIN",
        headers=headers
    )
    assert response.status_code == HTTPStatus.FORBIDDEN

@pytest.mark.asyncio
async def test_role_upgrade_email_not_found(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.post(
        f"/emails/test/role-upgrade/00000000-0000-0000-0000-000000000000/AUTHENTICATED/ADMIN",
        headers=headers
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

@pytest.mark.asyncio
async def test_role_upgrade_email_success(async_client, admin_token, unverified_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.post(
        f"/emails/test/role-upgrade/{str(unverified_user.id)}/AUTHENTICATED/ADMIN",
        headers=headers
    )
    assert response.status_code == HTTPStatus.ACCEPTED
    data = response.json()
    assert data.get("status") == "success"
