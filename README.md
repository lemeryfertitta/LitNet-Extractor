## LitNet Extractor

This project provides a method for automatic social network extraction from literary texts that have been processed with [BookNLP](https://github.com/dbamman/book-nlp).

## Code Example

Write to a GraphML file:

```
lnextract booknlp_tokens.csv booknlp_chars.json graphml my_network.graphml
```

This requires the tokens tab-separated (novel_name.tokens) file and character JSON file (book.id.book) that is output by BookNLP.

## Installation

Clone the repo and run 

```
python setup.py install
```
