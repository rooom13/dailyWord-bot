const SpreadSheetClient = require('./SpreadSheetClient')
const TelegramBot = require('./TelegramBot')
const { TOKEN } = require('./telegramBot_token.json')



const debug = {
    fakeWord: false,
    fakeUsers: false
}

const sheetClient = new SpreadSheetClient(debug.fakeWord)
const telegramBot = new TelegramBot(TOKEN, debug.fakeUsers)



const getAndSendWord = () => {
    sheetClient.getWord().then(word => telegramBot.broadcastWord(word))
}
// getAndSendWord()



var CronJob = require('cron').CronJob;
new CronJob('40 12,18,20 * * 0-6', function () {
    console.log(`Word broadcast sent at ${new Date().toString()}`);
    getAndSendWord()

}, null, true, 'Europe/Madrid');