const GoogleSpreadsheet = require('google-spreadsheet')
const { promisify } = require('util')

const credentials = require('./service-account.json')


module.exports = class {
  constructor(fakeWordRequest) {
    this.SPREADSHEET_ID = `1Jl1L0PwF4ftYMMvGOZ-_1ow_Z2ckxtAYX106TbpRlb0`
    this.doc = new GoogleSpreadsheet(this.SPREADSHEET_ID)
    this.fakeWordRequest = fakeWordRequest

  }

  async getWord() {
    if (this.fakeWordRequest) {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            de: 'Kartoffel',
            es: 'Patata',
            examples: [{ de: 'Die Kartoffel ist lecker', es: 'La patata es deliciosa' }, { de: 'Die Kartoffel ist kaput', es: 'La patata está rota' }]
          })
        }, 0)
      });
    }



    await promisify(this.doc.useServiceAccountAuth)(credentials)

    const info = await promisify(this.doc.getInfo)()
    const sheet = info.worksheets[0]
    const wordCount = sheet.rowCount
    const rndIndex = Math.floor(Math.random() * (wordCount - 2)) + 2
    const cells = await promisify(sheet.getCells)({
      range: `B${rndIndex}:K${rndIndex}`,
      'return-empty': true,
    })

    let getExamples = () => {
      let examples = []
      let i = 0
      let example = null
      for (const cell of cells.splice(2)) {
        if (cell.value) {
          if (i % 2) {
            example.es = cell.value
            examples.push(example)
          }
          else {
            example= {}
            example.de = cell.value
          }
        }
        ++i
      }
      return examples
    }

    let word = {
      de: cells[0].value.split('/'),
      es: cells[1].value.split('/'),
      examples: getExamples()
    }

    return new Promise(resolve => {
      resolve(word);
    });

  }
}
