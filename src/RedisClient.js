const redis = require('redis')

module.exports = class {

    constructor() {
        this.client = redis.createClient()
        this.client.on('error', (err) => console.log('redis error', err))
    }

    async getAllActiveChatId() {
        return new Promise(resolve => {
            this.client.smembers('users', (err, res) => {
                resolve(res)
            });
        });
    }

    saveChatId(chatId) {
        return new Promise(resolve => {
            this.client.sadd(['users', chatId], (err, res) => {
                resolve(res)
            });
        });
    }

    removeChatId(chatId) {
        return new Promise(resolve => {
            this.client.srem(['users', chatId], (err, res) => {
                resolve(res)
            });
        });
    }
}
