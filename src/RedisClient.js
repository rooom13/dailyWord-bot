const redis = require('redis')

module.exports = class {

    constructor(redisInDifferentHost, fakeUsers) {
        this.fakeUsers = fakeUsers

        if (!this.fakeUsers) {
            this.client = redisInDifferentHost ? redis.createClient({ host: 'redis' }) : redis.createClient()
            this.client.on('error', (err) => console.log('redis error', err))
        }
    }

    async getAllActiveChatId() {

        if (this.fakeUsers) {
            return new Promise(resolve => resolve(['335813769']))
        }
        return new Promise(resolve => {
            this.client.smembers('users', (err, res) => {
                resolve(res)
            });
        });
    }

    saveChatId(chatId) {

        if (!this.fakeUsers) {


            return new Promise(resolve => {
                this.client.sadd(['users', chatId], (err, res) => {
                    resolve(res)
                });
            });
        }
    }

    removeChatId(chatId) {
        if (!this.fakeUsers) {
            return new Promise(resolve => {
                this.client.srem(['users', chatId], (err, res) => {
                    resolve(res)
                });
            });
        }
    }
}
