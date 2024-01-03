import nltk
from bs4 import BeautifulSoup
import requests
import re
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn
nltk.download('wordnet')
nltk.download('omw-1.4')
global text
global top_results
global score
global saved_query
score = 0


# Returns the top 10 terms
def returnTopResult():
    global top_results
    return top_results


# Returns the rating of the query/refined query
def returnScore():
    global score
    return score


# Gets the HTML information from Google API search engine
def search(query):
    global text
    global saved_query
    saved_query = query
    search = query.replace(' ', '+')
    results = 50
    url = (f"https://www.google.com/search?q={search}&num={results}")   # Google's format for their engine
    text = ""
    returned_text = ""
    requests_results = requests.get(url)
    soup_link = BeautifulSoup(requests_results.content, "html.parser")  # Parses through the HTML
    links = soup_link.find_all("a")
    n = 1

    for link in links:  # Finds all the links within the HTML
        link_href = link.get('href')
        if "url?q=" in link_href and not "webcache" in link_href:
            title = link.find_all('h3')
            if len(title) > 0:  # Adds them all into a string for the multiline textbox to display
                returned_text = returned_text + (str(n) + ". " + title[0].getText()) + "\n"
                returned_text = returned_text + (link.get('href').split("?q=")[1].split("&sa=U")[0]) + "\n"
                returned_text = returned_text + "------\n"
                n = n + 1
                text = text + title[0].getText() + " "

    return returned_text


# Calculating the number of times the words in the query appear in the web results
def ratingRefinement(tokens):
    global saved_query
    global score
    score = 0
    query_terms = saved_query.split(' ')
    for term in tokens:     # Adding score
        if term in query_terms:
            score += 1
    score = score / len(tokens)


# Creates the histogram and return the plot to the canvas
def plot():
    global text
    global top_results
    global score
    text = re.sub(r'[^a-zA-Z]', ' ', text)  # Discard any text that is not alphabetical
    text = text.lower() # Lower the text to remove capitalization
    text = text.replace('pdf', '')  # Discard pdf because it is not a word
    text_tokens = word_tokenize(text)
    tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
    ratingRefinement(tokens_without_sw)

    # Top 10 terms
    n = 10
    counts = dict(Counter(tokens_without_sw).most_common(n))    # Sort through the most common terms
    top_results = sorted(counts, key=lambda x: (-counts[x], x))     # Sorts the top results for the graph's labels
    counts = {val[0]: val[1] for val in sorted(counts.items(), key=lambda x: (-x[1], x[0]))}

    labels = top_results    # Labels the graph with terms
    values = counts.values()    # Labels the graph with values

    y_pos = np.arange(len(labels))
    # Create horizontal bars
    plt.barh(y_pos, values)
    # Create names on the x-axis
    plt.yticks(y_pos, labels)
    plt.gca().invert_yaxis()
    # Return graphic/plot
    return plt.gcf()
