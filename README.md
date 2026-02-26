# INA-data-scrapper

This Python project is designed to extract the data from the https://data.ina.fr/ website.
Specifically, this program aims at extracting the data from the charts ([exemple here](https://data.ina.fr/cles-lecture/femmes-hommes#comment-repartit-temps-parole-femmes-hommes-semaine)). The extracted data are published here : https://www.data.gouv.fr/datasets/ina-comment-se-repartit-le-temps-de-parole-femmes-hommes-dans-la-semaine.

For the moment only 2 charts have been implemented. Feel free to contribute to this project ([see section bellow](#contribute)).

To use this program, create a python script (in this exemple `main.py` and paste the following code).
Each implemented chart has its own class(es) to extract the data. Instantiate the matching class with the parameters to
filter, extract and save the data.

Here is an exemple to extract the data from the _"Comment évolue la répartition du temps de parole entre les femmes et les hommes ?"_ chart :

```python
from src.speech_time_male_female.evolution import *
import os
import time


def main() -> None:
    # Defines the root directory to store the files.
    base_path: str = os.path.join(os.getcwd(), "output/speech_time_male_female_evolution")

    # For all available channels in the generalist channels section.
    for channel in GeneralistChannels.all():
        # Defines a specific directory to store the generated files.
        path = os.path.join(base_path, f"generalist_channels/{str(channel)}")

        # Attempts to extract the data of the channel in CSV format.
        # If it could not extract the data it stops.
        if not SpeechTimeEvolutionGeneralist(channel, path, SaveMode.CSV).get():
            return

        # Waits 1 second to not get IP banned.
        time.sleep(1)

    for channel in NewsChannels.all():
        # Defines a specific directory to store the generated files.
        path = os.path.join(base_path, f"news_channels/{str(channel)}")

        # Attempts to extract the data of the channel in CSV format.
        # If it could not extract the data it stops.
        if not SpeechTimeEvolutionNews(channel, path, SaveMode.CSV).get():
            return

        # Waits 1 second to not get IP banned.
        time.sleep(1)

    for radio in Radios.all():
        # Defines a specific directory to store the generated files.
        path = os.path.join(base_path, f"radios/{str(radio)}")

        # Attempts to extract the data of the radio in CSV format.
        # If it could not extract the data it stops.
        if not SpeechTimeEvolutionRadio(radio, path, SaveMode.CSV).get():
            return

        # Waits 1 second to not get IP banned.
        time.sleep(1)

if __name__ == "__main__":
    main()
```

## Implemented charts

For the moment, these are the implemented charts :

- https://data.ina.fr/cles-lecture/femmes-hommes#comment-repartit-temps-parole-femmes-hommes-semaine
  - Quelle est la répartition du temps de parole entre les femmes et les hommes sur les chaînes de radio et de télévision ?
    <br />
    `src.speech_time_male_female.repartition`
  - Comment évolue la répartition du temps de parole entre les femmes et les hommes ?
    <br />
    `src.speech_time_male_female.evolution`

## Contribute

To contribute to this project you can choose a chart and apply the following process:

1. Create a directory for a specific web page and / or a python file for each chart in this directory.
2. List all the filters of the chart (note that if there are a lot of filters it might be better not to add the time range filters).
3. For each filter extract the corresponding URL. To do so :
   1. Go to the web page at the chart.
   2. Open your web browser dev tools panel (`F12` or `CTRL` + `MAJ` + `I` or Right click > inspect)
   3. Select the network tab.
   4. Clear the network tab (little bin icon).
   5. Select and apply the filters.
   6. You should see lines appearing in the network tab.
   7. Select the `GET` method with `JSON` format (the largest one).
   8. Right click it and select copy the URL. (Note that it might change depending on your web browser but it will be pretty similar).
4. Use the same code structure for the other charts but with the copied URL.
5. Make sure to test it :)
