const SpreadSheetClient = require('./SpreadSheetClient')
const TelegramBot = require('./bot')
// const CronJob = require('cron'),CronJob;
const { TOKEN } = require('./telegramBot_token.json') //'628444584:AAEa3EzJFpRP8IQjEPEwL6olA_YI2Pzfoyo' ||

const sheetClient = new SpreadSheetClient()
const telegramBot = new TelegramBot(TOKEN)
const isFake = true




const getAndSendWord = () => {
    sheetClient.getWord(isFake).then(word => telegramBot.broadcastWord(word))
}
// getAndSendWord()



var CronJob = require('cron').CronJob;
new CronJob('40 12,18,20 * * 0-6', function () {
    console.log('You will see this message every second');
    getAndSendWord()

}, null, true, 'Europe/Madrid');