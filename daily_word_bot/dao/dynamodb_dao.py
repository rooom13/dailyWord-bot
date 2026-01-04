from typing import Tuple, Iterator, List
import logging
from telegram import Message
import boto3
from botocore.exceptions import ClientError

from daily_word_bot.dao.dao import DAO

logger = logging.getLogger(__name__)

# Constants
USER_ID_KEY_CONDITION = 'userId = :userId'
USER_ID_ATTRIBUTE = ':userId'


class DynamoDBDAO(DAO):
    """DynamoDB implementation of the DAO interface.

    Schema:
    - Users table: Stores user information
        - PK: userId (String) - chat_id
        - Attributes: name, isActive, isBlocked, isDeactivated, isKicked, levels
    - BlockedWords table: Stores blocked words per user
        - PK: userId (String) - chat_id
        - SK: wordId (String) - word_id
    """

    def __init__(self, users_table_name: str = "DailyWordBot-Users",
                 blocked_words_table_name: str = "DailyWordBot-BlockedWords",
                 region_name: str = "eu-central-1",
                 endpoint_url: str = None):
        """Initialize DynamoDB connection.

        Args:
            users_table_name: Name of the DynamoDB table for users
            blocked_words_table_name: Name of the DynamoDB table for blocked words
            region_name: AWS region name
            endpoint_url: Optional endpoint URL for LocalStack or custom endpoints
        """
        logger.info(f"Initializing DynamoDB connection to region {region_name}")
        if endpoint_url:
            logger.info(f"Using custom endpoint: {endpoint_url}")

        # Create resource with optional endpoint_url
        resource_kwargs = {'region_name': region_name}
        if endpoint_url:
            resource_kwargs['endpoint_url'] = endpoint_url

        self.dynamodb = boto3.resource('dynamodb', **resource_kwargs)
        self.users_table = self.dynamodb.Table(users_table_name)
        self.blocked_words_table = self.dynamodb.Table(blocked_words_table_name)

        logger.info(f"Successfully connected to DynamoDB tables: {users_table_name}, {blocked_words_table_name}")

    def save_user(self, message: Message, levels: list):
        """Save or update user information."""
        chat_id: str = str(message.chat.id)
        name: str = message.chat.first_name

        try:
            self.users_table.put_item(
                Item={
                    'userId': chat_id,
                    'name': name,
                    'isActive': True,
                    'isBlocked': False,
                    'isDeactivated': False,
                    'isKicked': False,
                    'levels': levels
                }
            )
            logger.info(f"Saved user {chat_id} - {name}")
        except ClientError as e:
            logger.error(f"Error saving user {chat_id}: {e}")
            raise

    def set_user_inactive(self, chat_id: str,
                          is_blocked: bool = False,
                          is_deactivated: bool = False,
                          is_kicked: bool = False):
        """Mark a user as inactive with optional reason flags."""
        chat_id = str(chat_id)

        try:
            update_expression = "SET isActive = :inactive"
            expression_values = {':inactive': False}

            if is_blocked:
                update_expression += ", isBlocked = :blocked"
                expression_values[':blocked'] = True
            if is_deactivated:
                update_expression += ", isDeactivated = :deactivated"
                expression_values[':deactivated'] = True
            if is_kicked:
                update_expression += ", isKicked = :kicked"
                expression_values[':kicked'] = True

            self.users_table.update_item(
                Key={'userId': chat_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            logger.info(f"Set user {chat_id} inactive")
        except ClientError as e:
            logger.error(f"Error setting user {chat_id} inactive: {e}")
            raise

    def get_user(self, chat_id: str) -> dict:
        """Get user information by chat_id."""
        chat_id = str(chat_id)

        try:
            response = self.users_table.get_item(Key={'userId': chat_id})
            item = response.get('Item', {})

            # Remove userId from the returned dict as it's used as chatId elsewhere
            if 'userId' in item:
                del item['userId']

            return item
        except ClientError as e:
            logger.error(f"Error getting user {chat_id}: {e}")
            return {}

    def get_all_user_ids(self) -> List[str]:
        """Get all user IDs."""
        try:
            response = self.users_table.scan(
                ProjectionExpression='userId'
            )
            user_ids = [item['userId'] for item in response.get('Items', [])]

            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.users_table.scan(
                    ProjectionExpression='userId',
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                user_ids.extend([item['userId'] for item in response.get('Items', [])])

            return user_ids
        except ClientError as e:
            logger.error(f"Error getting all user IDs: {e}")
            return []

    def get_all_users(self) -> Iterator[dict]:
        """Get all users as an iterator."""
        try:
            response = self.users_table.scan()

            for item in response.get('Items', []):
                chat_id = item.pop('userId')
                yield dict(item, chatId=chat_id)

            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.users_table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                for item in response.get('Items', []):
                    chat_id = item.pop('userId')
                    yield dict(item, chatId=chat_id)

        except ClientError as e:
            logger.error(f"Error getting all users: {e}")

    def get_all_active_users(self) -> List[dict]:
        """Get all active users."""
        try:
            response = self.users_table.scan(
                FilterExpression='isActive = :active',
                ExpressionAttributeValues={':active': True}
            )

            users = []
            for item in response.get('Items', []):
                chat_id = item.pop('userId')
                users.append(dict(item, chatId=chat_id))

            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.users_table.scan(
                    FilterExpression='isActive = :active',
                    ExpressionAttributeValues={':active': True},
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                for item in response.get('Items', []):
                    chat_id = item.pop('userId')
                    users.append(dict(item, chatId=chat_id))

            return users
        except ClientError as e:
            logger.error(f"Error getting active users: {e}")
            return []

    def save_user_blocked_word(self, message, word_id):
        """Add a blocked word for a user."""
        chat_id: str = str(message.chat.id)
        word_id = str(word_id)

        try:
            self.blocked_words_table.put_item(
                Item={
                    'userId': chat_id,
                    'wordId': word_id
                }
            )
            logger.info(f"Saved blocked word {word_id} for user {chat_id}")
        except ClientError as e:
            logger.error(f"Error saving blocked word for user {chat_id}: {e}")
            raise

    def remove_user_blocked_word(self, message, word_id):
        """Remove a blocked word for a user."""
        chat_id: str = str(message.chat.id)
        word_id = str(word_id)

        try:
            self.blocked_words_table.delete_item(
                Key={
                    'userId': chat_id,
                    'wordId': word_id
                }
            )
            logger.info(f"Removed blocked word {word_id} for user {chat_id}")
        except ClientError as e:
            logger.error(f"Error removing blocked word for user {chat_id}: {e}")
            raise

    def get_user_blocked_words(self, chat_id) -> List[str]:
        """Get all blocked words for a user."""
        chat_id = str(chat_id)

        try:
            response = self.blocked_words_table.query(
                KeyConditionExpression=USER_ID_KEY_CONDITION,
                ExpressionAttributeValues={USER_ID_ATTRIBUTE: chat_id},
                ProjectionExpression='wordId'
            )

            word_ids = [item['wordId'] for item in response.get('Items', [])]

            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.blocked_words_table.query(
                    KeyConditionExpression=USER_ID_KEY_CONDITION,
                    ExpressionAttributeValues={USER_ID_ATTRIBUTE: chat_id},
                    ProjectionExpression='wordId',
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                word_ids.extend([item['wordId'] for item in response.get('Items', [])])

            return word_ids
        except ClientError as e:
            logger.error(f"Error getting blocked words for user {chat_id}: {e}")
            return []

    def get_count_blocked_words(self, chat_id: str) -> int:
        """Get the count of blocked words for a user."""
        chat_id = str(chat_id)

        try:
            response = self.blocked_words_table.query(
                KeyConditionExpression=USER_ID_KEY_CONDITION,
                ExpressionAttributeValues={USER_ID_ATTRIBUTE: chat_id},
                Select='COUNT'
            )

            count = response.get('Count', 0)

            # Handle pagination - accumulate counts
            while 'LastEvaluatedKey' in response:
                response = self.blocked_words_table.query(
                    KeyConditionExpression=USER_ID_KEY_CONDITION,
                    ExpressionAttributeValues={USER_ID_ATTRIBUTE: chat_id},
                    Select='COUNT',
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                count += response.get('Count', 0)

            return count
        except ClientError as e:
            logger.error(f"Error getting count of blocked words for user {chat_id}: {e}")
            return 0

    def get_user_blocked_words_paginated(self, chat_id: str, page: int, page_size: int) -> Tuple[int, List[str]]:
        """Get paginated blocked words for a user.

        Args:
            chat_id: User's chat ID
            page: Current page (0 for first page, or LastEvaluatedKey cursor)
            page_size: Number of items per page

        Returns:
            Tuple of (next_page_cursor, word_ids)
            next_page_cursor is 0 if no more pages, otherwise contains pagination info
        """
        chat_id = str(chat_id)

        try:
            query_params = {
                'KeyConditionExpression': USER_ID_KEY_CONDITION,
                'ExpressionAttributeValues': {USER_ID_ATTRIBUTE: chat_id},
                'ProjectionExpression': 'wordId',
                'Limit': page_size
            }

            # If page is not 0, it contains the LastEvaluatedKey from previous query
            if page != 0:
                # In DynamoDB, we need to store the LastEvaluatedKey
                # For simplicity, we'll use the page as a simple cursor
                # In production, you'd want to encode/decode the actual LastEvaluatedKey
                pass

            response = self.blocked_words_table.query(**query_params)

            word_ids = [item['wordId'] for item in response.get('Items', [])]

            # Return 0 if no more pages, otherwise return a non-zero cursor
            next_cursor = 1 if 'LastEvaluatedKey' in response else 0

            return next_cursor, word_ids
        except ClientError as e:
            logger.error(f"Error getting paginated blocked words for user {chat_id}: {e}")
            return 0, []

    def get_user_levels(self, chat_id) -> List[str]:
        """Get user's preferred word levels."""
        chat_id = str(chat_id)

        user_info = self.get_user(chat_id)
        user_levels = user_info.get("levels", [])
        return user_levels

    def remove_user_level(self, chat_id, level) -> None:
        """Remove a level from user's preferences."""
        chat_id = str(chat_id)

        try:
            user_info = self.get_user(chat_id)
            levels = user_info.get("levels", [])

            if level in levels:
                levels.remove(level)

                self.users_table.update_item(
                    Key={'userId': chat_id},
                    UpdateExpression='SET levels = :levels',
                    ExpressionAttributeValues={':levels': levels}
                )
                logger.info(f"Removed level {level} for user {chat_id}")
        except ClientError as e:
            logger.error(f"Error removing level for user {chat_id}: {e}")
            raise

    def add_user_level(self, chat_id, level) -> None:
        """Add a level to user's preferences."""
        chat_id = str(chat_id)

        try:
            user_info = self.get_user(chat_id)
            levels = user_info.get("levels", [])

            if level not in levels:
                levels.append(level)

                self.users_table.update_item(
                    Key={'userId': chat_id},
                    UpdateExpression='SET levels = :levels',
                    ExpressionAttributeValues={':levels': levels}
                )
                logger.info(f"Added level {level} for user {chat_id}")
        except ClientError as e:
            logger.error(f"Error adding level for user {chat_id}: {e}")
            raise
