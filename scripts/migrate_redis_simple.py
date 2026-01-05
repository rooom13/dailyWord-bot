#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "redis",
#     "boto3",
# ]
# ///
"""
Simple migration script to transfer data from a running Redis instance to DynamoDB.

This script connects to a live Redis instance and migrates data to DynamoDB.

Usage:
    uv run scripts/migrate_redis_simple.py --redis-host localhost --redis-port 6379
    
    # To AWS DynamoDB (no endpoint-url)
    uv run scripts/migrate_redis_simple.py --redis-host localhost --region eu-central-1
    
    # Dry run
    uv run scripts/migrate_redis_simple.py --redis-host localhost --dry-run
"""

import argparse
import json
import logging
import os
import sys

import boto3
import redis
from botocore.exceptions import ClientError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def connect_redis(host: str, port: int, use_ssl: bool = False, password: str = None):
    """Connect to Redis."""
    logger.info(f"Connecting to Redis at {host}:{port} (SSL: {use_ssl})...")

    redis_kwargs = {
        'host': host,
        'port': port,
        'decode_responses': True,
        'socket_connect_timeout': 10,
        'socket_timeout': 10,
    }

    if use_ssl:
        redis_kwargs['ssl'] = True
        redis_kwargs['ssl_cert_reqs'] = None

    if password:
        redis_kwargs['password'] = password

    r = redis.Redis(**redis_kwargs)
    r.ping()
    logger.info("Successfully connected to Redis")
    return r


def connect_dynamodb(region: str, endpoint_url: str = None):
    """Connect to DynamoDB."""
    logger.info(f"Connecting to DynamoDB in region {region}...")

    resource_kwargs = {'region_name': region}
    if endpoint_url:
        resource_kwargs['endpoint_url'] = endpoint_url
        logger.info(f"Using custom endpoint: {endpoint_url}")

    dynamodb = boto3.resource('dynamodb', **resource_kwargs)
    logger.info("Successfully connected to DynamoDB")
    return dynamodb


def extract_redis_data(redis_client):
    """Extract all data from Redis."""
    logger.info("Extracting data from Redis...")

    data = {
        'users': {},
        'blocked_words': {}
    }

    # Get all user IDs
    user_ids = redis_client.smembers('users')
    logger.info(f"Found {len(user_ids)} users in Redis")

    # Extract user info
    for user_id in user_ids:
        user_info_key = f'userInfo:{user_id}'
        user_info_json = redis_client.get(user_info_key)

        if user_info_json:
            try:
                user_info = json.loads(user_info_json)
                data['users'][user_id] = user_info
                logger.debug(f"Extracted user {user_id}: {user_info.get('name', 'N/A')}")
            except json.JSONDecodeError as e:
                logger.warning(f"Could not parse user info for {user_id}: {e}")
        else:
            logger.warning(f"No user info found for user {user_id}")

    # Extract blocked words
    for user_id in user_ids:
        blocked_words_key = f'blockedWords-{user_id}'
        blocked_words = redis_client.smembers(blocked_words_key)

        if blocked_words:
            data['blocked_words'][user_id] = list(blocked_words)
            logger.debug(f"User {user_id} has {len(blocked_words)} blocked words")

    logger.info(f"Extraction complete: {len(data['users'])} users, "
                f"{len(data['blocked_words'])} users with blocked words")
    return data


def migrate_to_dynamodb(data, dynamodb, users_table_name, blocked_words_table_name, dry_run=False):
    """Migrate extracted data to DynamoDB."""
    users_table = dynamodb.Table(users_table_name)
    blocked_words_table = dynamodb.Table(blocked_words_table_name)

    # Migrate users
    logger.info(f"Migrating {len(data['users'])} users...")
    user_success = 0
    user_errors = 0

    for user_id, user_info in data['users'].items():
        try:
            item = {
                'userId': str(user_id),
                'name': user_info.get('name', 'Unknown'),
                'isActive': user_info.get('isActive', True),
                'isBlocked': user_info.get('isBlocked', False),
                'isDeactivated': user_info.get('isDeactivated', False),
                'isKicked': user_info.get('isKicked', False),
                'levels': user_info.get('levels', [])
            }

            if dry_run:
                logger.info(f"[DRY RUN] Would create user: {user_id} - {item['name']}")
            else:
                users_table.put_item(Item=item)
                logger.debug(f"Created user: {user_id} - {item['name']}")

            user_success += 1
        except ClientError as e:
            logger.error(f"Error creating user {user_id}: {e}")
            user_errors += 1

    logger.info(f"Users: {user_success} successful, {user_errors} errors")

    # Migrate blocked words
    logger.info(f"Migrating blocked words for {len(data['blocked_words'])} users...")
    word_success = 0
    word_errors = 0

    for user_id, word_ids in data['blocked_words'].items():
        for word_id in word_ids:
            try:
                item = {
                    'userId': str(user_id),
                    'wordId': str(word_id)
                }

                if dry_run:
                    logger.debug(f"[DRY RUN] Would create blocked word: {user_id} -> {word_id}")
                else:
                    blocked_words_table.put_item(Item=item)
                    logger.debug(f"Created blocked word: {user_id} -> {word_id}")

                word_success += 1
            except ClientError as e:
                logger.error(f"Error creating blocked word {user_id}/{word_id}: {e}")
                word_errors += 1

    logger.info(f"Blocked words: {word_success} successful, {word_errors} errors")

    return user_success, user_errors, word_success, word_errors


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Migrate data from Redis to DynamoDB',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Redis options
    parser.add_argument('--redis-host', default='localhost', help='Redis host')
    parser.add_argument('--redis-port', type=int, default=6379, help='Redis port')
    parser.add_argument('--redis-password', help='Redis password (if required)')
    parser.add_argument('--redis-ssl', action='store_true', help='Use SSL for Redis')

    # DynamoDB options
    parser.add_argument('--region', default='eu-central-1', help='AWS region')
    parser.add_argument('--endpoint-url', help='DynamoDB endpoint URL (for LocalStack)')
    parser.add_argument('--users-table', default='daily-word-bot-users', help='Users table name')
    parser.add_argument('--blocked-words-table', default='daily-word-bot-blocked-words',
                        help='Blocked words table name')

    # Execution options
    parser.add_argument('--dry-run', action='store_true',
                        help='Dry run - do not write to DynamoDB')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Connect to Redis
        redis_client = connect_redis(
            args.redis_host,
            args.redis_port,
            args.redis_ssl,
            args.redis_password
        )

        # Connect to DynamoDB
        dynamodb = connect_dynamodb(args.region, args.endpoint_url)

        # Extract data from Redis
        data = extract_redis_data(redis_client)

        # Migrate to DynamoDB
        logger.info("=" * 60)
        logger.info("Starting migration to DynamoDB...")
        logger.info("=" * 60)

        user_success, user_errors, word_success, word_errors = migrate_to_dynamodb(
            data,
            dynamodb,
            args.users_table,
            args.blocked_words_table,
            args.dry_run
        )

        # Summary
        logger.info("=" * 60)
        logger.info("Migration Summary:")
        logger.info(f"  Users: {user_success} successful, {user_errors} errors")
        logger.info(f"  Blocked Words: {word_success} successful, {word_errors} errors")
        logger.info("=" * 60)

        if args.dry_run:
            logger.info("DRY RUN - No data was actually written to DynamoDB")
        else:
            logger.info("Migration complete!")

        sys.exit(0 if user_errors == 0 and word_errors == 0 else 1)

    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
