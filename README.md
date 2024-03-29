<!-- # KeywordsSearcher

## Installation

### Virtual environment
It is recomended to use virtual environment for the project. To install it with name `env` use command:
```
python -m venv env
```
Now to activate virtual environment with name `env` use:
```
source ./env/bin/activate
```
Upgrade `pip`:
```
pip install --upgrade pip
```
Or (on `Windows` recommended):
```
python -m pip install --upgrade pip
```

### Packages
Tested python version for this project is `Python 3.8.9`. Install requirement packages by following command:
```
pip install -r requirements.txt
```

### Files needed

Not all files are provided in the repository.

#### Keywords list
If you want to use keywords statistics search, you should create file with list of keywords at directory `resources`. Every keyword should be seperated with `\n` - new line symbol. Default file name is **keywords.csv** but you can change it in `settings.json`.

#### Chromedriver
You also should download **chromedriver** that suits to your system.

1. To know your **chrome version** go to Chrome settings: chrome://settings/help;
2. Go to [Chromedriver web page](https://chromedriver.chromium.org/downloads) and download **chromedriver** that suits your chrome versions and OS version;
3. Put the file into directory `driver`. You can also change folder path in `settings.json`.

# Settings

All flexible settings of the application are in `settings.json`.

- **keyword** - str; `Keyword` for the first iteration of app links finding. (Not needed for now);
- **driver_path** - str; Destination path to the `chromedriver`. Defult value is `"driver/chromedriver"`;
- **keyword_file_path** - str; Destination path to the `keyword list`. Defult value is `"resources/keywords.csv"`;
- **time_to_sleep** - float; `Base time` to wait between operations. For now it is set to `1`. It means that script scrolls down page and waits `1` second untill new apps are loaded. If they are still loading - wait half of the time while not; 
- **is_headless_mode** - bool; `Hide chromedriver` GUI or not. By tests it is **not** significantly improving performance in perpose of time but maybe it reduces the load on RAM or processor. By default set to `True`;
- **number_of_threads** - int; `Number of threads` - how many driver instance would be scanning pages in parallel. By default set to `2`;
- **app_links** - list(str); `List of app links` whose positions need to be checked.
- **timeout_time** - int; Time in seconds to wait for connection.

# Usage

The entry point of the application is `main.py`. To see help, input this in command line:
```
python main.py --help
```
Output:
```
usage: Keywords searcher [-h] [--links] [--kwstats] [--mergestats [D [D ...]]]

This programm is written for automate the process of finding links, keywords statistics.

optional arguments:
  -h, --help            show this help message and exit
  --links               Upload links for the keyword that is set in settings.json.
  --kwstats             Upload keywords statistics (Also starts if none of the other parameter were given).
  --mergestats [D [D ...]]
                        Merges statistics for given days.
```

This means that for now you can use 3 main functionalities - upload links, upload keywords statistics, merge uploaded keywords statistics in one file. For instance:
```
python main.py --links                  # Uploads the links
python main.py --kwstats                # Uploads keywords statistics
python main.py --links --kwstats        # Uploads links and then keywords statistics
python main.py --mergestats 2022-05-05  # Merges uploaded keywords statistics for day 2022-05-05
python main.py                          # Uploads keywords statistics
``` -->
