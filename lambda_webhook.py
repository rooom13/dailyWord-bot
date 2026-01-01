import json
import logging
import signal
import os
from contextlib import contextmanager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TimeoutException(Exception):
    pass


AWS_LAMBDA_FUNCTION_TIMEOUT_S = int(os.getenv('AWS_LAMBDA_FUNCTION_TIMEOUT_S', '40'))


@contextmanager
def timeout(seconds):
    """Context manager that raises TimeoutException after specified seconds."""
    def timeout_handler(signum, frame):
        raise TimeoutException(f"Operation timed out after {seconds} seconds")

    # Set the signal handler and alarm
    original_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Disable the alarm and restore original handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)


def lambda_handler(event, context):
    """
    AWS Lambda handler function for Telegram Webhooks.
    """
    logger.info(f"Received webhook event: {json.dumps(event)}")

    try:

        if 'body' in event:
            body = json.loads(event['body'])

            try:
                with timeout(AWS_LAMBDA_FUNCTION_TIMEOUT_S):
                    from daily_word_bot.app import App
                    app = App()
                    app.process_update(body)

                return {
                    'statusCode': 200,
                    'body': json.dumps('Update processed')
                }
            except TimeoutException as te:
                logger.error(f"Timeout processing update: {te}")
                return {
                    'statusCode': 504,
                    'body': json.dumps('Request timeout')
                }

        logger.error(f"Unrecognized event structure: {json.dumps(event)}")
        return {
            'statusCode': 400,
            'body': json.dumps('Unrecognized event type')
        }

    except Exception as e:
        logger.exception(f"Error processing event={json.dumps(event)}: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal server error: {str(e)}")
        }
