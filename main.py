#set up
import requests
from bs4 import BeautifulSoup
import pandas as pd

class rottenTomatoesScraper():
    def __init__(self, name):
        self.name = name

    def parse_rotten_tomatoes(self, page_link: str):
        response = requests.get(page_link)
        if response.status_code != 200:
            return f"Request failed. Status: {response.status_code}"
        else:
            # create soup
            html = response.content
            soup = BeautifulSoup(html, 'lxml')
            # get movies tags
            divs = soup.find_all("div", {"class": "col-sm-18 col-full-xs countdown-item-content"})
            headings = [div.find("h2") for div in divs]

            # getting movie data: names, year, scores, consensus, directors, cast, adjusted scores, synopsis
            names = [heading.find('a').string for heading in headings]

            years = [heading.find("span", class_='start-year').string for heading in headings]
            years = [year.strip('()') for year in years]
            years = [int(year) for year in years]

            scores = [heading.find("span", class_='tMeterScore').string for heading in headings]
            scores = [s.strip('%') for s in scores]
            scores = [int(s) for s in scores]

            consensus = [div.find("div", {"class": "info critics-consensus"}) for div in divs]
            consensus = [con.contents[1].strip() for con in consensus]

            directors = [div.find("div", class_='director') for div in divs]
            directors = [
                None if director.find("a") is None else director.find("a").string for director in directors
            ]
            cast_info = [div.find("div", class_='cast') for div in divs]
            cast = [", ".join([link.string for link in c.find_all("a")]) for c in cast_info]

            adj_scores = [div.find("div", {"class": "info countdown-adjusted-score"}) for div in divs]
            adj_scores_clean = [score.contents[1].strip('% ') for score in adj_scores]
            adj_scores = [float(score) for score in adj_scores_clean]

            synopsis = [div.find('div', class_='synopsis') for div in divs]
            synopsis = [syn.contents[1] for syn in synopsis]

            # to dataframe
            # Organize data
            movies = pd.DataFrame({
                "title": names,
                "year": years,
                "score": scores,
                "adjusted_score": adj_scores,
                "director": directors,
                "synopsis": synopsis,
                "cast": cast,
                "consensus": consensus
            })
            movies.to_excel("movies_info.xlsx")
            return movies

base_site = "https://editorial.rottentomatoes.com/guide/100-best-classic-movies/2/"
a = rottenTomatoesScraper("new_parser")
a.parse_rotten_tomatoes(base_site)

