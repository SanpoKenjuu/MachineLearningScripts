# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import peakutils
from sklearn import linear_model
import numpy as np
import json
from . import SelectCSVDataFromDB

def parse_data_into_dataframe(filepath = None,url = None,jsonstr = None):
    """Depending on type of date, 
    parse to a pandas dataframe
    """
    if filepath is not None:
        dataFrame = pd.read_csv(filepath)
    if url is not None:
        dataFrame = pd.read_csv(url)
    if jsonstr is not None:
        dataFrame = pd.read_json(jsonstr)
    print ("type is " + str(type(dataFrame)))
        
    return dataFrame

def process_data_frame(dataFrame):
    """Remove redundant data and process data.
    This method is not generic, we will need to clean it up later.
    """
    #dataFrame = dataFrame.drop('DATE_FOR_TIME', 1)
    dataFrame['DATE_TIME'] = pd.to_datetime(dataFrame['DATE']+" "+dataFrame['TIME'],format='%d-%b-%y %I.%M.%S %p')
    #dataFrame = dataFrame.drop('TIME', 1)
    dataFrame.sort_values(['DATE_TIME'], ascending=[True], inplace=True)
    returningDataFrame = dataFrame
    print("In process_data_frame,before returning dataframe")
    print(returningDataFrame['DATE_TIME'])
    return returningDataFrame
        
        
def group_data_by_category(dataFrame,typesOfLicense=['Base','Plus','Apex']):
    """returns List of dataframes by category of license
    """
    listOfLicenseGroups = []
    LicenseTypeGroups = dataFrame.groupby('LIC_TYPE')
    for typeofLicense in typesOfLicense:
        licenseGroup = LicenseTypeGroups.get_group(typeofLicense)
        listOfLicenseGroups.append(licenseGroup)
    
    return listOfLicenseGroups

def save_plot_for_license_type(license_group,file_name):
    ax = license_group.plot(x='DATE_TIME',y='MAX_COUNT')
    fig = ax.get_figure()
    fig.savefig('plots/'+file_name)
    
def transform_to_uniform_index_column(license_group,column_name):
    return pd.DataFrame({'index': range(len(license_group.index)),
                   'values': license_group[column_name]}).set_index('index')['values']
    
def get_peak_index(column):
    return peakutils.indexes(column, thres=0.4, min_dist=2)

def save_peak_plot_for_license_type(license_group,file_name):
    col1 = transform_to_uniform_index_column(license_group,'DATE_TIME')
    col2 = transform_to_uniform_index_column(license_group,'MAX_COUNT')
    index = get_peak_index(col2)
    fig, ax = plt.subplots( nrows=1, ncols=1 )
    plt.plot(col1,col2, lw=0.4, alpha=0.4 )
    plt.plot(col1[index],col2[index], marker="o", ls="", ms=3 )
    plt.plot(col1[index],col2[index], marker="o", ms=3 )
    fig.savefig('plots/'+file_name)
    
