"""
This python script handles data extraction from the https://data.ina.fr/cles-lecture/femmes-hommes#comment-repartit-temps-parole-femmes-hommes-semaine
specifically the "Comment évolue la répartition du temps de parole entre les femmes et les hommes ?" chart
"""

from typing import List, Any, Dict, Set
from enum import Enum
import requests
import json
import csv
import logging
from src.save_mode import SaveMode
import os


class GeneralistChannels(Enum):
    """Represents all the available generalist channels for this chart.
    """
    ARTE = "arte"
    CANAL_PLUS = "canal+"
    FRANCE2 = "france2"
    FRANCE3 = "france3"
    FRANCE5 = "france5"
    M6 = "m6"
    TV5_MONDE = "tv5monde"
    TF1 = "tf1"

    @staticmethod
    def all() -> list["GeneralistChannels"]:
        """Returns all the available generalist channels for this chart.
        """
        return [
            GeneralistChannels.ARTE,
            GeneralistChannels.CANAL_PLUS,
            GeneralistChannels.FRANCE2,
            GeneralistChannels.FRANCE3,
            GeneralistChannels.FRANCE5,
            GeneralistChannels.M6,
            GeneralistChannels.TV5_MONDE,
            GeneralistChannels.TF1,
        ]


class NewsChannels(Enum):
    """Represents all the available news channels for this chart.
    """
    BMF_TV = "bfmtv"
    CNEWS = "cnews"
    FRANCE_INFO = "franceinfo"
    FRANCE_24 = "france24"
    LCI = "lci"

    @staticmethod
    def all() -> List["NewsChannels"]:
        """Returns all the available news channels for this chart.
        """
        return [
            NewsChannels.BMF_TV,
            NewsChannels.CNEWS,
            NewsChannels.FRANCE_INFO,
            NewsChannels.FRANCE_24,
            NewsChannels.LCI,
        ]


class Radios(Enum):
    """Represents all the available radios for this chart.
    """

    FRANCE_CULTURE = "franceculture"
    FRANCE_INFO = "franceinfo"
    FRANCE_INTER = "franceinter"
    RMC = "rmc"
    RTL = "rtl"

    @staticmethod
    def all() -> List["Radios"]:
        """Returns all the available radios for this chart.
        """
        return [
            Radios.FRANCE_CULTURE,
            Radios.FRANCE_INFO,
            Radios.FRANCE_INTER,
            Radios.RMC,
            Radios.RTL,
        ]


class SpeechTimeEvolution:
    """This top level class handles the chart's data extraction. 
    """

    def __init__(self, directory_path: str, save_mode: SaveMode) -> None:
        """Classes' constructor.

        Args:
            directory_path (str): The directory in which the extracted data will be stored.
            save_mode (SaveMode): The extracted data saving format.
        """
        self.directory_path = directory_path
        self.save_mode = save_mode

    def process(self, url: str) -> bool:
        """Extracts and saves the data from the chart using the given URL.

        Args:
            url (str): The chart's URL with filters.

        Returns:
            bool: Indicates if this operation was a success.
        """
        try:
            req = requests.get(url).json()

            if (data := req.get("data")) is None:
                logging.error("Could not get 'data' param from json object.")
                return False

            keys = list(data.keys())

            if len(keys) != 2:
                logging.error("Could not extract chart data from json object.")
                return False

            return self.process_dynamic_data(data[keys[0]]) and self.process_dynamic_race(
                data[keys[0]]) and self.process_aggredated_historical_view(data[keys[1]])

        except Exception as e:
            logging.error(f"Could not process {url} due to {e}")
            return False

    def process_dynamic_data(self, obj: Dict[str, Any]) -> bool:
        """Extracts and saves the data from the chart's 'dynamic' tab static mode.

        Args:
            obj (Dict[str, Any]): The requested json object.

        Returns:
            bool: Indicates if this operation was a success.
        """
        path = os.path.join(self.directory_path, f"dynamic_data{self.save_mode.extension}")

        if (data := obj.get('data')) is None:
            logging.error("Could not get 'data' param from obj.")
            return False

        if (chartDatasRow := data.get('chartDatasRow')) is None:
            logging.error("Could not get 'chartDatasRow' param from obj.")
            return False

        return save_file(self.save_mode, path, chartDatasRow)

    def process_dynamic_race(self, obj: Dict[str, Any]) -> bool:
        """Extracts and saves the data from the chart's 'dynamic' tab animated mode.

        Args:
            obj (Dict[str, Any]): The requested json object.

        Returns:
            bool: Indicates if this operation was a success.
        """
        path = os.path.join(self.directory_path, f"dynamic_race{self.save_mode.extension}")

        if (race := obj.get('race')) is None:
            logging.error("Could not get 'race' param from obj.")
            return False

        if (datas := race.get('datas')) is None:
            logging.error("Could not get 'datas' param from obj.")
            return False

        res: List[Dict[str, Any]] = list()

        for (date, lst) in datas.items():
            for item in lst:
                if len(item) != 2:
                    continue

                if len(item[1].keys()) != 1:
                    continue

                res.append({
                    "date": date,
                    "label": item[0],
                    "value": item[1][list(item[1].keys())[0]]
                })

        return save_file(self.save_mode, path, res)

    def process_aggredated_historical_view(self, obj: Dict[str, Any]) -> bool:
        """Extracts and saves the data from the chart's 'aggregated historical' tab.

        Args:
            obj (Dict[str, Any]): The requested json object.

        Returns:
            bool: Indicates if this operation was a success.
        """
        path = os.path.join(self.directory_path, f"aggregated_historical_view{self.save_mode.extension}")

        if (data := obj.get('data')) is None:
            logging.error("Could not get 'data' param from obj.")
            return False

        if (chartDatasRow := data.get('chartDatasRow')) is None:
            logging.error("Could not get 'chartDatasRow' param from obj.")
            return False

        return save_file(self.save_mode, path, chartDatasRow)


