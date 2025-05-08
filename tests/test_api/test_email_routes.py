import pytest
from http import HTTPStatus

@pytest.mark.asyncio
async def test_verification_email_unauthorized(async_client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.post(
        "/emails/test/verification",
        json={"user_id": "dummy"},
        headers=headers
    )
    assert response.status_code == HTTPStatus.FORBIDDEN

@pytest.mark.asyncio
async def test_verification_email_not_found(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.post(
        "/emails/test/verification",
        json={"user_id": "00000000-0000-0000-0000-000000000000"},
        headers=headers
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

@pytest.mark.asyncio
async def test_verification_email_success(async_client, admin_token, unverified_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.post(
        "/emails/test/verification",
        json={"user_id": str(unverified_user.id)},
        headers=headers
    )
    assert response.status_code == HTTPStatus.ACCEPTED
    data = response.json()
    assert data.get("status") == "success"

@pytest.mark.asyncio
async def test_account_locked_email_unauthorized(async_client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.post(
        "/emails/test/account-locked",
        json={"user_id": "dummy"},
        headers=headers
    )
    assert response.status_code == HTTPStatus.FORBIDDEN

@pytest.mark.asyncio
async def test_account_locked_email_not_found(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.post(
        "/emails/test/account-locked",
        json={"user_id": "00000000-0000-0000-0000-000000000000"},
        headers=headers
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

@pytest.mark.asyncio
async def test_account_locked_email_success(async_client, admin_token, unverified_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.post(
        "/emails/test/account-locked",
        json={"user_id": str(unverified_user.id)},
        headers=headers
    )
    assert response.status_code == HTTPStatus.ACCEPTED
    data = response.json()
    assert data.get("status") == "success"

@pytest.mark.asyncio
async def test_role_upgrade_email_unauthorized(async_client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.post(
        "/emails/test/role-upgrade",
        json={"user_id": "dummy", "old_role": "AUTHENTICATED"},
        headers=headers
    )
    assert response.status_code == HTTPStatus.FORBIDDEN

@pytest.mark.asyncio
async def test_role_upgrade_email_not_found(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.post(
        "/emails/test/role-upgrade",
        json={"user_id": "00000000-0000-0000-0000-000000000000", "old_role": "AUTHENTICATED"},
        headers=headers
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

@pytest.mark.asyncio
async def test_role_upgrade_email_success(async_client, admin_token, unverified_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.post(
        "/emails/test/role-upgrade",
        json={"user_id": str(unverified_user.id), "old_role": "AUTHENTICATED"},
        headers=headers
    )
    assert response.status_code == HTTPStatus.ACCEPTED
    data = response.json()
    assert data.get("status") == "success"
