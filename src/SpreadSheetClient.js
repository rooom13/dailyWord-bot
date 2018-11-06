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
    range: `B${rndIndex}:K${rndIndex}`,

    'return-empty': true,
  })


    let getExamples = () => {

    let examples = []
    let i = 0
    for(const cell of cells.splice(2)){
      let example = {}
      if(cell.value){
      if(i%2)example.de = cell.value
      else example.es = cell.value

      examples.push(example)
    
    }}
      return examples
    }

   

   let word = {
    de: cells[0].value,
    es: cells[1].value,
    examples: getExamples()
  }
  
/*   let i = 0  
  for(const cell of cells){
    console.log(i)
    if(i == 0) word.de = cell.value
    else if(i == 1) word.es = cell.value
    else
    {
      let example = {}
      if(i%2) example.de = cell.value
      else example.es = cell.value
      word.examples.push(example)
    }
    ++i
    console.log(i)

  }  */
  

 
  console.log(word)

  


}

accessSpreadsheet()

