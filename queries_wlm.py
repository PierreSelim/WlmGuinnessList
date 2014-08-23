# -*- coding: utf-8 -*-
#!/usr/bin/python

import json
import os
import MySQLdb
import time

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
    def __init__(self, words, country, outfile):
        self.outfile = outfile
        self.title = words[0].decode('utf-8')
        self.last_upload = WlmFile.__read_timestamp__(words[1])
        self.last_uploader = words[3].decode('utf-8')
        self.last_by_bot = str(words[4])
        if words[5] is not None:
            self.first_upload = WlmFile.__read_timestamp__(words[2])
            self.first_uploader = words[5].decode('utf-8')
            self.first_by_bot = str(words[6])
        else:
            self.first_upload = self.last_upload
            self.first_uploader = self.last_uploader
            self.first_by_bot = self.last_by_bot
        self.country = country

    def save(self):
        """ write to file. """ 
        self.outfile.write(self.title.encode('utf-8'))
        self.outfile.write(';;;')
        self.outfile.write(self.country)
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
class WlmContest:
    def __init__(self, country, cursor):
        """initialize a new contest with country name and db cursor."""
        self.country = country
        self.cursor = cursor

    def __get_contest_query__(self):
        country_sql = self.country.replace(' ', '_')
        return u"""SELECT /* SLOW_OK */ page.page_title AS title,
image.img_timestamp AS TIMESTAMP,
oldimage.oi_timestamp AS 'original_timestamp',
image.img_user_text AS 'last_uploader',
IF(ug_img.ug_group IS NULL, 0, 1) AS 'last_uploader_group_is_bot',
oldimage.oi_user_text AS 'first_uploader',
IF(ug_oi.ug_group IS NULL, 0, 1)  AS 'first_uploader_is_bot'
FROM image 
LEFT JOIN user_groups ug_img ON (ug_img.ug_user = image.img_user AND ug_img.ug_group = 'bot')
CROSS JOIN page ON image.img_name = page.page_title     
CROSS JOIN categorylinks ON page.page_id = categorylinks.cl_from    
LEFT JOIN oldimage ON image.img_name = oldimage.oi_name AND oldimage.oi_timestamp = (SELECT MIN(o.oi_timestamp) FROM oldimage o WHERE o.oi_name = image
.img_name)
LEFT JOIN user_groups ug_oi ON (ug_oi.ug_user = oldimage.oi_user AND ug_oi.ug_group = 'bot')
WHERE 
  categorylinks.cl_to = "Images_from_Wiki_Loves_Monuments_2013_in_%s"
ORDER BY img_timestamp ASC;""" % (country_sql)

    def get_files(self):
        """ Execute query on country contest category and store data in file. """
        self.cursor.execute(self.__get_contest_query__())
        result = self.cursor.fetchall()
        with open(self.country+'.txt', 'w') as outfile:
            for image in result:
                img = WlmFile(image, self.country, outfile)
                img.save()

def main():
    """ Main script for WLM file list. """
    sql = MySQLdb.connect(host="commonswiki.labsdb", db="commonswiki_p", read_default_file="~/replica.my.cnf", charset='utf8')
    cursor = sql.cursor()
    for country in countries:
        start_time = time.time()
        print "---- Fetching files for: %s" % country
        wlm = WlmContest(country, cursor)
        wlm.get_files()
        print "---- fetched in %03.3f seconds" % (time.time() - start_time)

if __name__== '__main__':
    main()