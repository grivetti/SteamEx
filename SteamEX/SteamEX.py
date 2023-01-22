import requests
from bs4 import BeautifulSoup
import csv


class ParseSteam:
    def parser_url(self, begin: int,end:int) -> str:
        for pagenum in range(begin,end+1):
            response = requests.get(f"https://store.steampowered.com/search/?category1=998%2C996&page={pagenum}")
            soup = BeautifulSoup(response.text, 'lxml')
            table = soup.find("div",attrs={"id":"search_resultsRows"})
            for game in table.find_all("a"):
                yield game["href"]
    
    def parser_game(self, url:str):
        d = {}
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            infodump = soup.find("div",attrs={"id":"genresAndManufacturer"}).text.split("\n")
            d[infodump[1].split(":")[0]] = infodump[1].split(":")[1]
            d[infodump[2].split(":")[0]] = infodump[2].split(":")[1].split(",")
            try:
                try:
                    d["Price"] = float(soup.find("div",attrs={"class":"game_purchase_price price"}).text.replace("R$","").replace(",","."))
                except ValueError:
                        d["Price"] = 0
            except AttributeError:
                try:
                    d["Price"] = float(soup.find("div",attrs={"class":"discount_final_price"}).text.replace("R$","").replace(",","."))
                except AttributeError:
                    d["Price"] = 0
            try:
                d[infodump[4].replace(":","")] = infodump[5].split(",")
            except IndexError:
                d[infodump[4].replace(":","")] = infodump[5]
            try:
                d[infodump[8].replace(":","")] = infodump[9].split(",")
            except IndexError:
                d[infodump[8].replace(":","")] = ""
            try:
                d["Review Count"] = int(soup.find("meta",attrs={"itemprop":"reviewCount"})["content"])
                d["Rating Value"] = int(soup.find("meta",attrs={"itemprop":"ratingValue"})["content"])
            except TypeError:
                d["Review Count"] = 0
                d["Rating Value"] = 0
        except AttributeError:
            pass
        return d
    def run(self, begin: int,end:int):
        lst = []
        for i in self.parser_url(begin,end):
            print(i)
            row = self.parser_game(i)
            if(row != {}):
                with open('Data/steam.csv', 'a+', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=row.keys())
                    writer.writerow(row)
