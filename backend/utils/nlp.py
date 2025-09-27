from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def preprocessText(text):
    tokens = word_tokenize(text.lower())
    
    stopWords = set(stopwords.words('portuguese'))
    filteredTokens = [word for word in tokens if word.isalpha() and word not in stopWords]

    return " ".join(filteredTokens)