const SpreadSheetClient = require('./SpreadSheetClient')
const TelegramBot = require('./bot')
const {TOKEN} =  require('./telegramBot_token.json') //'628444584:AAEa3EzJFpRP8IQjEPEwL6olA_YI2Pzfoyo' ||

const sheetClient = new SpreadSheetClient()
const telegramBot = new TelegramBot(TOKEN)
const isFake = true


const getAndSendWord = () => {

        sheetClient.getWord(isFake).then(word => telegramBot.broadcastword)

}


getAndSendWord()

/* 
Falta: 
    conectar bot con server 
    Crear users on /Start
    Timer
*/