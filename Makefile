.PHONY: start tests

start:
	uv run --env-file=.env python -m daily_word_bot

tests:
	uv run --env-file=.env pytest tests \
		--cov-report html:reports/coverage \
		--cov=daily_word_bot/ \
		--cov-fail-under=99 \
		--junitxml=reports/tests/report.xml \
		--flake8 ./ \
		--cache-clear
