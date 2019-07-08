import datetime
import glob
import json
import os

import praw

from account import *


def save_traffic(traffic):
    now = datetime.datetime.now()
    filename = str(now.today()) + '.json'
    with open('data/' + filename, 'w') as traffic_file:
        traffic_file.write(json.dumps(traffic))
        traffic_file.close()


def retrieve_traffic_stats():
    r = praw.Reddit(client_id=mod_script_id, client_secret=mod_script_secret, user_agent="churning_stats",
                    username=mod_username,
                    password=mod_password)

    sub = r.subreddit('churning')
    traffic = sub.traffic()
    save_traffic(traffic)


def create_csv_from_json(filename):
    csv_filename = filename.replace('json', 'csv')
    if os.path.isfile(csv_filename):
        return
    with open(filename) as json_contents:
        data = json.loads(json_contents.read())

    # Write day
    day_csv = 'unix_time,unique,page_views,subscriptions\n'
    for day in data['day']:
        day_csv += ','.join(map(str, day)) + '\n'

    with open(csv_filename, 'w') as csv:
        csv.write(day_csv)
        csv.close()

    # Write hour
    hour_csv = 'unix,uniques,pageviews\n'
    for hour in data['hour']:
        hour_csv += ','.join(map(str, hour)) + '\n'
    with open(csv_filename.replace('.csv', '_hour.csv'), 'w') as csv:
        csv.write(hour_csv)
        csv.close()

    # Write month
    month_csv = 'unix,uniques,pageviews\n'
    for month in data['month']:
        month_csv += ','.join(map(str, month)) + '\n'
    with open(csv_filename.replace('.csv', '_month.csv'), 'w') as csv:
        csv.write(month_csv)
        csv.close()


def create_stats(filename):
    with open(filename) as json_contents:
        data = json.loads(json_contents.read())

    subs_60_days = 0
    least = {'amount': 99999, 'day': None}
    most = {'amount': -1, 'day': None}
    for day in data['day']:
        subs_60_days += day[3]
        if day[3] < least['amount'] and day[3]:
            least['amount'] = day[3]
            least['day'] = day[0]
        if day[3] > most['amount']:
            most['amount'] = day[3]
            most['day'] = day[0]


    print(f'{subs_60_days} new subscriptions in last {len(data["day"])} days')
    print(f'The most subscriptions, {most["amount"]}, were on {datetime.datetime.utcfromtimestamp(most["day"]).strftime("%Y-%m-%d")}')
    print(f'The least subscriptions, {least["amount"]}, were on {datetime.datetime.utcfromtimestamp(least["day"]).strftime("%Y-%m-%d")}')


def create_csvs_from_json():
    json_files = glob.glob('data/*.json')
    for file in json_files:
        create_csv_from_json(file)
        create_stats(file)


if __name__ == "__main__":
    create_csvs_from_json()
