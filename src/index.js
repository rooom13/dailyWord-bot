const bot = require('./bot.js')
var fs = require('fs');


  const TOKEN = process.argv[2]
  const existRedisClient = false



// If no TOKEN provided via argvs
if (!TOKEN) {

  // Check if TOKEN in TOKEN file
  fs.readFile('TOKEN', 'utf8', function (err, TOKENFILE) {


    if (err) {
      // Prompt error & exit
      console.log(`
    Must provide a token! E.g. yarn start MYTOKEN43242
    or
    add a the token in a file named TOKEN & yarn start
    `)
      process.exit(1);
    }
    const detuschBot = new bot(TOKENFILE, existRedisClient)
  });
} else {

  const detuschBot = new bot(TOKEN, existRedisClient)
}

