import argparse
import csv
import re
import requests
import os
from collections import defaultdict
from datetime import datetime

def download_log_file(url):
    try:
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            file_name = os.path.basename(url)
            save_directory = 'log'
            os.makedirs(save_directory, exist_ok=True)
            file_path = os.path.join(save_directory, file_name)

            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            return file_path

        else:
            print(f"Failed to download the file. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while downloading the file: {str(e)}")
        return None

def process_log_file(log_file):
    image_hits = 0
    total_hits = 0
    browser_counts = defaultdict(int)
    hour_counts = defaultdict(int)

    with open(log_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            total_hits += 1
            path, datetime_str, user_agent, status, size = row

            if re.search(r'\.(jpg|gif|png)$', path, re.IGNORECASE):
                image_hits += 1
            if re.search(r'Firefox', user_agent):
                browser_counts['Firefox'] += 1
            elif re.search(r'Chrome', user_agent):
                browser_counts['Chrome'] += 1
            elif re.search(r'Internet Explorer', user_agent):
                browser_counts['Internet Explorer'] += 1
            elif re.search(r'Safari', user_agent):
                browser_counts['Safari'] += 1

            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

            hour = dt.hour
            hour_counts[hour] += 1

    image_percentage = (image_hits / total_hits) * 100
    most_popular_browser = max(browser_counts, key=browser_counts.get)
    print(f"Image requests account for {image_percentage:.1f}% of all requests")
    print(f"The most popular browser is {most_popular_browser}")

    for hour in sorted(hour_counts.keys()):
        print(f"Hour {hour:02d} has {hour_counts[hour]} hits")

def main():
    parser = argparse.ArgumentParser(description='Web Log Analyzer')
    parser.add_argument('--url', type=str, required=True, help='URL of the web log file')
    args = parser.parse_args()

    log_file = download_log_file(args.url)
    if log_file:
        process_log_file(log_file)

if __name__ == '__main__':
    main()