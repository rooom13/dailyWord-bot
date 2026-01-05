import pytest
from unittest.mock import Mock
from moto import mock_aws
import boto3
from telegram import Chat, Message

from daily_word_bot.dao.dynamodb_dao import DynamoDBDAO


@pytest.fixture(scope="function")
def aws_credentials():
    """Mock AWS Credentials for moto."""
    import os
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    # Remove endpoint URL to ensure we use moto, not LocalStack
    os.environ.pop('AWS_ENDPOINT_URL', None)
    os.environ.pop('DYNAMODB_ENDPOINT_URL', None)


@pytest.fixture(scope="function")
def dao(aws_credentials):
    """Create DynamoDBDAO instance with mocked DynamoDB."""
    with mock_aws():
        # Create DynamoDB resource
        region = 'eu-central-1'  # Match the default region in DynamoDBDAO
        dynamodb = boto3.resource('dynamodb', region_name=region)  # noqa: S106

        # Create Users table
        dynamodb.create_table(
            TableName=DynamoDBDAO.USERS_TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'userId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'userId', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        # Create BlockedWords table
        dynamodb.create_table(
            TableName=DynamoDBDAO.BLOCKED_WORDS_TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'userId', 'KeyType': 'HASH'},
                {'AttributeName': 'wordId', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'userId', 'AttributeType': 'S'},
                {'AttributeName': 'wordId', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        # Create DAO inside the mock context - explicitly pass endpoint_url=None to use moto
        dao_instance = DynamoDBDAO(region_name=region, endpoint_url=None)

        yield dao_instance


@pytest.fixture
def mock_message():
    """Create a mock Telegram Message."""
    message = Mock(spec=Message)
    chat = Mock(spec=Chat)
    chat.id = 123456
    chat.first_name = "TestUser"
    message.chat = chat
    return message


def test_save_user(dao, mock_message):
    """Test saving a user."""
    levels = ["beginner", "intermediate"]
    dao.save_user(mock_message, levels)

    # Verify user was saved
    user = dao.get_user("123456")
    assert user["name"] == "TestUser"
    assert user["isActive"] is True
    assert user["isBlocked"] is False
    assert user["levels"] == levels


def test_get_user_nonexistent(dao):
    """Test getting a non-existent user returns empty dict."""
    user = dao.get_user("999999")
    assert user == {}


def test_set_user_inactive(dao, mock_message):
    """Test setting a user inactive."""
    levels = ["beginner"]
    dao.save_user(mock_message, levels)

    # Set user inactive with blocked flag
    dao.set_user_inactive("123456", is_blocked=True)

    user = dao.get_user("123456")
    assert user["isActive"] is False
    assert user["isBlocked"] is True
    assert user["isDeactivated"] is False
    assert user["isKicked"] is False


def test_get_all_user_ids(dao, mock_message):
    """Test getting all user IDs."""
    dao.save_user(mock_message, ["beginner"])

    # Create another user
    mock_message.chat.id = 789012
    dao.save_user(mock_message, ["advanced"])

    user_ids = dao.get_all_user_ids()
    assert len(user_ids) == 2
    assert "123456" in user_ids
    assert "789012" in user_ids


def test_get_all_users(dao, mock_message):
    """Test getting all users."""
    dao.save_user(mock_message, ["beginner"])

    users = list(dao.get_all_users())
    assert len(users) == 1
    assert users[0]["chatId"] == "123456"
    assert users[0]["name"] == "TestUser"


def test_get_all_active_users(dao, mock_message):
    """Test getting only active users."""
    # Create two users
    dao.save_user(mock_message, ["beginner"])

    mock_message.chat.id = 789012
    mock_message.chat.first_name = "AnotherUser"
    dao.save_user(mock_message, ["advanced"])

    # Set one user inactive
    dao.set_user_inactive("123456")

    active_users = dao.get_all_active_users()
    assert len(active_users) == 1
    assert active_users[0]["chatId"] == "789012"


def test_save_and_get_blocked_words(dao, mock_message):
    """Test saving and retrieving blocked words."""
    dao.save_user(mock_message, ["beginner"])

    # Block some words
    dao.save_user_blocked_word(mock_message, "word1")
    dao.save_user_blocked_word(mock_message, "word2")

    blocked_words = dao.get_user_blocked_words("123456")
    assert len(blocked_words) == 2
    assert "word1" in blocked_words
    assert "word2" in blocked_words


def test_remove_blocked_word(dao, mock_message):
    """Test removing a blocked word."""
    dao.save_user(mock_message, ["beginner"])
    dao.save_user_blocked_word(mock_message, "word1")
    dao.save_user_blocked_word(mock_message, "word2")

    # Remove one word
    dao.remove_user_blocked_word(mock_message, "word1")

    blocked_words = dao.get_user_blocked_words("123456")
    assert len(blocked_words) == 1
    assert "word2" in blocked_words
    assert "word1" not in blocked_words


def test_get_count_blocked_words(dao, mock_message):
    """Test getting count of blocked words."""
    dao.save_user(mock_message, ["beginner"])
    dao.save_user_blocked_word(mock_message, "word1")
    dao.save_user_blocked_word(mock_message, "word2")
    dao.save_user_blocked_word(mock_message, "word3")

    count = dao.get_count_blocked_words("123456")
    assert count == 3


def test_get_blocked_words_paginated(dao, mock_message):
    """Test getting paginated blocked words."""
    dao.save_user(mock_message, ["beginner"])

    # Add multiple words
    for i in range(5):
        dao.save_user_blocked_word(mock_message, f"word{i}")

    # Get first page
    next_cursor, word_ids = dao.get_user_blocked_words_paginated("123456", 0, 3)
    assert len(word_ids) <= 3

    # If there are more pages, next_cursor should be non-zero
    if len(word_ids) == 3:
        assert next_cursor != 0
    else:
        assert next_cursor == 0


def test_get_user_levels(dao, mock_message):
    """Test getting user levels."""
    levels = ["beginner", "intermediate"]
    dao.save_user(mock_message, levels)

    user_levels = dao.get_user_levels("123456")
    assert user_levels == levels


def test_add_user_level(dao, mock_message):
    """Test adding a level to user."""
    dao.save_user(mock_message, ["beginner"])

    dao.add_user_level("123456", "intermediate")

    user_levels = dao.get_user_levels("123456")
    assert "beginner" in user_levels
    assert "intermediate" in user_levels


def test_remove_user_level(dao, mock_message):
    """Test removing a level from user."""
    dao.save_user(mock_message, ["beginner", "intermediate", "advanced"])

    dao.remove_user_level("123456", "intermediate")

    user_levels = dao.get_user_levels("123456")
    assert "beginner" in user_levels
    assert "advanced" in user_levels
    assert "intermediate" not in user_levels


def test_get_user_levels_nonexistent_user(dao):
    """Test getting levels for non-existent user returns empty list."""
    levels = dao.get_user_levels("999999")
    assert levels == []
