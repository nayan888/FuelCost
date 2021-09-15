import pandas as pd
import os
import fueltools as ft


def loadFile(filename):
    global header_list, airc_ls, flights_df
    print("Processing File:", filename)
    fname = filename
    loadrows = None

    header_list = ["ECTRL_ID", "ADEP", "ADEP_Latitude", "ADEP_Longitude", "ADES", "ADES_Latitude", "ADES_Longitude",
                   "FILED_OFF_BLOCK_TIME", "FILED_ARRIVAL_TIME",
                   "ACTUAL_OFF_BLOCK_TIME", "ACTUAL_ARRIVAL_TIME", "AC_Type", "AC_Operator", "AC_Registration",
                   "ICAO_Flight_Type", "STATFOR_Market_Segment", "Requested_FL", "Actual_Distance_Flown"]
    airc_ls = []
    df_chunk = pd.read_csv(fname,
                           parse_dates=['FILED_OFF_BLOCK_TIME', 'FILED_ARRIVAL_TIME', 'ACTUAL_OFF_BLOCK_TIME',
                                        'ACTUAL_ARRIVAL_TIME'], dayfirst=True, compression='gzip',
                           names=header_list, skiprows=1, chunksize=10000, nrows=loadrows,
                           dtype={'STATFOR_Market_Segment': 'category', 'AC_Type': 'category',
                                  'ICAO_Flight_Type': 'category', 'ADES': 'category', 'ADEP': 'category'})
    iC = 0
    for chunk in df_chunk:
        airc_ls.append(chunk)
        print("Chunk:", iC)
        print("Chunk:", chunk.shape)
        iC = iC + 1
    flights_df = pd.concat(airc_ls)
    print(filename, " contains: ", flights_df.shape)
    return flights_df

def preprocess(fnamelist):
    # Load acperf
    header_list = ["KEY","BK_AC_TYPE_ID","ICAO_TYPE_CODE","AC_CATEGORY","EQV_TYPE","EQV_NAME","ICAO_ENGINE_DESC","CO2_COEFF","MASS","BAND_FROM_NM","BAND_TO_NM","BAND_FLOOR_NM","FUEL_TOT","FUEL_TOT_MARG_RATE","CORR_FACTOR","CALC_RETURN_CODE","TINV","S","N","X_BAR","SXX","E","ERROR_TYPE","MASS_RATIO","ERROR_RATE_FUEL_PER_NM","AO_FUEL_VERSION_ID","CREA_DATE","CREA_NOTE","VALID_FROM","VALID_TO"]
    airc_ls = []
    acperf_df = pd.read_csv('data/acperfDB.csv' , names=header_list, skiprows=1)
    acperf_df = pd.read_excel('data/acperfDB.xlsx', names=header_list, skiprows=1)

    print("Ac Performance File contains: ", acperf_df.shape)


    directory = 'data'
    for filename in fnamelist:
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            filename, file_extension = os.path.splitext(f)
            if file_extension=='.gz':
                flights_df = loadFile(f)



                flights_df["AC_Type"] = flights_df["AC_Type"].astype(str)+'----'

                flights_df=flights_df.join(acperf_df.set_index('KEY'), on ='AC_Type', how='inner')

                print("Shape after join",flights_df.shape)



                flights_df['FUEL'] = ((flights_df['FUEL_TOT'] + (flights_df['Actual_Distance_Flown'] * flights_df['FUEL_TOT_MARG_RATE'])) * flights_df['CORR_FACTOR'] )
                flights_df['EMISSIONS'] = flights_df['CO2_COEFF'] * flights_df['FUEL']

                flights_df=flights_df.drop(["BK_AC_TYPE_ID","EQV_TYPE","EQV_NAME","ICAO_ENGINE_DESC","MASS","BAND_FROM_NM","BAND_TO_NM","BAND_FLOOR_NM","CALC_RETURN_CODE","TINV","S","N","X_BAR","SXX","E","ERROR_TYPE","MASS_RATIO","ERROR_RATE_FUEL_PER_NM","AO_FUEL_VERSION_ID","CREA_DATE","CREA_NOTE","VALID_FROM","VALID_TO"], axis=1)

                flights_df=CreateCategories(flights_df)

                flights_df.sort_values(by=['ECTRL_ID'], inplace=True)
                pklfilename = filename + '.raw.pkl'
                print('Saving to pickle CSV', pklfilename)
                flights_df.to_pickle(pklfilename)
                # csvfilename= filename + '.csv'
                # flights_df.to_csv(csvfilename)


