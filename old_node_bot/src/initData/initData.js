/*
    Ugly Script that stores the words in redis
*/

const redis = require('redis')
var client = redis.createClient()


var lineReader = require('readline').createInterface({
  input: require('fs').createReadStream('initData/words_raw.txt')
});
/*
lineReader.on('line',  (line) => {
    const data = parseLine(line)
    saveToRedis(data);
})*/

const parseLine = (line) => {
    const parts = line.split('.')
    return {
        key: parts[0],
        data: parts[1]
    }
}

const parseUser = (msg) => {
    return {
        key: 'u'+msg.chat.id,
        data:
    }
}


const saveUserToRedis = (user) => {
    client.hmset(user.key, "chat_id", user.chat_id, "name", user.name, "times", "5", function (err, res) {});
}


const saveToRedis = (data) => {
    client.set(data.key, data.data, redis.print);
}
