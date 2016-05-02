"""
This module queries the [API](http://ergast.com/mrd/)

"""

import urllib.request
import json

class DataManager:
    def getSeasonList(self):
        url = 'http://ergast.com/api/f1/seasons.json'
        with urllib.request.urlopen(url) as response:
            # html = response.read()
            encoding = response.info().get_content_charset('utf8')
            data = json.loads(response.read().decode(encoding))

        print(data['MRData'].keys())


DataManager().getSeasonList()