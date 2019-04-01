const fs = require("fs")

let getExamples = (exs) => {
    let examples = []
    let i = 0
    let example = null

    for (const cell of exs) {
        if (i % 2) {
            example.es = cell
            examples.push(example)
        }
        else {
            example = {}
            example.de = cell
        }

        ++i
    }
    return examples
}

const num = process.argv[2]


const FILENAME = 'testData.txt'
fs.readFile(FILENAME, 'utf8', (err, data) => {
    const words = data.split("\n")
    const rnd =  num || Math.floor(Math.random() * words.length)
    console.error(rnd)
    const wordArray = words[rnd].split("\t").filter(a => a)

    const word = {
        de: wordArray[0],
        es: wordArray[1],
        examples: getExamples(wordArray.splice(2))
    }

    word.examples.forEach( e => console.log(highlight(word.de, e.de)))
    

}
)




function highlight(wordLine, ex){
    const terms = wordLine.split("/")
    let termsWithoutArticles = []
    let highlighted = ex
    console.log(wordLine.split("x"))
    console.log(terms)
    terms.forEach( w =>  termsWithoutArticles.push(w.replace(/die |das |der |el |la /g, '') ))
    console.log(termsWithoutArticles)

    termsWithoutArticles.forEach( t => highlighted = highlighted.replace(t, wordFinded =>  `**${wordFinded}**`) )
    return highlighted

}