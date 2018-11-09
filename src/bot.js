

const TelegramBot = require('node-telegram-bot-api')
const https = require('https');
const redis = require('redis')





module.exports = class {


    constructor(TOKEN) {



        this.bot = new TelegramBot(TOKEN, { polling: true });
        let direction = { src: 'es', srcFlag: '🇪🇸', dst: 'de', dstFlag: '🇩🇪' }

        this.bot.on('message', (msg) => {

            const userMsg = msg.text.toString().toLowerCase()
            switch (userMsg) {
                case '/start':
                    this.onStartReceived(msg)
                    break
                case '/help':
                    this.onHelpReceived(msg)
                    break
                case '/lang':
                    this.onLangReceived(msg)
                    break
                case '/switch':
                    this.onSwitchReceived(msg)
                    break
                case '/rand':
                    this.sendWordsToAll([1], {})
                    break
                default:
                    this.onWordReceived(msg)
                    break
            }
        });
        this.bot.on('callback_query', (data) => {
            switch (data.data) {
                case 'switch':
                    this.onSwitchReceived(data.message)
                    break;
                case 'deToEs':
                    console.log('deToEs');
                default:
                    break

            };

        });
    }



    // ON RECEIVED CALLBACKS
    onStartReceived(msg){

        this.sendStartResponse(msg)
    }
    onRandReceived(msg){

    }
    onWordReceived(msg){
        const word = msg.text.toString().toLowerCase()
        this.getWordData(word, direction)
            .then(response => this.sendWordResponse(response, msg), (error) => { this.sendFailResponse(error, msg) })
    }
    onHelpReceived(msg){
        this.sendHelpResponse(msg)
    }
    onSwitchReceived(msg){
        this.switchLanguages()
        this.sendSwitchResponse(msg)
    }

    switchLanguages(){
        if (direction.src === 'es') {
            direction = {
                src: 'de',
                srcFlag: '🇩🇪',
                dst: 'es',
                dstFlag: '🇪🇸'
            }
        } else {
            direction = {
                src: 'es',
                srcFlag: '🇪🇸',
                dst: 'de',
                dstFlag: '🇩🇪'
            }
        }
    }

    // SEND RESPONSE
    sendFailResponse(err, msg){
        console.log(' - Sending fail msg')
        console.log(err);
        this.bot.sendMessage(msg.chat.id, `There was a failure mate!\nThe word ${this.hightlight(msg.text)} was not in the dictionary 😢
        ` + err, { parse_mode: 'HTML' });

    }

    sendStartResponse(msg){

        const startMsg =
            `Hello ${msg.from.first_name}!
        Available commands:
        · /help  ➡ Opens this help section
        · /from  ➡ Sets the source language
        · /lang  ➡ Sets the translation languages
        · &lt;word&gt; ➡ Translates the word`
        this.bot.sendMessage(msg.chat.id, startMsg, { parse_mode: 'HTML' });
    }
    sendHelpResponse(msg){

        const helpMsg =
            `<b>HELP</b>
        Available commands:
        · /help  ➡ Opens this help section
        · /from  ➡ Sets the source language
        · /lang  ➡ Sets the translation languages
        · &lt;word&gt; ➡ Translates the word`
        this.bot.sendMessage(msg.chat.id, helpMsg, { parse_mode: 'HTML' });
    }

    sendSwitchResponse(msg){
        const switchMsg =
            `Translating from ${direction.src} ${direction.srcFlag} to ${direction.dst} ${direction.dstFlag}`
        this.bot.sendMessage(msg.chat.id, switchMsg, {
            parse_mode: 'HTML',
            reply_markup: JSON.stringify({
                inline_keyboard: [
                    [{ text: 'Switch 🔄', callback_data: 'switch' }]
                ]
            })
        });
    }
    sendLangResponse(msg){

        const langMsg =
            `Choose the translation languages`
        this.bot.sendMessage(msg.chat.id, langMsg, {
            parse_mode: 'HTML',
            reply_markup: JSON.stringify({
                inline_keyboard: [
                    [{ text: '🇪🇸 ES  ➡  🇩🇪 DE', callback_data: 'esToDe' }],
                    [{ text: '🇩🇪 DE  ➡  🇪🇸 ES', callback_data: 'deToEs' }]
                ]
            })

        });
    }
    sendWordResponse(receivedData, msg){

        const data = this.parseData(receivedData)
        console.log(` - Sending word response`)

        const fromLan = data.srcLang
        const fromFlag = '🇪🇸'

        const toLan = data.dstLang
        const toFlag = '🇩🇪'

        const fromWord = data.srcWord
        const toWord = data.dstWord

        const fromSentence = data.srcSentence.replace(fromWord, this.hightlight(fromWord)) + '\n'
        const toSentence = data.dstSentence.replace(toWord, this.hightlight(toWord)) + '\n'

        const introLine = 'Here the translation!\n'

        const fromWordLine = `<b>${fromLan}</b> ${fromFlag}   ➡  ${fromWord}\n`
        const toLine = `<b>${toLan}</b> ${toFlag}   ➡  ${toWord}\n`

        const sentencesLine = 'And here a sentence:\n'

        const fromSentenceLine = `<b>${fromLan}</b> ${fromFlag}   ➡  ${fromSentence}\n`
        const toSentenceLine = `<b>${toLan}</b> ${toFlag}   ➡  ${toSentence}\n`

        const msgResponse = introLine + fromWordLine + toLine + sentencesLine + fromSentenceLine + toSentenceLine
        this.bot.sendMessage(msg.chat.id, msgResponse, { parse_mode: 'HTML' });

    }
    sendRandomResponse(data, msg){

        console.log(` - Sending word response`)
        const parts = data.split('/')
        const msgResponse = `🇬🇧${parts[0]}\n🇩🇪${parts[1]} / ${parts[2]}`
        this.bot.sendMessage(msg.chat.id, msgResponse, { parse_mode: 'HTML' });

    }

    // GET TRANSLATION HTTP REQUEST
    getWordData(word, dir){
        const url = `https://linguee-api.herokuapp.com/api?q=${word}&src=${dir.src}&dst=${dir.dst}`
        console.log('request', url);
        return new Promise((resolve, reject) => {
            https.get(url, (resp) => {
                console.log("Response status: " + resp.statusCode);
                if (resp.statusCode === 200) {
                    let data = '';
                    resp.on('data', (chunk) => {
                        data += chunk;
                    });
                    resp.on('end', () => {
                        console.log('Got data')
                        resolve(JSON.parse(data))
                    });
                } else {
                    console.log('Failed for' + word);
                    reject(resp.statusCode)
                }
            }).on("error", (err) => {
                console.log(err);
                reject(err);
            });
        }
        )
    }

    parseData(receivedData){
        console.log(` - Parsing`)

        const parsedData = {
            srcLang: receivedData.src_lang,
            dstLang: receivedData.dst_lang,
            srcFlag: direction.srcFlag,
            dstFlag: direction.dstFlag,
            srcWord: receivedData.query,
            dstWord: receivedData.exact_matches[0].translations[0].text,
            srcSentence: receivedData.real_examples[0].src,
            dstSentence: receivedData.real_examples[0].dst
        }

        return parsedData
    }

    hightlight(word){`<b> ${word} </b>`}




    sendWordsToAll(chat_ids, word) {
        chat_ids.forEach(chat_id =>
            this.bot.sendMessage(chat_id, `Hola que passa`, { parse_mode: 'HTML' }))
    }
}
