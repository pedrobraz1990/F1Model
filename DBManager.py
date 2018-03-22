import datetime as dt
import numpy as np
import pandas as pd
import pymysql
import time
import re

class DBManager():

    """
    This class interacts with the database image retrieved from ergast
    """

    # conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='Reag@123', db='mysql')
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='malinha', db='mysql')
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    #TODO a method that updates the MySQL DB

    def getDriversAges(self,row):
        """
        Retrieves a float with the drivers age difference at the time. The input should be a pandas row containing the columns
        `circuitId`, `driver1` and `driver2

        Returns True if success

        :return: float
        """

        query = """

            SELECT dob FROM F1.drivers
            WHERE driverId = {driverId!s}

        """.format(driverId=row["driver1"])

        df = pd.read_sql(query, self.conn)
        d1 = df.iloc[0].iloc[0]
        d1 = row["date"] - d1

        query = """

            SELECT dob FROM F1.drivers
            WHERE driverId = {driverId!s}

        """.format(driverId=row["driver2"])

        df = pd.read_sql(query, self.conn)
        d2 = df.iloc[0].iloc[0]
        d2 = row["date"] - d2

        return (d2 - d1).days / 365

    def getDriversFromRace(self, raceId):

        """
        Retrieves a pandas DataFrame with all Drivers Ids for a given race
        :return: pandas DF
        """

        query = """

            SELECT driverId FROM F1.races R

            INNER JOIN F1.results RE ON R.raceId = RE.raceId

            WHERE R.raceId = {raceId!s}

            ORDER BY driverId

        """.format(raceId=raceId)

        df = pd.read_sql(query, self.conn)

        return df

    def getQualifyingFromPandas(self, row):
        """
        Retrieves an integer with a qualifying position. The input should be a pandas row containing the columns
        `circuitId`, `driver1` and `driver2

        :return: integer
        """

        query = """

            SELECT position FROM F1.qualifying

            WHERE raceId = {raceId!s} AND driverId ={driverId!s}

        """.format(raceId=row["raceId"], driverId=row["driver1"])

        df = pd.read_sql(query, self.conn)
        d1 = int(df.loc[0])

        query = """

                    SELECT position FROM F1.qualifying

                    WHERE raceId = {raceId!s} AND driverId ={driverId!s}

                """.format(raceId=row["raceId"], driverId=row["driver2"])

        df = pd.read_sql(query, self.conn)
        d2 = int(df.loc[0])

        return d2 - d1

    def getRaces(self,):

        """
        Retrieves a pandas DataFrame with all races
        :return: pandas DF
        """

        query = """
            SELECT raceId, year, circuitId, name, date, round FROM F1.races ORDER BY date DESC

        """.format()

        df = pd.read_sql(query, self.conn)

        return df

    def getFirstYear_table(self):
        """
        Retrieves a pandas DataFrame with the first year of racing for each driver Id
        :return: pandas DF
        """

        query = """

            SELECT R.driverId, min(RA.year) firstYear FROM F1.results R

            INNER JOIN F1.races RA ON R.raceId = RA.raceId

            GROUP BY R.driverId

            ORDER BY R.driverId;

        """.format()

        df = pd.read_sql(query, self.conn)

        return df.set_index("driverId")

    def getResults_table(self):
        """
        Retrieves a pandas DataFrame with all results indexed by raceId-driver
        :return: pandas DF
        """

        query = """

            SELECT * FROM F1.results;

        """.format()

        df = pd.read_sql(query, self.conn)
        df = df.set_index(["raceId","driverId"])

        return df.sort_index()

    def getQualifying_table(self):
        """
        Retrieves a pandas DataFrame with all results indexed by raceId-driver.
        Also creates a column `qualiTime` with the driver' best qualifying lap time
        :return: pandas DF
        """

        query = """

            SELECT * FROM F1.qualifying

        """.format()

        df = pd.read_sql(query, self.conn)
        df.replace("None",np.nan,inplace=True)

        df["q1"] = df["q1"].apply(self.adjust_second_colon)
        df["q2"] = df["q2"].apply(self.adjust_second_colon)
        df["q3"] = df["q3"].apply(self.adjust_second_colon)

        df["q1"] = df["q1"].apply(self.createTimeDelta)
        df["q2"] = df["q2"].apply(self.createTimeDelta)
        df["q3"] = df["q3"].apply(self.createTimeDelta)

        df["qualiTime"] = df[["q1", "q2", "q3", ]].min(axis=1) #.apply(dt.timedelta.total_seconds)

        df = df.set_index(["raceId","driverId"])

        return df.sort_index()

    def getDrivers_table(self):
        """
        Retrieves a pandas DataFrame with all driver info
        :return: pandas DF
        """

        query = """

            SELECT * FROM F1.drivers

        """.format()

        df = pd.read_sql(query, self.conn)

        df.dob = pd.to_datetime(df.dob)

        return df.set_index("driverId")


    def getStandings_table(self):
        """
        Retrieves a pandas DataFrame with all standings info
        :return: pandas DF
        """

        query = """

            SELECT * FROM F1.driverStandings;

        """.format()

        df = pd.read_sql(query, self.conn)

        df.set_index(["raceId","driverId"],inplace=True)


        return df.sort_index()

    def adjust_second_colon(self,s):
        """
        Aux function to convert strings like "1:23:453" to "1:23.453". This was necessary because we found
        a few issues like this on the table `qualifying`
        :return: string
        """
        #     return re.sub('(:[^:]*),', r'\1. ', string)

        ret = None
        if s is not None and s is not '':
            # print(s)
            ret = re.sub(r'^((?:(?!\:).)*\:(?:(?!\:).)*)\:', r'\1.', s)
        return ret

    def createTimeDelta(self,stri):
        """
        Aux function to create a time delta from a string with the format MM:SS.mili
        Pandas can' do this

        :return: TimeDelta
        """
        ret = None
        if stri is not None and stri is not '':
            fmt = "%M:%S.%f"
            ret = dt.datetime.strptime(stri, fmt) - dt.datetime.strptime("00:00.000", fmt)
        return ret

    def total_seconds(self,td):
        """
        `TimeDelta`'s `total_seconds`method can't receive NaTType. This method can

        :param td: TimeDelta or NaT
        :return: float
        """
        ret = None

        if td is not None:
            ret = dt.timedelta.total_seconds(td)
        return ret

if __name__ == "__main__":
    rows = pd.read_pickle('test.pkl')
    rows["driverAge"] = rows.apply(DBManager().getDriversAges, axis=1)