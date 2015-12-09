## LitNet Extractor

This project provides a method for automatic social network extraction from literary texts that have been processed with [BookNLP](https://github.com/dbamman/book-nlp).

## Code Example

Build vertex and edge lists:

```
extractor novel.tokens novel.book vertices.csv edges.csv
```

This requires the tokens tab-separated file and .book JSON file that is output by BookNLP.

## Installation

Clone the repo and run 

```
python setup.py install
```