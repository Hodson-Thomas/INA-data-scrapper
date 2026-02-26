import requests
from enum import Enum
from typing import Dict, Any, List, Set
from src.save_mode import SaveMode
import json
import csv
import logging


class TimeRange(Enum):
    """Represents the chart's available time ranges.
    """
    LAST_DAY = "1d"
    LAST_SEVEN_DAYS = "7d"
    LAST_MONTH = "1m"
    LAST_SIX_MONTHS = "6m"
    LAST_YEAR = "1y"
    ALL = "all"


class SpeechTimeRepartition:
    """Handles the chart's data with 'TimeRange' filters.
    """

    def __init__(self, save_mode: SaveMode, path: str, range: TimeRange) -> None:
        """Classes' constructor.

        Args:
            save_mode (SaveMode): The data saving format.
            path (str): The storage folder.
            range (TimeRange): The chart's selected time range.
        """
        self.save_mode = save_mode
        self.path = path
        self.range = range

    def get(self) -> bool:
        """Extracts and saves the selected time range's corresponding chart's data. 

        Returns:
            bool: Indicates if this operation was a success.
        """
        match self.range:
            case TimeRange.LAST_DAY:
                return self.__query_data(
                    'https://data-api.ina.fr/api/chart/76fa3d95cd85849475c3890c1860e1ce?filtres=f389eac567c2358bf7e72824362caf71bdfbed4e2c69188d0a3769b769ac2ef5f054704035454c71e088a99d44f0d4a8')
            case TimeRange.LAST_SEVEN_DAYS:
                return self.__query_data(
                    "https://data-api.ina.fr/api/chart/76fa3d95cd85849475c3890c1860e1ce?filtres=f389eac567c2358bf7e72824362caf71db12739db299e043308b9be344785a40f054704035454c71e088a99d44f0d4a8")
            case TimeRange.LAST_MONTH:
                return self.__query_data(
                    'https://data-api.ina.fr/api/chart/76fa3d95cd85849475c3890c1860e1ce?filtres=f389eac567c2358bf7e72824362caf71d0bcc5517b73ce7cc234d8f47ff72942f054704035454c71e088a99d44f0d4a8')
            case TimeRange.LAST_SIX_MONTHS:
                return self.__query_data(
                    'https://data-api.ina.fr/api/chart/76fa3d95cd85849475c3890c1860e1ce?filtres=f389eac567c2358bf7e72824362caf71d36ab66320dd492ba4b0c066ad5802fef054704035454c71e088a99d44f0d4a8')
            case TimeRange.LAST_YEAR:
                return self.__query_data(
                    'https://data-api.ina.fr/api/chart/76fa3d95cd85849475c3890c1860e1ce?filtres=f389eac567c2358bf7e72824362caf7109f92713c458f9b319480ff89de4060cf054704035454c71e088a99d44f0d4a8')
            case TimeRange.ALL:
                return self.__query_data(
                    'https://data-api.ina.fr/api/chart/76fa3d95cd85849475c3890c1860e1ce?filtres=6af3bb0ab8bd716eeb3d973f0672459009f92713c458f9b319480ff89de4060cf054704035454c71e088a99d44f0d4a8')
            case _:
                logging.critical(f"TIME RANGE {self.range} has not been implemented.")
                return False

    def __query_data(self, url: str) -> bool:
        """Queries the chart's data using thje given URL.

        Args:
            url (str): The chart's URL with the active filters.

        Returns:
            bool: Indicates if this operation was a success.
        """
        try:
            data = requests.get(url).json()
            return self.__clean_data(data)
        except Exception as e:
            logging.error(e)
            return False

    def __clean_data(self, json: Dict[str, Any]) -> bool:
        """Cleans the given JSON data.

        Args:
            json (Dict[str, Any]): The JSON data to clean.

        Returns:
            bool: Indicates if this operation was a success.
        """
        if (data := json.get('data')) is None:
            logging.error(f"Could not extract 'data' param from queried json")
            return False

        keys = list(data.keys())
        if len(keys) == 0:
            logging.error(f"Empty object.")
            return False

        data = data[keys[0]]
        if (d := data.get('data')) is None:
            logging.error(f"Could not extract 'data' param from queried json")
            return False

        if (chart_rows := d.get('chartDatasRow')) is None:
            logging.error(f"Could not extract 'chartDatasRow' param from queried json")
            return False

        return self.__save_to_file(chart_rows)

    def __save_to_file(self, data: List[Dict[str, Any]]) -> bool:
        """Saves the given data in the storage folder with the selected saving format.

        Args:
            data (List[Dict[str, Any]]): The data to save.

        Returns:
            bool: Indicates if this operation was a success.
        """
        match self.save_mode:
            case SaveMode.CSV:
                return self.__save_to_csv(data)
            case SaveMode.JSON:
                return self.__save_to_json(data)
            case _:
                logging.critical(f"SAVE MODE {self.save_mode} has not been implemented")
                return False

    def __save_to_json(self, data: List[Dict[str, Any]]) -> bool:
        """Saves the given data in the storage folder in JSON format.

        Args:
            data (List[Dict[str, Any]]): The data to save.

        Returns:
            bool: Indicates if this operation was a success.
        """
        try:
            with open(self.path, 'w') as f:
                json.dump({"data": data}, f)
        except Exception as e:
            logging.error(e)
            return False
        return True

    def __save_to_csv(self, data: List[Dict[str, Any]]) -> bool:
        """Saves the given data in the storage folder in CSV format.

        Args:
            data (List[Dict[str, Any]]): The data to save.

        Returns:
            bool: Indicates if this operation was a success.
        """
        field_names: Set[str] = set()

        for item in data:
            field_names.update(item.keys())

        try:
            with open(self.path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=field_names)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            logging.error(e)
            return False

        return True
