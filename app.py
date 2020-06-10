from flask import Flask
import pandas as pd
import time
import copy
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)


@app.route('/')
def hello_world():
    caps = copy.deepcopy(DesiredCapabilities.CHROME)
    caps['loggingPrefs'] = {'performance': 'ALL'}

    chrome_options = Options()
    chrome_options.add_experimental_option('w3c', False)

    driver = webdriver.Chrome(
        desired_capabilities=caps, options=chrome_options)

    driver.implicitly_wait(8)  # set timeout to 8 seconds

    driver.get('https://www.maps.ie/coordinates.html')
    time.sleep(30)  # wait for page to load for the first time

    p = driver.get_log('performance')  # discard all previous logs

    cdp = []
    time.sleep(10)  # make sure page loaded completely before writing log

    # Write to CSV file
    with open('logspo.txt', 'w') as f:
        for entry in p:
            f.write(str(entry) + '\n')
    driver.close()

    with open('logspo.txt') as infile, open('outfile.csv', 'w') as outfile:
        for line in infile:
            outfile.write(line.replace(' ', ','))
    outfile.close()

    lines_list = []
    with open('outfile.csv') as csv_file:
        for line in csv_file:
            lines_list.append(line)

    df_lat_lng = pd.DataFrame(columns=['lat', 'lng'])

    i = 0
    for line in lines_list:
        if len(line.split('srtm3JSON?lat=')) > 1:
            df_lat_lng.loc[i, 'lat'] = line.split('srtm3JSON?lat=')[1].split('&lng=')[0]
            df_lat_lng.loc[i, 'lng'] = line.split('srtm3JSON?lat=')[1].split('&lng=')[1].split('&username')[0]
        i += 1

    df_lat_lng.drop_duplicates(inplace=True)
    df_lat_lng.to_csv('lat_lng.csv')

    return ('Thank You!')


if __name__ == '__main__':
    app.run()
