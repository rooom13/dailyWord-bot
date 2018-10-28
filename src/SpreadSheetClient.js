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

