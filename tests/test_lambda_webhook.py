import json
import pytest
from unittest.mock import MagicMock, patch

from lambda_webhook import lambda_handler, timeout, TimeoutException


# Sample event from Telegram webhook
SAMPLE_WEBHOOK_EVENT = {
    "version": "2.0",
    "routeKey": "$default",
    "rawPath": "/",
    "rawQueryString": "",
    "headers": {
        "x-amzn-tls-cipher-suite": "TLS_AES_128_GCM_SHA256",
        "content-length": "285",
        "x-amzn-tls-version": "TLSv1.3",
        "x-amzn-trace-id": "Root=1-69557760-5776c50e0549894544a6d000",
        "x-forwarded-proto": "https",
        "host": "njkep4w63src4gefb6meylt6ee0swsub.lambda-url.eu-central-1.on.aws",
        "x-forwarded-port": "443",
        "content-type": "application/json",
        "x-forwarded-for": "91.108.5.118",
        "accept-encoding": "gzip, deflate"
    },
    "requestContext": {
        "accountId": "anonymous",
        "apiId": "njkep4w63src4gefb6meylt6ee0swsub",
        "domainName": "njkep4w63src4gefb6meylt6ee0swsub.lambda-url.eu-central-1.on.aws",
        "domainPrefix": "njkep4w63src4gefb6meylt6ee0swsub",
        "http": {
            "method": "POST",
            "path": "/",
            "protocol": "HTTP/1.1",
            "sourceIp": "91.108.5.118",
            "userAgent": None
        },
        "requestId": "d42bcde9-ea99-48e7-817b-dbb9b9ae9ec3",
        "routeKey": "$default",
        "stage": "$default",
        "time": "31/Dec/2025:19:20:00 +0000",
        "timeEpoch": 1767208800939
    },
    "body": json.dumps({
        "update_id": 600588129,
        "message": {
            "message_id": 48161,
            "from": {
                "id": 335813769,
                "is_bot": False,
                "first_name": "r",
                "language_code": "es"
            },
            "chat": {
                "id": 335813769,
                "first_name": "r",
                "type": "private"
            },
            "date": 1767208666,
            "text": "/mylevels",
            "entities": [{"offset": 0, "length": 9, "type": "bot_command"}]
        }
    }),
    "isBase64Encoded": False
}


class TestTimeoutContextManager:
    """Tests for the timeout context manager."""

    def test_timeout_does_not_raise_when_operation_completes(self):
        """Test that no exception is raised when operation completes in time."""
        with timeout(1):
            result = 1 + 1
        assert result == 2

    def test_timeout_raises_exception_when_exceeded(self):
        """Test that TimeoutException is raised when timeout is exceeded."""
        import time
        with pytest.raises(TimeoutException) as exc_info:
            with timeout(1):
                time.sleep(2)
        assert "Operation timed out after 1 seconds" in str(exc_info.value)