def apply_ransac_linear_regression_on_group(license_group,no_of_days):
    col1 = transform_to_uniform_index_column(license_group,'DATE_TIME')
    col2 = transform_to_uniform_index_column(license_group,'MAX_COUNT')
    index = get_peak_index(col2)

    X = np.reshape(col1[index],(-1,1))
    Y = np.reshape(col2[index],(-1,1))

    list_x = []
    for x_value in col1[index].tolist():
        list_x.append((str(x_value.date())).replace('-',''))

    list_y = []
    for y_value in col2[index].tolist():
        list_y.append(y_value)

    daysDiff = []
    for x in X:
        x = x-X[0]
        days = x.astype('timedelta64[D]')
        actual = days / np.timedelta64(1, 'D')
        daysDiff.append(actual)
    X = np.asarray(daysDiff)
    X = X.astype(int)
    
    model_ransac = linear_model.RANSACRegressor(linear_model.LinearRegression())
    print ("X and Y Length" + str(len(X)) +" , " +str(len(Y)))
    model_ransac.fit(X,Y)
    inlier_mask = model_ransac.inlier_mask_
    outlier_mask = np.logical_not(inlier_mask)
    
    line_X = np.arange(0, no_of_days)
    line_y_ransac = model_ransac.predict(line_X[:, np.newaxis])

    list_line_y_ransac = line_y_ransac.tolist()
    newList = []
    for list_line_y_ransac_value in list_line_y_ransac:
        newList.append(str(list_line_y_ransac_value[0]))

    line_X_Date = []
    date_range_for_predict = pd.date_range(str(np.asarray(license_group.head(1)['DATE_TIME']))[2:12], periods=200).tolist()
    for date_value in date_range_for_predict:
        line_X_Date.append(str(date_value.date()).replace('-',''))
    
    fig, ax = plt.subplots( nrows=1, ncols=1 )
    plt.scatter(X[inlier_mask], Y[inlier_mask], color='yellowgreen', marker='.'
                ,label='Inliers')
    plt.scatter(X[outlier_mask], Y[outlier_mask], color='gold', marker='.',
                label='Outliers')
    plt.plot(line_X, line_y_ransac, color='cornflowerblue', linestyle='-',
         linewidth=2, label='RANSAC regressor')
    plt.legend(loc='lower right')

    result = []
    coord = {}
    counter = 0
    for item in line_X_Date:
        coord = {}
        coord["date"] = line_X_Date[counter]    
        coord["max_count"] = newList[counter]
        counter = counter + 1
        result.append(coord)

    peakList = []
    peak = {}
    count = 0
    for item1 in list_x:
        peak = {}
        peak["date"] = list_x[count]
        peak["max_count"] = list_y[count]
        count = count + 1
        peakList.append(peak)
    
    main_list = {}
    main_list["predict"] = result
    main_list["max_count"] = peakList
    print ("Test")
    print (main_list)
    return main_list
    

def main(data, license_type):
    print("Main works")
    
    #license_data = parse_data_into_dataframe(filepath='FremontBridge.csv')
    
    #print(license_data)
    #licenseJsonString = SelectCSVDataFromDB.select_csv_data_from_db()
    #print(licenseJsonString)
    #print(type(licenseJsonString))
    #licenseDataFrame = parse_data_into_dataframe(filepath = 'LicenseCount.csv')
    #licenseDataFrame = parse_data_into_dataframe(jsonstr = str(data))
    #print(licenseDataFrame.head())
    #licenseDataFrameProcess = process_data_frame(licenseDataFrame)
    #print(licenseDataFrameProcess['DATE_FOR_TIME'])
    #licenseGroup = group_data_by_category(licenseDataFrameProcess,[license_type])
    #print(listOfLicenseGroups)
    #result = []
    #result.append(apply_ransac_linear_regression_on_group(licenseGroup,200,ransacPlotName))
    #count = 0
    #for licenseGroup in listOfLicenseGroups:
        #count+=1
        #fileName = 'Plot'+str(count)
        #peakFileName = 'PeakPlot'+str(count)
        #ransacPlotName = 'RansacPlot'+str(count)
        #save_plot_for_license_type(licenseGroup,fileName)
        #save_peak_plot_for_license_type(licenseGroup,peakFileName)
        #result.append(apply_ransac_linear_regression_on_group(licenseGroup,200,ransacPlotName))
    # my code here
    #icenseJsonString = SelectCSVDataFromDB.select_date_count_from_db('ISE','Base','CiscoAlpha')
    data = json.loads(data)
    license_group = pd.DataFrame(data)
    print(license_group.head())
    license_group['DATE_TIME'] = pd.to_datetime(license_group['date'],format='%Y%m%d')
    license_group['MAX_COUNT'] = pd.to_numeric(license_group['max_count'], errors='coerce')
    license_group.sort_values(['DATE_TIME'], ascending=[True], inplace=True)
    print ("sorted Lic Group")
    print(license_group.head())
    result = apply_ransac_linear_regression_on_group(license_group,200)
    print ("X and Y coordinates")
    print (result)
    return result
