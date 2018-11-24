const SpreadSheetClient = require('./SpreadSheetClient')
const TelegramBot = require('./TelegramBot')
const { TOKEN, TEST_TOKEN } = require('./telegramBot_token.json')


// Set testBo: true when developing
const debug = {
    fakeWord: false,
    fakeUsers: true,
    testBot: true,
    redisInDifferentHost: process.argv[2] !== 'local'

}
 

console.log('DEBUG')
console.log(debug)


const sheetClient = new SpreadSheetClient(debug.fakeWord)
const telegramBot = new TelegramBot(debug.testBot ? TEST_TOKEN: TOKEN, debug.redisInDifferentHost, debug.fakeUsers)



const getAndSendWord = () => {
    sheetClient.getWord().then(word => telegramBot.broadcastWord(word))
}



var CronJob = require('cron').CronJob;
new CronJob('30 10,18,20 * * 0-6', function () {
    console.log(`Word broadcast sent at ${new Date().toString()}`);
    getAndSendWord()

}, null, true, 'Europe/Madrid');