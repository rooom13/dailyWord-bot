const SpreadSheetClient = require('./SpreadSheetClient')
const TelegramBot = require('./TelegramBot')
const { TOKEN, TEST_TOKEN } = require('./telegramBot_token.json')


// Set testBo: true when developing
const debug = {
    fakeWord: false,
    testBot: false,
    redisInDifferentHost: process.argv[2] !== 'local'

}
 

console.log('DEBUG', debug)


const sheetClient = new SpreadSheetClient(debug.fakeWord)
const telegramBot = new TelegramBot(debug.testBot ? TEST_TOKEN: TOKEN, debug.redisInDifferentHost )



const getAndSendWord = () => {
    console.log(`Word broadcast sent at ${new Date().toString()}`);

    sheetClient.getWord().then(word => telegramBot.broadcastWord(word))
}





var CronJob = require('cron').CronJob;
new CronJob('30 10,18,20 * * 0-6', function () {
    getAndSendWord()
}, null, true, 'Europe/Madrid');
