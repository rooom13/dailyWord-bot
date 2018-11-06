const SpreadSheetClient = require('./SpreadSheetClient')

const sheetClient = new SpreadSheetClient()

sheetClient.getWord().then( word => console.log(word) )

// const a = await sheetClient.getWord()
// console.log(a   )