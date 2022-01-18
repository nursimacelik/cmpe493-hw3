# CMPE 493 Introduction to Information Retrieval Homework 3

Book recommendation program.

1. When you run for the first time, create a file listing Goodreads urls of books. This will be the dataset.

```
> python3 main.py
Enter a file path or url: my_url_list.txt
```
Running this way will dump two files: "matrix.pickle" and "vocabulary.json". You don't use these, they are necessary for further queries.

2. For the query part, provide the url of a book.
```
> python3 main.py
Enter a file path or url: https://www.goodreads.com/book/show/3450744-nudge
```
Prints metadata of the book such as title, authors, description. Then recommends 18 books based on cosine similarity between their descriptions and genres. Also, evaluates the result by comparing our recommendations with recommended books in Goodreads. Prints precision and average precision.
