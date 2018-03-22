t
import numpy as np
import pandas as pd
import math
import re

import urllib.request
import json

from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.utils import np_utils

from DBManager import *

import itertools


class F1NN:

    def __init__(self,useQualiData = True,
                 lowerLimit = 1980,
                 upperLimit = 2018,
                 sessionId = '',
                 calculateFeatures = True,
                 features_list = ['year']
                 ):

        self.useQualiData = True
        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit
        self.sessionId = sessionId
        self.features_list = features_list

        self.loadTables()
        self.prioriMissingTreatment()

        if calculateFeatures:
            self.calculateFeatures()

        self.dataset = pd.read_pickle('dataset_' + self.sessionId + '.pkl')

    def loadTables(self):
        races = DBManager().getRaces()
        races.set_index('raceId', inplace=True)
        self.races = races
        self.races.sort_index(inplace=True)

        # to find years in F1 we need a driverID-results-race year table
        first_year = DBManager().getFirstYear_table()
        self.first_year = first_year

        results_na = DBManager().getResults_table()
        self.results_na = results_na

        qualifying_na = DBManager().getQualifying_table()
        qualifying = qualifying_na.copy()
        self.qualifying_na = qualifying_na
        self.qualifying = qualifying

        drivers_table = DBManager().getDrivers_table()
        self.drivers_table = drivers_table

        standings_table = DBManager().getStandings_table()
        self.standings_table = standings_table


        # getting previous race Id
        self.races = self.races.reset_index().set_index(["year", "round"])
        self.races["prevRaceId"] = self.races["raceId"].shift(1)
        self.races = self.races.reset_index().set_index("raceId").sort_index()

    def prioriMissingTreatment(self):

        # For now we just use it to compute the binary variable of whoever won.
        # If we use positions for something later one idea is to u  se the last in the grid instead of a 1000
        self.results = self.results_na.copy().fillna(1000)


        # How to deal with the fact that during the first race there is no position ?
        # If we set it to zero perhaps it won't have an impact, since there will be no activation.
        # To do so, for every 1st round we will set prevRaceId to NaN and later on the POST missing value treatment the
        # NaNs will become zeroes
        self.races["prevRaceId"][self.races["round"] == 1] = np.nan



        # Missing Quali Times We need two treatments:
        # * When there is no quali data for the entire race we consider them all to be 0
        # * When there is no available quali data for a specifiwe will choose to set it to the worst quali time available
        worstLaps = self.qualifying.copy().groupby(level="raceId").max()["qualiTime"]
        missingWorstLaps = worstLaps[
            worstLaps.isnull()].index  # get the raceIds which have NULL worst laps, thus have no time recorded
        self.qualifying["qualiTime"].loc[missingWorstLaps, :] = dt.timedelta(minutes=0)
        missingIndex = qualifying[qualifying["qualiTime"].isnull()].index

        # getting only the ones we are interested in
        worstMissingLaps = worstLaps.loc[missingIndex.get_level_values(0)]
        worstMissingLaps.index = missingIndex

        # setting them to the data
        self.qualifying.loc[missingIndex, "qualiTime"] = worstMissingLaps

        self.qualifying["qualiTime"] = self.qualifying["qualiTime"].apply(DBManager().total_seconds)

    def cutSample(self):
        lowerLimit = self.lowerLimit
        if self.useQualiData:
            lowerLimit = 2003

        self.races.drop(self.races.index[races["year"] >= self.upperLimit], inplace=True)
        self.races.drop(self.races.index[self.races["year"] < lowerLimit], inplace=True)


    def feature_qualifying(self,raceId):
        idx = pd.IndexSlice

        if raceId in self.qualifying.index.get_level_values(
                0):  # Many missing qualifyings, check "missingQuali.sql MISSING TREATMENT
            self.rows["qualifying"] = self.qualifying.loc[idx[raceId, self.rows["driver2"].tolist()], :]["position"].reset_index(
                drop=True) - self.qualifying.loc[idx[raceId, self.rows["driver1"].tolist()], :]["position"].reset_index(
                drop=True)
        else:
            self.rows["qualifying"] = 0

    def feature_driverAge(self,raceId):
        

    def calculateFeatures(self):

        self.cutSample()


        data = []

        for raceId in self.races.index:

            drivers = DBManager().getDriversFromRace(raceId=raceId)
            self.rows = pd.DataFrame(list(itertools.combinations(drivers['driverId'], 2)), columns=["driver1", "driver2"])

            # NonFeatures
            self.rows["raceId"] = raceId
            self.rows["date"] = self.races.loc[raceId]["date"]
            self.rows["prevRaceId"] = self.races.loc[raceId]["prevRaceId"]

            # Features
            if "year" in self.features_list:
                self.rows["year"] = self.races.loc[raceId]["year"]

            if "qualifcircuitIdying" in self.features_list:
                self.rows["circuitId"] = self.races.loc[raceId]["circuitId"]

            if "qualifying" in self.features_list:
                self.feature_qualifying(raceId)

            if "driverAge" in self.features_list:
            self.rows["driverAge"] = (self.drivers_table.loc[self.rows["driver1"]]["dob"].reset_index(drop=True)).sub(
                self.drivers_table.loc[self.rows["driver2"]]["dob"].reset_index(drop=True)).dt.days / 365
            self.rows["yearsF1"] = - self.first_year.loc[self.rows["driver2"]].reset_index(drop=True) + self.first_year.loc[
                self.rows["driver1"]].reset_index(drop=True)

            #     Drivers Championship position in season
            #     For those whose prevRaceId is not NaN we have to fulfill it with a query
            if math.isnan(self.races.loc[raceId]["prevRaceId"]):
                self.rows["seasonStanding_d1"] = 0
                self.rows["seasonStanding_d2"] = 0
            else:
                #         print(races.loc[raceId]["prevRaceId"])
                self.rows.set_index(["raceId", "driver1"], inplace=True)
                self.rows["seasonStanding_d1"] = self.standings_table.loc[self.rows.index, :]["position"]
                self.rows.reset_index(inplace=True)
                self.rows.set_index(["raceId", "driver2"], inplace=True)
                self.rows["seasonStanding_d2"] = self.standings_table.loc[self.rows.index, :]["position"]
                self.rows.reset_index(inplace=True)
                self.rows["seasonStanding"] = self.rows["seasonStanding_d2"] - self.rows["seasonStanding_d1"]

            # Constructor
            self.rows.set_index(["raceId", "driver1"], inplace=True)
            self.rows["constructor_d1"] = self.results.loc[self.rows.index, :]["constructorId"]
            self.rows.reset_index(inplace=True)
            self.rows.set_index(["raceId", "driver2"], inplace=True)
            self.rows["constructor_d2"] = self.results.loc[self.rows.index, :]["constructorId"]
            self.rows.reset_index(inplace=True)

            # Pole Percentage time
            ind = pd.MultiIndex.from_arrays([pd.Series(raceId).repeat(self.rows["driver2"].shape[0]), self.rows["driver2"]])
            self.rows["qualifying_d2"] = self.qualifying.loc[ind]["qualiTime"].reset_index(drop=True)
            ind = pd.MultiIndex.from_arrays([pd.Series(raceId).repeat(self.rows["driver1"].shape[0]), self.rows["driver1"]])
            self.rows["qualifying_d1"] = self.qualifying.loc[ind]["qualiTime"].reset_index(drop=True)
            self.rows["polePercentage"] = (self.rows["qualifying_d2"] - self.rows["qualifying_d1"]) / self.qualifying.loc[raceId, :][
                "qualiTime"].min()

            # Races won in career
            # 1st cut "past" races
            date = self.races.loc[raceId]["date"]
            wins = self.results[self.results["date"] < date].groupby(level="driverId").sum()["victory"]
            self.rows["victory_d1"] = wins.loc[self.rows["driver1"]].reset_index(drop=True)
            self.rows["victory_d2"] = wins.loc[self.rows["driver2"]].reset_index(drop=True)
            self.rows["victory_in_career"] = (self.rows["victory_d2"] - self.rows["victory_d1"]).reset_index(drop=True)

            # True Values
            self.rows["output_1"] = self.rows.apply(lambda x: self.results.loc[x["raceId"], x["driver2"]]["position"].iloc[0] -
                                                    self.results.loc[x["raceId"], x["driver1"]]["position"].iloc[0], axis=1)
            self.rows["output"] = 0
            self.rows["output"][self.rows["output_1"] == 0] = 0.5  # Both retired
            self.rows["output"][self.rows["output_1"] > 0] = 1  # Driver 2 lost
            self.rows["output"][self.rows["output_1"] < 0] = 0  # Driver 2 won
            self.rows.drop("output_1", axis=1, inplace=True)

            data.append(self.rows)

        dataset = pd.concat(data)

        dataset.to_pickle('dataset_' + self.sessionId + '.pkl')