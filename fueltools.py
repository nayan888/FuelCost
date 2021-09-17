import os
from datetime import datetime
import pandas as pd
from dateutil import relativedelta
import datetime as dt

def getYears():

    dateDict= {}
    directory = 'data'
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        fname, file_extension = os.path.splitext(f)
        if os.path.isfile(f) and file_extension=='.pkl' and "Flights_" in filename:
            res =filename.replace("Flights_", "")
            res=res.replace(".csv.raw.pkl", "")
            splitDates=res.split("_")
            date_time_obj1 = datetime.strptime(splitDates[0], '%Y%m%d')
            year = date_time_obj1.year

            dateDict[year] = dateDict.get(year,0) +1

    res = [key for key, val in dateDict.items() if val>=3]


    return res

def getMonths(yearSelection=2018):

    dateDict= {}
    directory = 'data'
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        fname, file_extension = os.path.splitext(f)
        if os.path.isfile(f) and file_extension=='.pkl' and "Flights_" in filename:
            res =filename.replace("Flights_", "")
            res=res.replace(".csv.raw.pkl", "")
            splitDates=res.split("_")
            date_time_obj1 = datetime.strptime(splitDates[0], '%Y%m%d')
            year = date_time_obj1.year
            month = date_time_obj1.month
            if year==yearSelection:
                dateDict[month] = dateDict.get(month,0) +1

    res = [key for key, val in dateDict.items() if val>=1]


    return res


def getfilenamesForProcessing(directory):
    fileListGz=[]
    fileListPkl=[]
    for filename in os.listdir(directory):
        fname, extension = os.path.splitext(filename)
        if extension=='.pkl':
            fileListPkl.append(fname.replace(".raw",""))
        elif extension=='.gz':
            fileListGz.append(fname)
        else:
            None

    pkl = set(fileListPkl)
    gz= set(fileListGz)

    res=list(gz.difference(pkl))

    res[:] = [x+".gz" for x in res]

    return res


def loadPickle(year, month):

    yearsAvailable = getYears()
    if year not in yearsAvailable:
        raise ValueError('Year defined not in the list of available years')

    directory='data'
    flights_df_list=[]
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        fname, file_extension = os.path.splitext(f)
        if os.path.isfile(f) and file_extension=='.pkl' and "Flights_" in filename:
            res =filename.replace("Flights_", "")
            res=res.replace(".csv.raw.pkl", "")
            splitDates=res.split("_")
            date_time_obj1 = datetime.strptime(splitDates[0], '%Y%m%d')
            Fileyear = date_time_obj1.year
            Filemonth = date_time_obj1.month
            if Fileyear == year: # and Filemonth==month:
                temp_df = pd.read_pickle(f)
                flights_df_list.append(temp_df)

    flights_df = pd.concat(flights_df_list, ignore_index=True)
    return flights_df



# **************************************** #
# Constants for Fuel SAF Calculations
# all prices are in USD
# CostOfJetFuelPerKg = 0.61
# CostOfSafFuelPerKg = 3.66
# SafBlendingMandate = 0.02
# **************************************** #

def CalculateSAFCost(flights_df, costOfSafFuelPerKg = 3.66, safBlendingMandate = 0.02 ):

    flights_df['SAF_COST'] = flights_df['FUEL'] * safBlendingMandate * costOfSafFuelPerKg
    return flights_df

def CalculateFuelCost(flights_df, costOfJetFuelPerKg = 0.61, safBlendingMandate = 0.02 ):
    flights_df['FUEL_COST'] = flights_df['FUEL']*(1-safBlendingMandate) * costOfJetFuelPerKg
    return flights_df

def CalculateTotalFuelCost(flights_df):
    flights_df['TOTAL_FUEL_COST'] = flights_df['SAF_COST'] + flights_df['FUEL_COST']
    return flights_df


def getDFMonths(dtSeries):
    return set(dtSeries.dt.month.unique())


def getDFRatio(dfMonthsSet):
    summerIATA = set([4, 5, 6, 7, 8, 9, 10])
    winterIATA = set([1, 2, 3, 11, 12])

    reSum = summerIATA - dfMonthsSet
    reWin = winterIATA - dfMonthsSet

    sumMultiplier = len(summerIATA) - len(reSum)
    winMultiplier = len(winterIATA) - len(reWin)

    return sumMultiplier, winMultiplier


def getIATASeasons(setyear):
    startSummer = datetime(setyear, 3, 1) + relativedelta.relativedelta(day=31, weekday=relativedelta.SU(-1))

    endSummer = datetime(2018, 10, 1) + relativedelta.relativedelta(day=31, hours=24,
                                                                    weekday=relativedelta.SA(-1)) + dt.timedelta(days=1)

    return startSummer, endSummer
