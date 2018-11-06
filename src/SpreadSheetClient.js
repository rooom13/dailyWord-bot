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

  const wordCount = sheet.rowCount

  console.log(`word count: ${wordCount}`)

  const rndIndex = Math.floor(Math.random() *(wordCount-2)) +2



  const cells = await promisify(sheet.getCells)({
    range: `B${rndIndex}:B${rndIndex}`,

    'return-empty': true,
  })

  const word = {
    de: cells[0].value,
    es: cells[1].value,
    examples: []
    



  }
  console.log(word)


}

accessSpreadsheet()

