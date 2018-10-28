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






/*
const GoogleSpreadsheet = require('google-spreadsheet')
const { promisify } = require('util')

const credentials = require('./service-account.json')

const SPREADSHEET_ID2 = `1Jl1L0PwF4ftYMMvGOZ-_1ow_Z2ckxtAYX106TbpRlb0`
async function accessSpreadsheet() {
  const doc = new GoogleSpreadsheet(SPREADSHEET_ID2)
  await promisify(doc.useServiceAccountAuth)(credentials)
  const info = await promisify(doc.getInfo)()
  console.log(`Loaded doc: ` + info.title + ` by ` + info.author.email)
  const sheet = info.worksheets[0]
  console.log(
    `sheet 1: ` + sheet.title + ` ` + sheet.rowCount + `x` + sheet.colCount
  )





  const cells = await promisify(sheet.getCells)({
    range:  'B3:B9',

    'return-empty': true,
})
for (const cell of cells) {
    console.log(`${cell.row},${cell.col}: ${cell.value}`)
}

}

accessSpreadsheet()
*/
