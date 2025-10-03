import requests
from bs4 import BeautifulSoup as BSoup
from flask import Flask, render_template
import datetime

url = "https://limitlesstcg.com"

class Deck:
    def __init__(self, rank, name, link, points, share_perc):
        self.rank = rank
        self.name = name
        self.link = link
        self.points = points
        self.share_perc = share_perc
    
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
    return decks

app = Flask(__name__)

decks = fetch_decks()
last_update = datetime.datetime.now()

@app.route('/')
def index():
    if(datetime.datetime.now() - last_update).total_seconds() > 3600:
        global decks, last_update
        decks = fetch_decks()
        last_update = datetime.datetime.now()
    return render_template('index.html', decks=decks, last_update=last_update)

if __name__ == '__main__':
    app.run(debug=True)