

const TelegramBot = require('node-telegram-bot-api')
const https = require('https');
const RedisClient = require('./RedisClient')
const { ADMIN_CHAT_ID } = require('./telegramBot_token.json')





module.exports = class {


    constructor(TOKEN, redisInDifferentHost) {

        this.bot = new TelegramBot(TOKEN, { polling: true });
        this.redisClient = new RedisClient(redisInDifferentHost)
        this.availableCommands = `Available commands:
    · /help   ➡ Opens this help section
    · /stop   ➡ Stops me sending words
    · /start  ➡ Makes me start sending words
    · /switch ➡ Switches the translation direction
    · &lt;word&gt; ➡ Translates the word`

        this.bot.on('message', (msg) => {
            const userMsg = msg.text.toString().toLowerCase()
            switch (userMsg) {
                case '/start':
                    this.onStartReceived(msg)
                    break
                case '/stop':
                    this.onStopReceived(msg)
                    break
                case '/help':
                    this.onHelpReceived(msg)
                    break
                case '/switch':
                    this.onSwitchReceived(msg)
                    break
                case '/users':
                    this.onUsersReceived(msg)
                    break
            }
        });

        //broadcast
        this.bot.onText(/^\/broadcast (.|\n)+/g, msg => {
            this.onBroadcastReceived(msg)
        })

        // any word
        this.bot.onText(/^\w+/g, msg => {
            this.onWordReceived(msg)
        })

        this.bot.on('callback_query', (data) => {
            switch (data.data) {
                case 'switch':
                    this.onSwitchReceived(data.message)
                    break;
                case 'start':
                    this.onStartReceived(data.message)
                    break;
                case 'stop':
                    this.onStopReceived(data.message)
                    break;
                default:
                    break
            };
        });
    }



    // ON RECEIVED CALLBACKS
    onStartReceived(msg) {
        this.redisClient.saveUser(msg)
        this.sendStartResponse(msg)
    }
    onStopReceived(msg) {
        this.redisClient.removeChatIdFromActive(msg.chat.id)
        this.sendStopResponse(msg)
    }
    onWordReceived(msg) {
        const word = msg.text.toString().toLowerCase()

        this.redisClient.getUserDir(msg.chat.id).then(dir => {
            const direction = this.getCompleteDirection(dir)

            this.getWordData(word, direction)
                .then(response => this.sendWordResponse(response, msg, direction), (error) => { this.sendFailResponse(error, msg) })
        }
        )
    }

    onHelpReceived(msg) {
        this.sendHelpResponse(msg)
    }
    onSwitchReceived(msg) {

        this.switchLanguage(msg.chat.id).then(dir => this.sendSwitchResponse(msg, dir))

    }

    onUsersReceived(msg) {

        if (msg.chat.id == ADMIN_CHAT_ID) {
            this.redisClient.getUsersInfo().then(users =>
                this.sendUsersResponse(msg, users)
            )
        } else {
            this.sendNoAdminResponse(msg)
        }
    }

    onBroadcastReceived(msg){
        if (msg.chat.id == ADMIN_CHAT_ID) {
            this.redisClient.getUsers()
                .then(chat_ids => {
                    chat_ids.forEach(chat_id =>
                        this.bot.sendMessage(chat_id, msg.text.toString().replace('/broadcast ', ''), { parse_mode: 'HTML' })
                    )
                })

        } else {
            this.sendNoAdminResponse(msg)

        }
    }



    switchLanguage(chatId) {
        return new Promise((resolve, rejec) => this.redisClient.switchLanguage(chatId).then(dir => resolve(dir)))
    }

    // SEND RESPONSE
    sendFailResponse(err, msg) {
        console.log(' - Sending fail msg')
        console.log(err);
        this.bot.sendMessage(msg.chat.id, `There was a failure mate!\nThe word ${this.hightlight(msg.text)} was not in the dictionary 😢
        ` + err, { parse_mode: 'HTML' });

    }

    sendStartResponse(msg) {

        const startMsg =
            `Hello ${msg.from.first_name}!\n${this.availableCommands}
        `
        this.bot.sendMessage(msg.chat.id, startMsg, {
            parse_mode: 'HTML', reply_markup: JSON.stringify({
                inline_keyboard: [
                    [{ text: '/stop', callback_data: 'stop' }]
                ]
            })
        });
    }

    sendStopResponse(msg) {
        const stopMsg =
            `You will no longer receive words!\n...Unles you use /start`
        this.bot.sendMessage(msg.chat.id, stopMsg, {
            parse_mode: 'HTML',
            reply_markup: JSON.stringify({
                inline_keyboard: [
                    [{ text: '/start', callback_data: 'start' }]
                ]
            })
        });
    }

    sendHelpResponse(msg) {

        const helpMsg = `<b>HELP</b>\n${this.availableCommands}`
        this.bot.sendMessage(msg.chat.id, helpMsg, { parse_mode: 'HTML' });
    }



    sendSwitchResponse(msg, dir) {

        const direction = this.getCompleteDirection(dir)

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

    sendUsersResponse(msg, users) {
        let usersMsg = 'Users list\n'
        users.forEach(user => usersMsg += ` - ${user.chatId} ${user.isActive ? '😀' : '😴'}\n   name: ${user.name}\n   dir: ${user.dir === 'es' ? '🇪🇸' : '🇩🇪'}\n`)

        this.bot.sendMessage(msg.chat.id, usersMsg, {
            parse_mode: 'HTML',
        });
    }

    sendNoAdminResponse(msg) {
        let usersMsg = `Loitering around my github?\nDon't hesitate to greet me! 😀`
        this.bot.sendMessage(msg.chat.id, usersMsg, {
            parse_mode: 'HTML',
        });
    }


    sendWordResponse(receivedData, msg, direction) {

        const data = this.parseData(receivedData, direction)
        console.log(` - Sending word response`)

        const fromLan = data.srcLang
        const fromFlag = direction.srcFlag

        const toLan = data.dstLang
        const toFlag = direction.dstFlag

        const fromWord = data.srcWord
        const toWord = data.dstWord

        const fromSentence = data.srcSentence.replace(fromWord, this.hightlight(fromWord)) + '\n'
        const toSentence = data.dstSentence.replace(toWord, this.hightlight(toWord)) + '\n'

        const introLine = 'Here is the translation!\n'

        const fromWordLine = `<b>${fromLan}</b> ${fromFlag} ${fromWord}\n`
        const toLine = `<b>${toLan}</b> ${toFlag} ${toWord}\n`

        const sentencesLine = '\nAnd here a sentence:\n'

        const fromSentenceLine = `<b>${fromLan}</b> ${fromFlag} ${fromSentence}\n`
        const toSentenceLine = `<b>${toLan}</b> ${toFlag} ${toSentence}\n`

        const msgResponse = introLine + fromWordLine + toLine + sentencesLine + fromSentenceLine + toSentenceLine
        this.bot.sendMessage(msg.chat.id, msgResponse, { parse_mode: 'HTML' });

    }

    // GET TRANSLATION HTTP REQUEST
    getWordData(word, dir) {
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

    parseData(receivedData, direction) {
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

    getCompleteDirection(dir) {
        const toEs = dir === 'es'
        return {
            dst: toEs ? 'es' : 'de',
            dstFlag: toEs ? '🇪🇸' : '🇩🇪',
            src: toEs ? 'de' : 'es',
            srcFlag: toEs ? '🇩🇪' : '🇪🇸'
        }
    }

    hightlight(word) { return `<b>${word}</b>` }
    hightlightInSentence(sentence, word) {
        return sentence.replace(word.toLowerCase(), foundWord => `<b> ${foundWord} </b>`)
    }
    broadcastWord(word) {
        this.redisClient.getActiveUsers()
            .then(chat_ids => {
                chat_ids.forEach(chat_id =>
                    this.sendWordMessage(word, chat_id)
                )
            })
    }

    sendWordMessage(word, chat_id) {
        console.log(` - Sending word broadcast response`)
        let examplesMsg = ''
        word.examples.forEach(example => examplesMsg += `\n\n🇩🇪 ${this.hightlightInSentence(example.de, word.de[0])}\n🇪🇸 ${this.hightlightInSentence(example.es, word.es[0])}`)
        const wordMsg = `🇩🇪 ${word.de}\n🇪🇸 ${word.es}${examplesMsg}`
        this.bot.sendMessage(chat_id, wordMsg, { parse_mode: 'HTML' });
    }

}