class SpeechTimeEvolutionGeneralist(SpeechTimeEvolution):
    """Handles the chart's data with 'Generalist channels' filters.

    Args:
        SpeechTimeEvolution (_type_): Data extraction behavior.
    """

    def __init__(self, channel: GeneralistChannels, directory_path: str, save_mode: SaveMode) -> None:
        """Classes' constructor.

        Args:
            channel (GeneralistChannels): The targeted channel.
            directory_path (str): The directory in which the extracted data will be stored. 
            save_mode (SaveMode): The extracted data saving format.
        """
        super().__init__(directory_path, save_mode)
        self.channel = channel

    def get(self) -> bool:
        """Extracts and saves the targeted channel's corresponding chart's data. 

        Returns:
            bool: Indicates if this operation was a success.
        """
        match self.channel:
            case GeneralistChannels.ARTE:
                print("[SpeechTimeEvolutionGeneralist > ARTE] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=d3311596414ff35e4ea801dc0a643fa5b4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c92a3d22d70da460249151b328dc4732e21c76ad32c83128dbecb31f81802c0f7b601c7314ab52da511ad299be44ca5cc44be2e1b001130e0ce50c65fcf0d96720")
            case GeneralistChannels.CANAL_PLUS:
                print("[SpeechTimeEvolutionGeneralist > CANAL_PLUS] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=c5053995089e5af260cfad1b9f6c533bb4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c92a3d22d70da460249151b328dc4732e21c76ad32c83128dbecb31f81802c0f7b601c7314ab52da511ad299be44ca5cc44be2e1b001130e0ce50c65fcf0d96720")
            case GeneralistChannels.FRANCE2:
                print("[SpeechTimeEvolutionGeneralist > FRANCE2] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=aedeb93f19ce14a833c2e9c02b5e8deeb4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c92a3d22d70da460249151b328dc4732e21c76ad32c83128dbecb31f81802c0f7b601c7314ab52da511ad299be44ca5cc44be2e1b001130e0ce50c65fcf0d96720")
            case GeneralistChannels.FRANCE3:
                print("[SpeechTimeEvolutionGeneralist > FRANCE3] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=a5739c6458b03c7ef82a436e0efe8745b4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c92a3d22d70da460249151b328dc4732e21c76ad32c83128dbecb31f81802c0f7b601c7314ab52da511ad299be44ca5cc44be2e1b001130e0ce50c65fcf0d96720")
            case GeneralistChannels.FRANCE5:
                print("[SpeechTimeEvolutionGeneralist > FRANCE5] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=3d84ccd70b9b92656f55c0e8b4b6a20fb4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c92a3d22d70da460249151b328dc4732e21c76ad32c83128dbecb31f81802c0f7b601c7314ab52da511ad299be44ca5cc44be2e1b001130e0ce50c65fcf0d96720")
            case GeneralistChannels.M6:
                print("[SpeechTimeEvolutionGeneralist > M6] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=9bd75df8ecc6173bd6c1d711ccf1a888b4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c92a3d22d70da460249151b328dc4732e21c76ad32c83128dbecb31f81802c0f7b601c7314ab52da511ad299be44ca5cc44be2e1b001130e0ce50c65fcf0d96720")
            case GeneralistChannels.TV5_MONDE:
                print("[SpeechTimeEvolutionGeneralist > TV5_MONDE] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=78a31be17a0cf997a5006fc62df11336b4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c92a3d22d70da460249151b328dc4732e21c76ad32c83128dbecb31f81802c0f7b601c7314ab52da511ad299be44ca5cc44be2e1b001130e0ce50c65fcf0d96720")
            case GeneralistChannels.TF1:
                print("[SpeechTimeEvolutionGeneralist > TF1] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=080b536fe60754bffe8528149b077293b4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c92a3d22d70da460249151b328dc4732e21c76ad32c83128dbecb31f81802c0f7b601c7314ab52da511ad299be44ca5cc44be2e1b001130e0ce50c65fcf0d96720")
            case _:
                logging.error(f"GENERALIST CHANNEL {self.channel} is not yet implemented.")
                return False


