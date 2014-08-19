# -*- coding: utf-8 -*-
#!/usr/bin/python

import mw_api as Api
import json
import os

countries = [
"Algeria",     "China",        "Mexico",        "Taiwan",
"Andorra",     "Colombia",     "Nepal",         "Thailand",
"Antarctica",  "Egypt",        "Norway",        "the Czech Republic",
"Argentina",   "El Salvador",  "Panama",        "the Netherlands",
"Armenia",     "Estonia",      "Poland",        "the Philippines",
"Aruba",       "France",       "Romania",       "the United Kingdom",
"Austria",     "Germany",      "Russia",        "the United States",
"Azerbaijan",  "Hong Kong",    "Serbia",        "Tunisia",
"Belarus",     "Hungary",      "Slovakia",      "Ukraine",
"Belgium",     "India",        "South Africa",  "Uruguay",
"Bolivia",     "Israel",       "Spain",         "Venezuela",
"Cameroon",    "Italy",        "Sweden",
"Canada",      "Jordan",       "Switzerland",
"Chile",       "Luxembourg",   "Syria",
]

import datetime

class WlmFile:
    def __init__(self, words, country_per_image, outfile):
        self.outfile = outfile
        self.title = words[0].decode('utf-8')
        self.last_upload = WlmFile.__read_timestamp__(words[1])
        self.last_uploader = words[3].decode('utf-8')
        self.last_by_bot = words[4]
        self.country_per_image = country_per_image
        try:
            self.first_upload = WlmFile.__read_timestamp__(words[2])
            self.first_uploader = words[5].decode('utf-8')
            self.first_by_bot = words[6]
        except ValueError:
            self.first_upload = self.last_upload
            self.first_uploader = self.last_uploader
            self.first_by_bot = self.last_by_bot
        self.country_category = None
        self.__init_wlm_country_category__()

    def __init_wlm_country_category__(self):
        try:
            self.country_category = self.country_per_image[self.title]
            del self.country_per_image[self.title]
        except KeyError:
            self.country_category = u""

    def save(self):
        """ write to file. """ 
        self.outfile.write(self.title.encode('utf-8'))
        self.outfile.write(';;;')
        self.outfile.write(self.country_category)
        self.outfile.write(';;;')
        self.outfile.write(self.first_upload.isoformat())
        self.outfile.write(';;;')
        self.outfile.write(self.first_uploader.encode('utf-8'))
        self.outfile.write(';;;')
        self.outfile.write(self.first_by_bot)
        self.outfile.write(';;;')
        self.outfile.write(self.last_upload.isoformat())
        self.outfile.write(';;;')
        self.outfile.write(self.last_uploader.encode('utf-8'))
        self.outfile.write(';;;')
        self.outfile.write(self.last_by_bot)
        self.outfile.write('\n')
        
    @classmethod
    def __read_timestamp__(cls, timestamp):
        """ reading timestamp """
        return datetime.datetime(
            int(timestamp[0:4]),   # year
            int(timestamp[4:6]),   # month
            int(timestamp[6:8]),   # day
            int(timestamp[8:10]),  # hour
            int(timestamp[10:12]), # minute
            int(timestamp[12:14])  # second
            )


def fetch_files_from_country(site, country_category):
    """ fetch files from a the country_category by querying the mediawiki API.

    Args:
        site (Api.MwWiki):
        country_category (str):
    """
    country = country_category.replace("Category:Images from Wiki Loves Monuments 2013 in ", "")
    output = os.path.join('countries', country+'.txt')
    print "--- %s ---" % country_category
    query = Api.MwApiQuery(
        properties={
            "list" : "categorymembers",
            "cmtitle": country_category,
            "cmprop" : "ids|title|timestamp",
            "cmtype" : "file",
            "cmsort" : "timestamp",
            "cmdir" : "asc",
            "cmlimit": "max"
            })
    res = site.process_query(query, result=[])
    with open(output, 'w+', 0) as f:
        for image in res:
            f.write(image['title'].encode('utf-8')+'\n')

def all_countries_from_json(countries_json="categories.json"):
    """ Retrieves all files per countries and write them to 
    countries/country.txt

    Args:
        countries_json (str): query result with the list of categories of 
            Wiki Loves Monuments (optional by default)
    """
    with open(countries_json, 'r') as categories_file:
        commons = Api.MwWiki(url_api='https://commons.wikimedia.org/w/api.php')
        categories_query = json.loads(categories_file.read())
        category_list = [category['title'] for category in categories_query['query']['categorymembers']]
        for country_category in category_list:
            fetch_files_from_country(commons, country_category)

def country_per_files(country_list = countries):
    """"""
    result = dict()
    for country in country_list:
        with open(os.path.join('countries', country+'.txt'), 'r') as f:
            for image in f:
                name = image[5:].replace(' ', '_').replace('\n','').decode('utf-8')
                result[name] = country
    return result

def associate_wlm_image_info_to_country():
    # reading the query result list
    img_list = []
    with open('wlm2013/wlm2013.txt', 'r') as f:
        for line in f:
            img_list.append(line.split('\t'))
    with open('wlm2013/file_list.txt', 'w+') as f:
        for image in img_list:
            if 'TIMESTAMP' not in image:
                try:
                    wlmfile = WlmFile(image, country_per_files(), f)
                    wlmfile.save()
                except:
                    print "Did not work on %s" % image[0].decode('utf-8')

def main():
    """ Main script for WLM file list. """
    #import ArgumentParser from argparse
    associate_wlm_image_info_to_country()

if __name__== '__main__':
    main()