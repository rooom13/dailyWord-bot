import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the app outside the handler to reuse it across warm invocations


def lambda_handler(event, context):
    from daily_word_bot.app import App
    app = App()
    """
    AWS Lambda handler function for Telegram Webhooks.
    """
    logger.info(f"Received webhook event: {json.dumps(event)}")

    try:
        # User requested to read Excel on each request.
        # logger.info("Updating WordBank from source...")
        # app.word_bank.update()

        if 'body' in event:
            body = json.loads(event['body'])
            app.process_update(body)
            return {
                'statusCode': 200,
                'body': json.dumps('Update processed')
            }

        return {
            'statusCode': 400,
            'body': json.dumps('Unrecognized event type')
        }

    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal server error: {str(e)}")
        }
