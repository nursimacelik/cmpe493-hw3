import re
import urllib.request
import math
import pickle
import json
from Book import Book


# takes a url as input and returns the Book object constructed from the book residing in the url
def extract_book(url):
    # read the html
    page_html = urllib.request.urlopen(url).read().decode("utf-8")

    # get title
    tr = re.search(r"<h1 id=\"bookTitle\".*?>\n(.*?)\n<", page_html)
    if not tr:
        print("Title cannot be found for")
        print(url)
        title = ""
    else:
        title = tr.group(1).strip()

    # get list of authors
    authors = re.findall(r"<a\s*class=\"authorName.*?><span.*?>(.*?)</span>", page_html)
    if not authors:
        print("Authors cannot be found for")
        print(url)


    # get description
    # some books have two descriptions: one is longer than the other and can be seen when we click on "more" button
    # first, get the div containing description(s)
    desc_div = re.findall(r"<div\s*?id=\"description\".*?>.*?<span id=\"freeText.*?>.*?</span>.*?<span.*?>.*?</span>", page_html, re.DOTALL)
    if not desc_div:
        print("Description cannot be found for")
        print(url)
        description = ""
    else:
        # parse according to span keyword
        desc_spans = re.findall("<span id=\"freeText.*?>(.*?)</span>", desc_div[0], re.DOTALL)
        
        # the description we want is the last one
        # if only one description exists, it will work too
        description = desc_spans[-1]

    # get list of urls of books recommended by Goodreads for the current book
    recommended_books = re.findall(r"id=\'bookCover.*?<a href=\"(.*?)\">\s*?<img", page_html, re.DOTALL)

    # get list of genres
    genres = re.findall(r"googletag.pubads\(\)\.setTargeting\(\"shelf.*?\[(.*?)\]", page_html, re.DOTALL)

    # create a Book object and return
    return Book(url,title,authors,description,recommended_books,genres)

# takes v1, v2: lists (= vectors)
# returns the cosine similarity
def get_cos_sim(v1, v2):
    similarity = 0
    for i in range(0,len(v1)):
        similarity += v1[i] * v2[i]
    return similarity

# takes v: list (= vector)
# returns the normalized version
def normalize(v):
    l = 0
    for element in v:
        l += element**2
    l = math.sqrt(l)
    if l != 0:
        v = [i/l for i in v]
    
    return v


# main

# take input from user

inp = input("Enter a file path or url:")

# our results will be based on a score s, where
# s = alpha*cos_sim(descriptions) + (1-alpha)*cos_sim(genres) TODO
alpha = 0.5

if "http" in inp:
    # input is a url
    # there should be already two files: matrix.pickle and vocabulary.json

    # matrix[url] is a dictionary, from url to Book
    # ex. matrix["https://www.goodreads...."] = Book object at 0x...
    with open("matrix.pickle","rb") as infile:
        matrix = pickle.load(infile)

    # vocabulary is a dictionary, from word to document frequency
    # ex. vocabulary["apple"] = 2
    with open("vocabulary.json","r") as infile:
        vocabulary = json.load(infile)


    inp = inp.strip()
    # check if given url was already in corpus
    if inp not in matrix:
        # not in corpus
        # create Book from input url and convert to vector
        N = len(vocabulary)
        book = extract_book(inp)
        for word in vocabulary:
            if word in book.tokens:
                tf = 1 + math.log10(book.tokens.count(word))
            else:
                tf = 1
            idf = math.log10(N/vocabulary[word])
            
            book.vector.append(tf*idf)
        
        book.vector = normalize(book.vector)
        
    else:
        # it was in corpus
        # simply fetch it from matrix
        book = matrix[inp]

    print("\nMetadata of the given book:\n")
    print(book)
    print("Description: ")
    print(book.description)


    # calculate similarity between the book and all other books
    # store similarities in cos_similarities dictionary
    cos_similarities = dict()
    for url,b in matrix.items():
        sim = get_cos_sim(b.vector, book.vector)
        cos_similarities[url] = sim

    # same process for genres
    cos_sim_genre = dict()
    for url,b in matrix.items():
        sim = get_cos_sim(b.genre_vector, book.genre_vector)
        cos_sim_genre[url] = sim
    
    # merge the cosine similarities for description and genres
    final_cos_sim = dict()
    for url in cos_similarities:
        final_sim = alpha * cos_sim_genre[url] + (1 - alpha)*cos_similarities[url]
        if final_sim not in final_cos_sim:
            final_cos_sim[final_sim] = [url]
        else:
            final_cos_sim[final_sim].append(url)

    # find the most similar 18 books and print
    count = 0
    predicted_books = []
    print("\nWe recommend the following books:\n")
    for sim in sorted(final_cos_sim, reverse=True)[1:]:
        if count == 18:
            break
        # for every similarity value, there may be multiple books
        for url in final_cos_sim[sim]:
            print(count+1, end=". ")
            print(matrix[url])
            predicted_books.append(url)
            count += 1
        print("\n")

    # evaluation
    # compare predicted_books and book.recommended_books

    avg_precision_sum = 0
    relevant_count = 0
    loop_count = 1
    for url in predicted_books:
        if url in book.recommended_books:
            relevant_count += 1
            avg_precision_sum += relevant_count/loop_count
        loop_count += 1

    if(len(predicted_books) != 0):
        precision = relevant_count/len(predicted_books)
    else:
        precision = 0
    if(relevant_count != 0):
        avg_precision = avg_precision_sum/relevant_count
    else:
        avg_precision = 0

    print("Precision is " + str(precision))
    print("Average Precision is " + str(avg_precision))
        
    
else:
    file = open(inp)

    books = []              # array storing Book objects
    vocabulary = dict()     # word -> document frequency
    all_genres = dict()     # genre -> document frequency
    res = dict()            # url -> book

    for line in file:
        myUrl = line.strip()
        try:
            # read html and extract Book from it
            b = extract_book(myUrl)
            books.append(b)
            # add tokens to vocabulary
            for token in set(b.tokens):
                if token in vocabulary:
                    vocabulary[token] += 1
                else:
                    vocabulary[token] = 1
            
            for genre in set(b.genres):
                if genre in all_genres:
                    all_genres[genre] += 1
                else:
                    all_genres[genre] = 1
        
        except:
            pass

    # after the loop ended
    # start a new loop traversing books

    N = len(books)
    M = len(all_genres)
    # calculate normalized tf-idf vectors for each book
    for book in books:
        for word in vocabulary:
            if word in book.tokens:
                tf = 1 + math.log10(book.tokens.count(word))
            else:
                tf = 1
            idf = math.log10(N/vocabulary[word])
            book.vector.append(tf*idf)
        
        # normalized tf-idf vector for description
        book.vector = normalize(book.vector)
        
        # vector for genre
        for genre in all_genres:
            if genre in book.genres:
                tf = 1
            else:
                tf = 0
            idf = math.log10(M/all_genres[genre])
            book.genre_vector.append(tf*idf)
        
        # normalized tf-idf vector for genre
        book.genre_vector = normalize(book.genre_vector)
        res[book.url] = book

    file.close()

    # dump necessary files

    with open("matrix.pickle", "wb") as outfile:
        pickle.dump(res, outfile)
    
    with open("vocabulary.json", "w") as outfile:
        json.dump(vocabulary, outfile)