class TestLambdaHandler:
    """Tests for the lambda_handler function."""

    @patch.dict('os.environ', {'AWS_LAMBDA_FUNCTION_TIMEOUT_S': '2'})
    @patch('daily_word_bot.app.DAO')
    def test_successful_webhook_processing(self, mock_dao):
        """Test successful processing of a Telegram webhook event."""
        mock_dao.return_value = MagicMock()

        with patch('daily_word_bot.app.App') as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app

            response = lambda_handler(SAMPLE_WEBHOOK_EVENT, None)

            assert response['statusCode'] == 200
            assert json.loads(response['body']) == 'Update processed'
            mock_app.process_update.assert_called_once()

    @patch.dict('os.environ', {'AWS_LAMBDA_FUNCTION_TIMEOUT_S': '2'})
    @patch('daily_word_bot.app.DAO')
    def test_webhook_extracts_correct_body(self, mock_dao):
        """Test that the handler correctly extracts and parses the body."""
        mock_dao.return_value = MagicMock()

        with patch('daily_word_bot.app.App') as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app

            lambda_handler(SAMPLE_WEBHOOK_EVENT, None)

            # Verify the correct update body was passed to process_update
            call_args = mock_app.process_update.call_args[0][0]
            assert call_args['update_id'] == 600588129
            assert call_args['message']['text'] == '/mylevels'
            assert call_args['message']['chat']['id'] == 335813769

    @patch.dict('os.environ', {'AWS_LAMBDA_FUNCTION_TIMEOUT_S': '2'})
    def test_event_without_body_returns_400(self):
        """Test that event without body returns 400 status code."""
        event_without_body = {
            "version": "2.0",
            "routeKey": "$default"
        }

        response = lambda_handler(event_without_body, None)

        assert response['statusCode'] == 400
        assert 'Unrecognized event type' in response['body']

    @patch.dict('os.environ', {'AWS_LAMBDA_FUNCTION_TIMEOUT_S': '2'})
    @patch('daily_word_bot.app.DAO')
    def test_exception_during_processing_returns_500(self, mock_dao):
        """Test that exceptions during processing return 500 status code."""
        mock_dao.return_value = MagicMock()

        with patch('daily_word_bot.app.App') as mock_app_class:
            mock_app = MagicMock()
            mock_app.process_update.side_effect = Exception("Database error")
            mock_app_class.return_value = mock_app

            response = lambda_handler(SAMPLE_WEBHOOK_EVENT, None)

            assert response['statusCode'] == 500
            assert 'Internal server error' in response['body']

    @patch('lambda_webhook.AWS_LAMBDA_FUNCTION_TIMEOUT_S', 2)
    @patch('daily_word_bot.app.DAO')
    def test_timeout_returns_504(self, mock_dao):
        """Test that timeout during processing returns 504 status code."""
        mock_dao.return_value = MagicMock()

        with patch('daily_word_bot.app.App') as mock_app_class:
            mock_app = MagicMock()

            # Simulate a long-running operation that will trigger timeout (3 seconds > 2 seconds timeout)
            def slow_process(*args, **kwargs):
                import time
                time.sleep(3)

            mock_app.process_update.side_effect = slow_process
            mock_app_class.return_value = mock_app

            response = lambda_handler(SAMPLE_WEBHOOK_EVENT, None)

            assert response['statusCode'] == 504
            assert 'Request timeout' in response['body']

    @patch.dict('os.environ', {'AWS_LAMBDA_FUNCTION_TIMEOUT_S': '2'})
    @patch('daily_word_bot.app.DAO')
    def test_invalid_json_body_returns_500(self, mock_dao):
        """Test that invalid JSON body returns 500 status code."""
        mock_dao.return_value = MagicMock()
        event_with_invalid_json = {
            **SAMPLE_WEBHOOK_EVENT,
            "body": "not valid json"
        }

        response = lambda_handler(event_with_invalid_json, None)

        assert response['statusCode'] == 500
        assert 'Internal server error' in response['body']


class TestLambdaHandlerIntegration:
    """Integration-style tests for lambda_handler."""

    @patch.dict('os.environ', {'AWS_LAMBDA_FUNCTION_TIMEOUT_S': '2'})
    def test_full_event_structure_is_logged(self, caplog):
        """Test that the full event structure is logged."""
        import logging
        with caplog.at_level(logging.INFO):
            lambda_handler({"version": "2.0"}, None)

        assert 'Received webhook event' in caplog.text

    @patch.dict('os.environ', {'AWS_LAMBDA_FUNCTION_TIMEOUT_S': '2'})
    @patch('daily_word_bot.app.DAO')
    def test_mylevels_command_event(self, mock_dao):
        """Test processing of /mylevels command from actual Telegram event."""
        mock_dao.return_value = MagicMock()

        with patch('daily_word_bot.app.App') as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app

            response = lambda_handler(SAMPLE_WEBHOOK_EVENT, None)

            assert response['statusCode'] == 200

            # Verify the message command was detected
            call_args = mock_app.process_update.call_args[0][0]
            entities = call_args['message']['entities']
            assert len(entities) == 1
            assert entities[0]['type'] == 'bot_command'
