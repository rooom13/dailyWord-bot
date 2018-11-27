const redis = require('redis')

module.exports = class {

    constructor(redisInDifferentHost) {

        this.client = redisInDifferentHost ? redis.createClient({ host: 'redis' }) : redis.createClient()
        this.client.on('error', (err) => console.log('redis error', err))

    }

    async getActiveUsers() {

        return new Promise(resolve => {
            this.client.smembers('activeUsers', (err, res) => {
                resolve(res)
            });
        });
    }

    async getUsers() {

        return new Promise(resolve => {
            this.client.smembers('users', (err, res) => {
                resolve(res)
            });
        });
    }

    async getUserInfo(chatId) {

        return new Promise(resolve => {
            this.client.hgetall([`userInfo:${chatId}`], (err, res) => {
                res.isActive = res.isActive === '1'
                res.chatId = chatId
                resolve(res)
            })
        })
    }

    async getUsersInfo() {


        return new Promise(resolve => {
            this.getUsers().then(chatIds => {

                let promises = []
                chatIds.forEach(chatId => promises.push(this.getUserInfo(chatId)))
                Promise.all(promises).then(users => resolve(users))
            })
        })
    }

    saveUser(msg) {

        //all users id
        this.client.sadd(['users', msg.chat.id], (err, res) => {
            if (err) console.log(err)
        });

        //user info
        this.client.hmset([`userInfo:${msg.chat.id}`, 'name', msg.chat.first_name, 'isActive', '1', 'dir', 'es'], (err, res) => {
            if (err) console.log(err)
        });

        //active users id
        this.client.sadd(['activeUsers', msg.chat.id], (err, res) => {
            if (err) console.log(err)
        });

    }


    removeChatIdFromActive(chatId) {

        this.client.srem(['activeUsers', chatId], (err, res) => {
            if (err) console.log(err)
        });
        this.client.hset([`userInfo:${chatId}`, 'isActive', '0'])
    }

    async getUserDir(chatId) {
        return new Promise(resolve => {
            this.client.hget([`userInfo:${chatId}`, 'dir'], (err, dir) => resolve(dir))
        })
    }

    async switchLanguage(chatId) {


        return new Promise(resolve => {
            this.getUserDir(chatId).then(dir => {

                const newDir = (dir === 'es') ? 'de' : 'es'
                this.client.hset([`userInfo:${chatId}`, 'dir', newDir], (err, res) => resolve(newDir))
            })
        })
    }
}
