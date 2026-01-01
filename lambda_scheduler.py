import json
import logging
from daily_word_bot.app import App

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the app outside the handler to reuse it across warm invocations
app = App()


def lambda_handler(event, context):
    """
    AWS Lambda handler function for Scheduled Events.
    """
    logger.info(f"Received scheduled event: {json.dumps(event)}")

    try:
        # User requested to read Excel on each request.
        logger.info("Updating WordBank from source...")
        app.word_bank.update()

        # Pass the detail or the whole event to handle different schedules
        app.process_send_word(event.get('detail', {}))
        return {
            'statusCode': 200,
            'body': json.dumps('Scheduled event processed')
        }

    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal server error: {str(e)}")
        }
