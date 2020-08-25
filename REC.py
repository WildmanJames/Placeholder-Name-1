# This program will gather data from raspberry pi sensors and store the data for analysis later.
# I would like to rely on as few modules as possible.

# This program is intended for use with a raspberry 3 B+, BMP388 board, and ICM20629 board running with i2c.
# This is currently working with my testing methods, it could be improved however.

# While the Raspberry Pi is in a network it can be connected to over secure ssh, on PC, Linux, or Android (via Termius).
# It would be ideal to add a gps/cell board so a cell network can be used anywhere to connect to the pi.

# Some references--
# http://www.lunar.org/docs/LUNARclips/v5/v5n1/Accelerometers.html
# https://www.nxp.com/docs/en/application-note/AN3397.pdf

# Board is from Adafruit-Circuitpython and will work on a rasp pi, I cant find how to make it work for windows
# Without breaking everything.
import board
import busio
import adafruit_bmp3xx
import adafruit_icm20x
import time
import pandas as pd
import pathlib as pl
import datetime as dt
import logging

# Gotta learn logging and log stuff

# Connecting the breakout boards to the raspberry pi's i2c conncetion
i2c = busio.I2C(board.SCL, board.SDA)
bmp388 = adafruit_bmp3xx.BMP3XX_I2C(i2c)
icm20649 = adafruit_icm20x.ICM20649(i2c)

def main():
    """
    The main function will call all other functions and provide a text indication that the program has begun and ended.
    """

    print('Program start----------')

    g_max, g_min, a_cal = setup()

    determine_launch(g_max, g_min, a_cal)

    print('Program end----------')

    return None

def setup():
    """
    The setup function will reset, initialize, and calibrate all of the sensors to be used. This is done from rest
    (no movement on pad, nearly launch)
    """
    global bmp388
    global icm20649

    # Ask for pressure at sea level or use gps to find it, currently hard set to 1014.9 for testing

    bmp388.reset()
    bmp388.sea_level_pressure = 1014.9

    icm20649.reset()
    icm20649.initialize()
    print('Initializing, please wait...')
    # Allows time for sensors to "wake up"
    time.sleep(5)

    grav_vals = []
    for i in range(100):
        resultant = 0
        for j in range(3):
            resultant = resultant + (icm20649.acceleration[j] ** 2)
        resultant = resultant ** 0.5
        grav_vals.append(resultant)
    grav_vals.sort(reverse = True)
    avg_grav = (sum(grav_vals) / 100)
    max_grav = grav_vals[0]
    min_grav = grav_vals[len(grav_vals) - 1]

    a_cal = bmp388.altitude

    print('local difference from free fall acceleration at rest:')
    print(f'avg = {avg_grav}')
    print(f'max = {max_grav}')
    print(f'min = {min_grav}')

    return max_grav, min_grav, a_cal

def determine_launch(g_max, g_min, a_cal):
    """
    The determine launch function will do as it is named, and notify the user launch has been detected via text.

    Launch is determined by comparing the resultant acceleration determined by the board to the g_min and max values
    found by the setup function. Since we know that before launch V0 is zero, the only acceleration acting on the
    board must be the normal force acting on the board in the opposite direction of gravity. The board will trigger a
    launch message and proceed to collect data when the resultant is larger or smaller than a determined error
    (currently 0.5) from the g_max or min.
    """

    while True:
        resultant = 0
        for j in range(3):
            resultant = resultant + (icm20649.acceleration[j] ** 2)
        resultant = resultant ** 0.5

        if (resultant > (g_max + 0.5)) or (resultant < (g_min - 0.5)):
            print(f'***** Launch!!! *****')
            break

    gather_store_data(g_max, g_min, a_cal)

    return None

