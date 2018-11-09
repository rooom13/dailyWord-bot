const SpreadSheetClient = require('./SpreadSheetClient')
const RedisClient = require('./RedisClient')


const sheetClient = new SpreadSheetClient()
const redisClient = new RedisClient()

const isFake = true

redisClient.saveChatId(999)

const getAndSendWord = () => {

    Promise.all([sheetClient.getWord(isFake), redisClient.getAllActiveChatId()]).then( result => console.log(result))

}


getAndSendWord()

/* 
Falta: 
    conectar bot con server 
    Crear users on /Start
    Timer

*/