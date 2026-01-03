# [@dailyWord_bot](https://telegram.me/dailyWord_bot) (Check it, it's live :globe_with_meridians:)
[![dailyWord-bot](https://github.com/rooom13/dailyWord-bot/actions/workflows/github-action.yml/badge.svg?branch=master)](https://github.com/rooom13/dailyWord-bot/actions/workflows/github-action.yml)

This repository contains the source code for [**@dailyWord_bot**](https://telegram.me/dailyWord_bot), a Telegram Bot that eases learning new words & expressions in German and Spanish.
## What does @dailyWord_bot do?
**@dailyWord_bot** will send you daily words with examples with a set of sentence examples. You can as well mark/unmark the words that you already know so they won't appear anymore.

![screenshot](https://user-images.githubusercontent.com/32899185/100937837-f65e3b00-34f3-11eb-87cd-803d6fefd932.png)

The words data bank is updated dynamically with the will of collaborators via a Google Spread Sheet. Do not hesitate reaching out to collaborate! :blush:


## How can I start using it?
Just open Telegram and start a conversation with [**@dailyWord_bot**](https://telegram.me/dailyWord_bot)

### Tech Stack
| What | Tech |
| ------ | ------ |
| development | python |
| database | redis |
| deployment | AWS Lambda, Terraform, Docker |
| scheduled tasks | AWS EventBridge (CloudWatch Events) |
| CI | Github Actions to enforce merge checks for tests, static analysis & coverage |

## AWS Infrastructure

The bot is deployed on AWS using Terraform for infrastructure as code. The infrastructure includes:

### Lambda Functions
- **webhook Lambda**: Handles incoming Telegram webhook requests
- **scheduler Lambda**: Runs scheduled tasks (e.g., updating word bank)

### Scheduled Tasks
The scheduler Lambda is triggered daily at **12:30 PM UTC** using AWS EventBridge (CloudWatch Events) with a cron expression: `cron(30 12 * * ? *)`

**Note**: AWS EventBridge cron expressions use UTC timezone. To schedule for a different timezone:
- 12:30 PM UTC = 1:30 PM CET (Central European Time)
- 12:30 PM UTC = 2:30 PM CEST (Central European Summer Time)

### Deployment

1. Build the deployment package:
   ```bash
   make build
   ```

2. Deploy infrastructure with Terraform:
   ```bash
   make deploy
   ```

3. Set up required environment variables in `terraform.tfvars`:
   ```hcl
   bot_token      = "your-telegram-bot-token"
   admin_chat_ids = "comma,separated,admin,ids"
   ```


