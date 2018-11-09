const SpreadSheetClient = require('./SpreadSheetClient')
const RedisClient = require('./RedisClient')
const TelegramBot = require('./bot')
const {TOKEN} =  require('./telegramBot_token.json') //'628444584:AAEa3EzJFpRP8IQjEPEwL6olA_YI2Pzfoyo' ||

const sheetClient = new SpreadSheetClient()
const redisClient = new RedisClient()
const telegramBot = new TelegramBot(TOKEN)
const isFake = true

redisClient.saveChatId(335813769)

const getAndSendWord = () => {

    Promise.all([
        sheetClient.getWord(isFake), 
        redisClient.getAllActiveChatId()])
        .then(([word, chat_ids]) => telegramBot.sendWordsToAll(chat_ids, word))

}


getAndSendWord()

/* 
Falta: 
    conectar bot con server 
    Crear users on /Start
    Timer
*/