def CreateCategories(flights_df):
    icaoPrefixCategories = pd.read_excel('data/ICAOPrefix.xlsx')
    flights_df['ADEP_PREFIX'] = flights_df['ADEP'].str[:2]
    flights_df['ADES_PREFIX'] = flights_df['ADES'].str[:2]

    # fix flights to/from US, CANADA and Australia
    flights_df.loc[flights_df['ADEP_PREFIX'].str[:1] == 'K', 'ADEP_PREFIX'] = 'K'
    flights_df.loc[flights_df['ADES_PREFIX'].str[:1] == 'K', 'ADES_PREFIX'] = 'K'
    flights_df.loc[flights_df['ADEP_PREFIX'].str[:1] == 'C', 'ADEP_PREFIX'] = 'C'
    flights_df.loc[flights_df['ADES_PREFIX'].str[:1] == 'C', 'ADES_PREFIX'] = 'C'
    flights_df.loc[flights_df['ADEP_PREFIX'].str[:1] == 'Y', 'ADEP_PREFIX'] = 'Y'
    flights_df.loc[flights_df['ADES_PREFIX'].str[:1] == 'Y', 'ADES_PREFIX'] = 'Y'

    # fix flights to/from China
    flights_df.loc[(flights_df['ADEP_PREFIX'].str[:1] == 'Z') & (flights_df['ADEP_PREFIX'] != 'ZK') & (
                flights_df['ADEP_PREFIX'] != 'ZM'), 'ADEP_PREFIX'] = 'Z'
    flights_df.loc[(flights_df['ADES_PREFIX'].str[:1] == 'Z') & (flights_df['ADES_PREFIX'] != 'ZK') & (
                flights_df['ADES_PREFIX'] != 'ZM'), 'ADES_PREFIX'] = 'Z'

    # fix flights to/from Russia
    flights_df.loc[(flights_df['ADEP_PREFIX'].str[:1] == 'U') & (
        ~flights_df['ADEP_PREFIX'].isin(["UA", "UB", "UC", "UD", "UG", "UK", "UM", "UT"])), "ADEP_PREFIX"] = 'U'
    flights_df.loc[(flights_df['ADES_PREFIX'].str[:1] == 'U') & (
        ~flights_df['ADES_PREFIX'].isin(["UA", "UB", "UC", "UD", "UG", "UK", "UM", "UT"])), "ADES_PREFIX"] = 'U'

    # fix flights to/from Outermost Regions
    flights_df.loc[(flights_df['ADEP'].isin(
        ['FMEE', 'FMEP', 'FMCZ', 'LPCR', 'LPFL', 'LPGR', 'LPHR', 'LPPD', 'LPLA', 'LPPI', 'LPAZ', 'LPSJ', 'LPMA',
         'LPPS'])), "ADEP_PREFIX"] = flights_df['ADEP']
    flights_df.loc[(flights_df['ADES'].isin(
        ['FMEE', 'FMEP', 'FMCZ', 'LPCR', 'LPFL', 'LPGR', 'LPHR', 'LPPD', 'LPLA', 'LPPI', 'LPAZ', 'LPSJ', 'LPMA',
         'LPPS'])), "ADES_PREFIX"] = flights_df['ADES']

    icaoPrefixCategories.columns = 'ADEP_' + icaoPrefixCategories.columns
    flights_df = flights_df.join(icaoPrefixCategories.set_index('ADEP_PREFIX'), on='ADEP_PREFIX', how='inner',
                                 rsuffix="ADEP")

    icaoPrefixCategories.columns = icaoPrefixCategories.columns.str.replace('ADEP_', "")
    icaoPrefixCategories.columns = 'ADES_' + icaoPrefixCategories.columns
    flights_df = flights_df.join(icaoPrefixCategories.set_index('ADES_PREFIX'), on='ADES_PREFIX', how='inner',
                                 rsuffix="ADES")
    return flights_df



# **************************************** #
# Constants for Fuel SAF Calculations
# all prices are in USD
CostOfJetFuelPerKg = 0.61
CostOfSafFuelPerKg = 3.66
SafBlendingMandate = 0.02
# **************************************** #



# *************************************************** #
# Constants for Fuel TAX Calculations
# all prices are in Euros/GJ
# 2023 = 0 Tax rate
# 2024 = 1.075    2025 = 2.15 etc

#Tax rate in 2033
MaxFuelTaxRateEurosPerGJ = 10.75
#Using rate for 2025 to match the SAF mandate
FuelTaxRateEurosPerGJ = 2.15

#Current Exchange rate from Euros to USD
EurosToUsdExchangeRate = 1.19

#Tax rate in Euros/kg
FuelTaxRateEurosPerKg = (46.4/1000) * FuelTaxRateEurosPerGJ
FuelTaxRateUsdPerKg = FuelTaxRateEurosPerKg * EurosToUsdExchangeRate
# *************************************************** #