class SpeechTimeEvolutionNews(SpeechTimeEvolution):
    """Handles the chart's data with 'News channels' filters.

    Args:
        SpeechTimeEvolution (_type_): Data extraction behavior.
    """

    def __init__(self, channel: NewsChannels, directory_path: str, save_mode: SaveMode) -> None:
        """Classes' constructor.

        Args:
            channel (NewsChannels): The targeted channel.
            directory_path (str): The directory in which the extracted data will be stored. 
            save_mode (SaveMode): The extracted data saving format.
        """
        super().__init__(directory_path, save_mode)
        self.channel = channel

    def get(self) -> bool:
        """Extracts and saves the targeted channel's corresponding chart's data. 

        Returns:
            bool: Indicates if this operation was a success.
        """
        match self.channel:
            case NewsChannels.BMF_TV:
                print("[SpeechTimeEvolutionNews > BMF_TV] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=2e4748bc81b59c7227c83050bcce95d8b4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c93ccf4cc32cc92f2eff86aac64b98c78dff476f91511d0063f451cd9f077b8f1789b474585430e74d3239289a1aa72779f282064c81965a139abbf8b09f1b7e1e")
            case NewsChannels.CNEWS:
                print("[SpeechTimeEvolutionNews > CNEWS] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=d31df74ec6373c0ed2e7cd97dc89695cb4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c93ccf4cc32cc92f2eff86aac64b98c78dff476f91511d0063f451cd9f077b8f1789b474585430e74d3239289a1aa72779f282064c81965a139abbf8b09f1b7e1e")
            case NewsChannels.FRANCE_INFO:
                print("[SpeechTimeEvolutionNews > FRANCE_INFO] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=7cef780dc74ca1ac8cb8aa8f3562d2f1b4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c93ccf4cc32cc92f2eff86aac64b98c78dff476f91511d0063f451cd9f077b8f1789b474585430e74d3239289a1aa72779f282064c81965a139abbf8b09f1b7e1e")
            case NewsChannels.FRANCE_24:
                print("[SpeechTimeEvolutionNews > FRANCE_24] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=033a7b21cf56fedd5cace7d001b4d138b4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c93ccf4cc32cc92f2eff86aac64b98c78dff476f91511d0063f451cd9f077b8f1789b474585430e74d3239289a1aa72779f282064c81965a139abbf8b09f1b7e1e")
            case NewsChannels.LCI:
                print("[SpeechTimeEvolutionNews > LCI] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=dba036f51483314da73e52dc46637de3b4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c93ccf4cc32cc92f2eff86aac64b98c78dff476f91511d0063f451cd9f077b8f1789b474585430e74d3239289a1aa72779f282064c81965a139abbf8b09f1b7e1e")
            case _:
                logging.error(f"NEWS CHANNEL {self.channel} is not yet implemented.")
                return False


