const GoogleSpreadsheet = require('google-spreadsheet')
const { promisify } = require('util')

const credentials = require('./service-account.json')


module.exports = class {
  constructor(){
  this.SPREADSHEET_ID = `1Jl1L0PwF4ftYMMvGOZ-_1ow_Z2ckxtAYX106TbpRlb0`
  this.doc = new GoogleSpreadsheet(this.SPREADSHEET_ID)


  }

  async getWord() {
  
    await promisify(this.doc.useServiceAccountAuth)(credentials)
    
    const info = await promisify(this.doc.getInfo)()
    
    console.log(`Loaded: ` + info.title + ` by ` + info.author.email)
    
    const sheet = info.worksheets[0]
    const wordCount = sheet.rowCount
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
      de: cells[0].value.split('/'),
      es: cells[1].value.split('/'),
      examples: getExamples()
    }
    
    
    console.log('word obtained')
    return new Promise(resolve => {
        resolve(word);
    });
  }
}








//accessSpreadsheet()

