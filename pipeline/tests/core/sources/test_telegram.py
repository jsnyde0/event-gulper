import pytest
from telethon.tl.types import ChannelParticipantsAdmins

GROUP_TITLE = "Event Horizon"
GROUP_ID = -4642099484  # should be the "Event Horizon" group
GROUP_ADMIN_ID = 5155664906
GROUP_ADMIN_FIRST_NAME = "Jonatan"


@pytest.mark.asyncio
async def test_telegram_client_connection(telegram_client):
    """Test that we can connect to Telegram."""
    connected = telegram_client.is_connected()
    print("telegram_client connected: ", connected)
    assert connected


@pytest.mark.asyncio
async def test_telegram_client_can_get_messages(telegram_client):
    """Test that we can fetch messages from a group."""

    target_group = await telegram_client.get_entity(GROUP_ID)

    print(f"Group info: {target_group}")

    # Assert stable group properties
    assert target_group is not None, "Could not find 'Event Horizon' group in dialogs"
    assert target_group.id == abs(GROUP_ID), "Group ID should match"
    assert target_group.title == GROUP_TITLE, "Group title should match"
    assert target_group.deactivated is False, "Group should be active"

    # Get group admins
    participants = await telegram_client.get_participants(
        target_group, filter=ChannelParticipantsAdmins
    )
    admin = participants[-1]
    print(f"Group admin: {admin.first_name} (id: {admin.id})")

    assert admin.id == GROUP_ADMIN_ID, "Admin ID should match"
    assert admin.first_name == GROUP_ADMIN_FIRST_NAME, "Admin name should match"
    assert not admin.bot, "Admin should not be a bot"
