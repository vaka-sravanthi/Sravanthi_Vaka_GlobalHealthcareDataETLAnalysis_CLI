import requests
import configparser
import logging
from datetime import datetime
class APIClient:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.base_url = config['api']['url']
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def fetch_data(self, country, start_date, end_date):
        url = f"{self.base_url}/{country}?lastdays=all"
        try:
            logging.info(f" Fetching historical data for {country} from API...")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if 'timeline' not in data:
                logging.warning(f" No timeline data found for {country}.")
                return []

            cases = data['timeline'].get('cases', {})
            deaths = data['timeline'].get('deaths', {})
            recovered = data['timeline'].get('recovered', {})
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            filtered_data = []
            for date_str in cases:
                try:
                    date_obj = datetime.strptime(date_str, "%m/%d/%y")
                except ValueError:
                    logging.warning(f"Invalid date format: {date_str}")
                    continue

                if start <= date_obj <= end:
                    filtered_data.append({
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "country": country,
                        "cases": cases.get(date_str, 0),
                        "deaths": deaths.get(date_str, 0),
                        "recovered": recovered.get(date_str, 0)
                    })

            logging.info(f" Retrieved {len(filtered_data)} records for {country} between {start_date} and {end_date}.")
            return filtered_data

        except requests.exceptions.RequestException as e:
            logging.error(f" Error fetching data from API: {e}")
            return []
