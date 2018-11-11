const redis = require('redis')

module.exports = class {

    constructor(fakeUsers) {
        this.client = redis.createClient()
        this.fakeUsers = fakeUsers
        this.client.on('error', (err) => console.log('redis error', err))
    }

    async getAllActiveChatId() {

        if(this.fakeUsers){
            return new Promise(resolve => resolve(['335813769']))
        }
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
