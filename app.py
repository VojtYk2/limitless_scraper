import requests
from bs4 import BeautifulSoup as BSoup
from flask import Flask, render_template
import datetime

url = "https://limitlesstcg.com"

class Decklist:
    def __init__(self, link, place):
        self.link = link
        self.place = place
    
    def __str__(self):
        return f"Place: {self.place}, Link: {self.link}"

class Deck:
    def __init__(self, rank, name, link, points, share_perc):
        self.rank = rank
        self.name = name
        self.link = link
        self.points = points
        self.share_perc = share_perc
        self.decklists = []

    def add_decklist(self, link, place):
        self.decklists.append(Decklist(link, place))
    
    def __str__(self):
        return f"Rank: {self.rank}, Name: {self.name}, Points: {self.points}, Share%: {self.share_perc}"

def fetch_decks():
    response = requests.get(url + "/decks")
    soup = BSoup(response.content, 'html.parser')
    table = soup.find('table', class_='data-table striped')
    decks_html = table.find_all('tr')[1:]
    decks = []
    for deck in decks_html:
        cols = deck.find_all('td')
        rank = cols[0].text.strip()
        name = cols[2].text.strip()
        link = cols[2].find('a')['href']
        points = cols[3].text.strip()
        share_perc = cols[4].text.strip()
        decks.append(Deck(rank, name, link, points, share_perc))
        response = requests.get(url + link)
        soup = BSoup(response.content, 'html.parser')
        table = soup.find('table', class_='data-table striped')
        decklists_html = table.find_all('tr')[2:]
        for decklist in decklists_html:
            cols = decklist.find_all('td')
            if(len(cols) == 5):
                place = cols[1].text.strip()
                if(cols[4].text.strip() != ""):
                    link = cols[4].find('a')['href']
                decks[-1].add_decklist(link, place)

    return decks

app = Flask(__name__)

decks = fetch_decks()
last_update = datetime.datetime.now()

@app.route('/')
def index():
    global decks, last_update
    if(datetime.datetime.now() - last_update).total_seconds() > 3600:
        decks = fetch_decks()
        last_update = datetime.datetime.now()
    return render_template('index.html', decks=decks, last_update=last_update)

if __name__ == '__main__':
    app.run(debug=True)