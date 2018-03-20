"""
This module queries the [API](http://ergast.com/mrd/)


.. note:: Some of the functions can be tweaked to query the API for selections.
"""

import urllib.request
import json

class ApiManager:

    def getSeasonList(self):
        """
        This function fetches all the F1 seasons available.

        :return: A list of dictionaries with the keys ``url`` and ``season``. The former contains the wikipedia link for that season and the latter contains a string with the reference year.
        """
        url = 'http://ergast.com/api/f1/seasons.json'
        with urllib.request.urlopen(url) as response:
            encoding = response.info().get_content_charset('utf8')
            data = json.loads(response.read().decode(encoding))

        final = data['MRData']['SeasonTable']['Seasons']
        return final

    def getRaceSchedule(self,referenceYear):
        """
        This function fetches all races for a given season.

        The returning dictionaries contain the following keys and values:

        * ``season`: String containing the reference year
        * `round``: String with int number
        * ``url``: Wikipedia link
        * ``raceName``: string
        * ``Circuit`: Another dictionary with the keys ``cirtcuitId``, ``url``, ``circuitName``, ``Location``(lat,long,locality,country)
        * ``date``
        * ``time``

        :param referenceYear: 4 digit string or number corresponding to a year
        :return: A list of dictionaries.
        """
        url = 'http://ergast.com/api/f1/{raceYear!s}.json'.format(raceYear=referenceYear)
        # print(url)
        with urllib.request.urlopen(url) as response:
            encoding = response.info().get_content_charset('utf8')
            data = json.loads(response.read().decode(encoding))
        final = data['MRData']['RaceTable']['Races']
        print(final)
        return final

    def getRaceResults(self, referenceYear, round):
        """
        This function fetches the results for a given race

        The resulting object will be a list. Each element of that list is a dictionary that contains a mixed of values and dictionaries.

        The upper dictionary has the keys:

        * ``FastestLap``
        * ``laps``
        * ``position``
        * ``Driver``
        * ``status``
        * ``grid``
        * ``positionText``
        * ``Time``
        * ``number``
        * ``Constructor``
        * ``points``

        The two dictionaries in that listed are detailed below.

        ``Driver``:

        * ``driverId``
        * ``permanentNumber``
        * ``code``
        * ``givenName``
        * ``familyName``
        * ``dateOfBirth``
        * ``nationality``

        ``Constructor``

        * ``constructorId``
        * ``url``: Wikipedia link
        * ``name``
        * ``nationality``

        ``Time``:

        * ``millis``: Time in milisseconds
        * ``time``: Timestamp like string


        ``FastestLap``:

        * ``rank``
        * ``lap``
        * ``Time``: ``time``
        * ``AverageSpeed``:  ``units`` : kph, ``speed`` : float like string


        :param referenceYear: 4 digit string or number corresponding to a year
        :param round: digit string or number corresponding to a round
        :return: A list of dictionaries of dictionaries.
        """
        url = 'http://ergast.com/api/f1/{raceYear!s}/{round!s}/results.json'.format(raceYear=referenceYear,round=round)
        # print(url)
        with urllib.request.urlopen(url) as response:
            encoding = response.info().get_content_charset('utf8')
            data = json.loads(response.read().decode(encoding))

        final = data['MRData']['RaceTable']['Races'][0]['Results']
        print(final[0].keys())
        return final

    def getQualifyingResults(self, referenceYear, round):
        """
        This function fetches all races for a given race. It is only available since 2003 though.

        The returning dictionaries contain the following keys and values:

        * ``Q1`: Timestamp like string
        * `Q2``: Timestamp like string
        * ``Q3``: Timestamp like string
        * ``Constructor``: For Constructor info refer to
        * ``Driver`:  For Driver info refer to
        * ``number``
        * ``position``

        :param referenceYear: 4 digit string or number corresponding to a year
        :param round: digit string or number corresponding to a round
        :return: A list of dictionaries.
        """
        url = 'http://ergast.com/api/f1/{raceYear!s}/{round!s}/qualifying.json'.format(raceYear=referenceYear, round=round)
        # print(url)
        with urllib.request.urlopen(url) as response:
            encoding = response.info().get_content_charset('utf8')
            data = json.loads(response.read().decode(encoding))
        final = data['MRData']['RaceTable']['Races'][0]['QualifyingResults']
        print(final)
        return final

    def getStandings(self, referenceYear, round):
        """
        This function fetches the driver' standings after a specific race.

        The returning dictionaries contain the following keys and values:

        * ``wins`
        * `Driver``
        * ``points``
        * ``position``
        * ``Constructors`
        * ``positionText``:`Retrieves a integer, or ``D`` for disqualified or ``E`` for excluded.
        * ``position``

        :param referenceYear: 4 digit string or number corresponding to a year
        :param round: digit string or number corresponding to a round
        :return: A list of dictionaries.
        """
        url = 'http://ergast.com/api/f1/{raceYear!s}/{round!s}/driverStandings.json'.format(raceYear=referenceYear,
                                                                                       round=round)
        # print(url)
        with urllib.request.urlopen(url) as response:
            encoding = response.info().get_content_charset('utf8')
            data = json.loads(response.read().decode(encoding))
        final = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        print(final[0].keys())
        return final

    def getAllDrivers(self):
        """
        This function fetches all drivers' info.

        The returning dictionaries contain the following keys and values:

        * ``url`: Wikipedia link
        * `givenName``
        * ``familyName``
        * ``dateOfBirth``
        * ``nationality`
        * ``driverId``

        :return: A list of dictionaries.
        """
        url = 'http://ergast.com/api/f1/drivers.json'
        # print(url)
        with urllib.request.urlopen(url) as response:
            encoding = response.info().get_content_charset('utf8')
            # print(response.read().decode(encoding))
            data = json.loads(response.read().decode(encoding))
        final = data['MRData']['DriverTable']['Drivers']
        print(final[0].keys())
        return final

    def getAllConstructors(self):
        """
        This function fetches all constructors' info.

        The returning dictionaries contain the following keys and values:

        * ``url`: Wikipedia link
        * ``name``
        * ``nationality``
        * ``constructorId``

        :return: A list of dictionaries.
        """
        url = 'http://ergast.com/api/f1/constructors.json'
        # print(url)
        with urllib.request.urlopen(url) as response:
            encoding = response.info().get_content_charset('utf8')
            # print(response.read().decode(encoding))
            data = json.loads(response.read().decode(encoding))
        final = data['MRData']['ConstructorTable']['Constructors']
        print(final[0].keys())
        return final

    def getAllCircuits(self):
        """
        This function fetches all circuits' info.

        The returning dictionaries contain the following keys and values:

        * ``url`: Wikipedia link
        * ``circuitName``
        * ``Location``
        * ``circuitId``

        :return: A list of dictionaries.
        """
        url = 'http://ergast.com/api/f1/circuits.json'
        # print(url)
        with urllib.request.urlopen(url) as response:
            encoding = response.info().get_content_charset('utf8')
            # print(response.read().decode(encoding))
            data = json.loads(response.read().decode(encoding))
        final = data['MRData']['CircuitTable']['Circuits']
        print(final[0].keys())
        return final

    def getAllResults(self):
        """
        This function fetches all the F1 results available. Each line is a car with its corresponding standing and all.

        :return: A list of dictionaries with the keys ``url`` and ``season``. The former contains the wikipedia link for that season and the latter contains a string with the reference year.
        """
        url = 'http://ergast.com/api/f1/results.json'
        with urllib.request.urlopen(url) as response:
            encoding = response.info().get_content_charset('utf8')
            data = json.loads(response.read().decode(encoding))

        final = data['MRData']['SeasonTable']['Seasons']
        return final

# ApiManager().getSeasonList()
# ApiManager().getRaceSchedule(2012)
# ApiManager().getRaceResults(2008,5)
# ApiManager().getQualifyingResults(2008,5)
# ApiManager().getStandings(2008,5)
# ApiManager().getAllDrivers()
# ApiManager().getAllConstructors()
ApiManager().getAllCircuits()