# Available on GitHub!
# This program will gather data from raspberry pi sensors and store the data to make calculations later
# It must be compatible with raspbian and windows
# I would like to rely on as few modules as possible

import pandas as pd
import pathlib as pl
import datetime as dt
import logging

# Gotta learn logging

def main():

    gather_store_data()

    # while not determine_landed():
    # figure out how to keep only data from 3 seconds before launch
    # perhaps log data from when program starts and determine time of launch, then sort the big csv and remove data
    # from before the launch

    return None

def determine_launch():
    '''
    Will find the time of launch to be used in sorting data
    '''
    return None

def determine_landed():
    '''
    Will find the time of landing to be used in ending recording
    '''
    return None

def get_bta():
    '''
    This function will interact with the "--board--" and return the barometric pressure and temperature detected by the
    sensor. It will also return the current altitude calculated by its built in altitude function
    '''
    # b =  speak to "--device--" to get current data point
    # t =  speak to "--device--" to get current data point
    # a =  speak to "--device--" to get current data point

    # test
    b = pd.Series([], dtype = 'float64')
    t = pd.Series([], dtype = 'float64')
    a = pd.Series([], dtype = 'float64')
    for _ in range(10):
        b[_] = 2 * _
        t[_] = 2 * _
        a[_] = 2 * _
    return b, t, a

def get_accel():
    '''
        This function will interact with the "--board--" and return the accelerometer data detected by the
        sensor
    '''
    # x =  speak to "--device--" to get current data point
    # y =  speak to "--device--" to get current data point
    # z =  speak to "--device--" to get current data point

    # test
    x = pd.Series([], dtype = 'float64')
    y = pd.Series([], dtype = 'float64')
    z = pd.Series([], dtype = 'float64')
    for _ in range(10):
        x[_] = 2 * _
        y[_] = 2 * _
        z[_] = 2 * _
    return x, y, z

def get_gyro():
    '''
        This function will interact with the "--board--" and return the current gyro values detected by the sensor
    '''
    # x =  speak to "--device--" to get current data point
    # y =  speak to "--device--" to get current data point
    # z =  speak to "--device--" to get current data point

    # test
    x = pd.Series([], dtype = 'float64')
    y = pd.Series([], dtype = 'float64')
    z = pd.Series([], dtype = 'float64')
    for _ in range(10):
        x[_] = 2 * _
        y[_] = 2 * _
        z[_] = 2 * _
    return x, y, z

def mk_run_dir():
    '''
    This function will find the current path to the Flight-Recorder program and make a new directory named "Date-Run-#".
    It will also create all sub directories needed to store all flight data for further calculations
    if the same date and # exist it will add 1 to the greatest number file found
    '''

    file_num = 1

    while True:
        try:
            folder_name = f'{dt.date.today()}-Run-{file_num}'
            run_path = pl.Path.cwd() / folder_name
            run_path.mkdir(exist_ok = False)
            break
        except FileExistsError:
            file_num += 1
    print(f'Folder Created, {folder_name} @ {run_path}')
    return run_path

def gather_store_data():
    '''
    This function will gather the data and create a .csv file to save all the data into, each data type will have its own
    and column. Each consecutive data point will be stored in rows under their respective columns
    '''

    run_path = mk_run_dir()

    b, t, a = get_bta()
    a_x, a_y, a_z = get_accel()
    g_x, g_y, g_z = get_gyro()

    data_dict = {
            "Barometric Pressure":b,
            "Temperature":t,
            "Altitude_B":a,
            "Accelerometer_x":a_x,
            "Accelerometer_y":a_y,
            "Accelerometer_z":a_z,
            "Gyroscope_x":g_x,
            "Gyroscope_y":g_y,
            "Gyroscope_z":g_z,
        }
    data = pd.DataFrame.from_dict(data_dict)
    print(data)
    pd.DataFrame.to_csv(data,
                        path_or_buf = run_path / 'Run-Data',
                        mode = 'w'
                        )

    return None

# Optional things
# def get_gps, will determine devices location
# def determine_b_sea, will gather local barometric pressure at sea level from internet, will call get_gps

if __name__ == '__main__':
    main()