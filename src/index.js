// const bot = require('./bot.js')
// const detuschBot = new bot()

const GoogleSpreadsheet = require('google-spreadsheet')
const { promisify } = require('util')

const credentials = require('./service-account.json')

const SPREADSHEET_ID = `16DuyNoR14sthq8AEs4UAXzVI7HvOE9XME_514wMTiXg`
async function accessSpreadsheet() {
  const doc = new GoogleSpreadsheet(SPREADSHEET_ID)
  await promisify(doc.useServiceAccountAuth)(credentials)
  const info = await promisify(doc.getInfo)()
  console.log(`Loaded doc: ` + info.title + ` by ` + info.author.email)
  const sheet = info.worksheets[0]
  console.log(
    `sheet 1: ` + sheet.title + ` ` + sheet.rowCount + `x` + sheet.colCount
  )



  const cells = await promisify(sheet.getCells)({
    'min-row': 1,
    'max-row': 5,
    'min-col': 1,
    'max-col': 2,
    'return-empty': true,
})
for (const cell of cells) {
    console.log(`${cell.row},${cell.col}: ${cell.value}`)
}
console.log(cells)

}

accessSpreadsheet()
