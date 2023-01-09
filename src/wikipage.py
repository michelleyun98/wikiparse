import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import unicodedata
from collections import Counter, defaultdict
import re
import datetime

class Page:
    
    def __init__(self, url):
        self.url = url
        self.soup = BeautifulSoup(urlopen(self.url), 'lxml') # soup object for html 
        self.match = re.search(r"(?<=wiki\/).*", self.url).group() # matches article title from url with regex
        self.url2 = f"https://en.wikipedia.org/w/index.php?title=" + self.match + "&action=info" # page metadata
        self.soup2 = BeautifulSoup(urlopen(self.url2), "lxml") # soup object for html
    
    def text(self):
        """
        Returns text content as string
        """
        self.text = []
        for node in self.soup.find_all("p"):
            if not node.has_attr("class"):
                self.text.append(unicodedata.normalize("NFKD", node.get_text()).strip())
        return self.text
        
    def textcitations(self):
        """
        Returns list of citations (publication company, author, year of publication...)
        """
        self.citations = []
        for node in self.soup.find_all("cite"):
            self.citations.append(unicodedata.normalize("NFKD", node.get_text()))
        return self.citations
    
    def sourcetypes(self):
        """
        Returns dictionary with type of course (e.g. "journal") as key & frequency of occurance in article
        """
        self.types = defaultdict(int)
        for node in self.soup.find_all("cite"):
            sourcetype = node["class"][1]
            if sourcetype == 'cs1':
                self.types[sourcetype] = "unknown"
            else:
                self.types[sourcetype] += 1
        return self.types
            
    def citerefs(self):
        """
        Returns list of citerefs; e.g. 'CITEREFSteelTorrie1960'
        """
        self.citerefs = []
        for node in self.soup.find_all("cite"):
            if node.has_attr("id"):
                self.citerefs.append(node["id"])
        return self.citerefs
    
    # def citeyears(self):
    #     self.citeyears = defaultdict(int)
    #     for ref in self.citerefs():
    #         year = ref[-4:]
    #         self.citeyears[year] += 1
    #     return self.citeyears
      
    def get_num_edits(self):
        """
        Return total number of page edits
        """
        for node in self.soup2.find_all("tr", id="mw-pageinfo-edits"):
          for child in node.children:
              if child.get("style") == None:
                  return int(child.get_text().replace(",", ""))
                
    def get_origin_year(self):
        """
        Returns origin year of article
        """
        for node in self.soup2.find_all("tr", id="mw-pageinfo-firsttime"):
            for child in node.children:
                if child.a:
                    self.origin_year = child.get_text()[-4:]
                    return int(self.origin_year)

    def get_edits_per_year(self):
        """
        Returns how many times on average an article is edited in a year
        """
        current_year = datetime.date.today().year
        self.age = current_year - self.get_origin_year()
        return round(self.get_num_edits()/self.age, 2)

    def is_living(self):
        """
        If article is bibilographical, checks living status of subject
        """
        if "Living" in self.soup.script.get_text():
            return True
        else:
            return False



      
      

      
      
       
      


    