class SpeechTimeEvolutionRadio(SpeechTimeEvolution):
    """Handles the chart's data with 'Radios' filters.

    Args:
        SpeechTimeEvolution (_type_): Data extraction behavior.
    """

    def __init__(self, radio: Radios, directory_path: str, save_mode: SaveMode) -> None:
        """Classes' constructor.

        Args:
            channel (Radios): The targeted radio.
            directory_path (str): The directory in which the extracted data will be stored. 
            save_mode (SaveMode): The extracted data saving format.
        """
        super().__init__(directory_path, save_mode)
        self.radio = radio

    def get(self) -> bool:
        """Extracts and saves the targeted radio's corresponding chart's data. 

        Returns:
            bool: Indicates if this operation was a success.
        """
        match self.radio:
            case Radios.FRANCE_CULTURE:
                print("[SpeechTimeEvolutionRadio > FRANCE_CULTURE] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=0329f4bb42ab291561391abfc6a4cf6bb4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c9b579a002c4f0d2ed4d6035206f9a80b91ec3a0ca728da74a96d4647e7e12e36b12633449c3b7db421b2af4e9f600a878")
            case Radios.FRANCE_INFO:
                print("[SpeechTimeEvolutionRadio > FRANCE_INFO] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=3c7bfb46a49c3d55c0e1fc69895b60d0b4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c9b579a002c4f0d2ed4d6035206f9a80b91ec3a0ca728da74a96d4647e7e12e36b12633449c3b7db421b2af4e9f600a878")
            case Radios.FRANCE_INTER:
                print("[SpeechTimeEvolutionRadio > FRANCE_INTER] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=8e29023ec6201405a32ba549727d6f9bb4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c9b579a002c4f0d2ed4d6035206f9a80b91ec3a0ca728da74a96d4647e7e12e36b12633449c3b7db421b2af4e9f600a878")
            case Radios.RMC:
                print("[SpeechTimeEvolutionRadio > RMC] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=58c6278faeb0f84c77092af450bafd1bb4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c9b579a002c4f0d2ed4d6035206f9a80b91ec3a0ca728da74a96d4647e7e12e36b12633449c3b7db421b2af4e9f600a878")
            case Radios.RTL:
                print("[SpeechTimeEvolutionRadio > RTL] Query...")
                return self.process(
                    "https://data-api.ina.fr/api/chart/f579cec8bf6bfa001ec09f04dbbb5907?filtres=0b7420b860a4e3db8dc806c2600f5dfcb4ae138172b1cdbae3e39aa87d481e1bc14c6677efb0978ca9df5717add142a2b6daafe7474327025cfaf1e3dc42c8354b479dad98b1b1ffe59dcc4239b712c9b579a002c4f0d2ed4d6035206f9a80b91ec3a0ca728da74a96d4647e7e12e36b12633449c3b7db421b2af4e9f600a878")
            case _:
                logging.error(f"RADIOS {self.radio} is not yet implemented.")
                return False


def ensure_file(path: str) -> None:
    """Creates the given path if it does not exists.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not os.path.exists(path):
        with open(path, "w"):
            pass


def save_file(save_mode: SaveMode, file_path: str, data: List[Dict[str, Any]]) -> bool:
    """Saves the given data in the given format at the given path.

    Args:
        save_mode (SaveMode): The data saving format.
        file_path (str): The storage path.
        data (List[Dict[str, Any]]): The data to store.

    Returns:
        bool: Indicates if this operation was a success.
    """
    ensure_file(file_path)

    match save_mode:
        case SaveMode.CSV:
            return save_to_csv(file_path, data)
        case SaveMode.JSON:
            return save_to_json(file_path, data)
        case _:
            logging.error(f"SAVE MODE {save_mode} has not been implemented yet.")
            return False


def save_to_json(file_path: str, data: List[Dict[str, Any]]) -> bool:
    """Saves the given in JSON format at the given path.

    Args:
        file_path (str): The storage path.
        data (List[Dict[str, Any]]): The data to store.

    Returns:
        bool: Indicates if this operation was a success.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump({"data": data}, file)
    except Exception as e:
        logging.error(f"Could not save object in JSON format due to {e}.")
        return False
    return True


def save_to_csv(file_path: str, data: List[Dict[str, Any]]) -> bool:
    """Saves the given in CSV format at the given path.

    Args:
        file_path (str): The storage path.
        data (List[Dict[str, Any]]): The data to store.

    Returns:
        bool: Indicates if this operation was a success.
    """
    field_names: Set[str] = set()
    for item in data:
        field_names.update(item.keys())

    try:
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        logging.error(e)
        return False

    return True
