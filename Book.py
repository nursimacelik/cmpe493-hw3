import string

class Book:
    def __init__(self, url, title, authors, description, recommended_books, genres):
        self.url = url
        self.title = title
        self.authors = ", ".join(authors)
        self.description = description
        self.recommended_books = recommended_books
        self.genres = genres[0].replace("\"", "").split(",")

        self.tokens = self.preproces(self.description)
        self.vector = []
        self.genre_vector = []

    def preproces(self, text):

        # read stopWords
        stopWords = open("stopwords.txt").read().split()
        result = ""
        text = text.lower()
        text = text.replace("br", "")
        
        for ch in text:
            if(ch in string.punctuation):
                result += " "
            else:
                result += ch

        result2 = []
        for word in result.split():
            if word not in stopWords:
                result2.append(word)
                
        return result2


    def remove_punc(self, text):
        result = ""
        for ch in text:
            if ch!="\"":
                result += ch
        return result

    def __str__(self):
        return '{self.title} by {self.authors}'.format(self=self)

    #def extract_title(self):