def get_data(g_max, g_min, a_cal):
    """
    The get data function will interact with bmp388 and return the barometric pressure and temperature detected by the
    sensor. It will also return the current altitude calculated by its built in altitude function.

    The get data function will also interact with icm20649 and return the accelerometer and gyro data detected by the
    sensor.
    """

    b = []
    t = []
    a = []
    a_x = []
    a_y = []
    a_z = []
    g_x = []
    g_y = []
    g_z = []

    # test
    test_start = time.time()
    landing_test = []
    lt_index = 0
    while True:
        a_x.append(icm20649.acceleration[0])
        a_y.append(icm20649.acceleration[1])
        a_z.append(icm20649.acceleration[2])
        g_x.append(icm20649.gyro[0])
        g_y.append(icm20649.gyro[1])
        g_z.append(icm20649.gyro[2])
        b.append(bmp388.pressure)
        t.append(bmp388.temperature)
        a.append(bmp388.altitude)

        # Testing for if the board has landed
        # This is done in a similar way to determine launch, however this is checking the data to be recorded.
        # For now, it will check the last 50 data points to see if they all are within the g_max or min within error
        # Once it is determined the board is no longer accelerating 49 of the last 50 data points are removed.
        # A second condition must also be met, where the altitude is within 2 meters of the ground.

        resultant = ((a_x[lt_index] ** 2) + (a_y[lt_index] ** 2) + (a_z[lt_index] ** 2)) ** 0.5
        landing_test.append(resultant)

        if all((i < (g_max + 0.5)) and (i > (g_min - 0.5)) for i in landing_test[-50:])\
                and ((a[lt_index] - a_cal) <= 2):
            if lt_index >= 10:
                break

        lt_index += 1

    a_x = a_x[:len(a_x) - 49]
    a_y = a_y[:len(a_y) - 49]
    a_z = a_z[:len(a_z) - 49]
    g_x = g_x[:len(g_x) - 49]
    g_y = g_y[:len(g_y) - 49]
    g_z = g_z[:len(g_z) - 49]
    b = b[:len(b) - 49]
    t = t[:len(t) - 49]
    a = a[:len(a) - 49]

    print('End test!')
    test_end = time.time()
    duration = test_end - test_start
    print(f'Testing took {duration} seconds to complete.')

    return b, t, a, a_x, a_y, a_z, g_x, g_y, g_z

    # end test

def mk_run_dir():
    """
    The make run directory function will find the current path to the Flight-Recorder program and make a new directory
    named "Date-Run-#". If the same date and # exist it will add 1 to the greatest number file found allowing for
    multiple runs.
    """

    file_num = 1

    while True:
        try:
            folder_name = f'{dt.date.today()}-Run-{file_num}'
            run_path = pl.Path.cwd() / folder_name
            run_path.mkdir(exist_ok = False)
            break
        except FileExistsError:
            file_num += 1
    # log print(f'Folder Created, {folder_name} @ {run_path}')
    return run_path

def gather_store_data(g_max, g_min, a_cal):
    """
    The gather and store data function will gather the data and create a .csv file to save all the data into,
    each data type will have its own column. Each consecutive data point will be stored in rows under their
    respective columns.
    """

    run_path = mk_run_dir()

    b, t, a, a_x, a_y, a_z, g_x, g_y, g_z = get_data(g_max,g_min, a_cal)

    data_dict = {
        "Barometric Pressure":b,
        "Temperature"        :t,
        "Altitude_B"         :a,
        "Accelerometer_x"    :a_x,
        "Accelerometer_y"    :a_y,
        "Accelerometer_z"    :a_z,
        "Gyroscope_x"        :g_x,
        "Gyroscope_y"        :g_y,
        "Gyroscope_z"        :g_z,
        }
    data = pd.DataFrame.from_dict(data_dict)

    pd.DataFrame.to_csv(data,
                        path_or_buf = run_path / 'Run-Data',
                        mode = 'w'
                        )

    return None

# To do
# def get_gps, will determine devices location
# def determine_b_sea, will gather local barometric pressure at sea level from internet, will call get_gps

if __name__ == '__main__':
    main()