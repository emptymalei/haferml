## Extract

As a first step, we will download the all the data files from the official website of [Rideindego](https://www.rideindego.com/about/data/).

The web page contains multiple links to the file. We will get all the links to the data files using `DataLinkHTMLExtractor` defined in `utils.fetch`. We will then run through each link and download the zip file using `DataDownloader`.


```python
import os

import click
import simplejson as json
from dotenv import load_dotenv
from loguru import logger

from utils.fetch import DataDownloader, DataLinkHTMLExtractor
from utils.fetch import get_page_html as _get_page_html
from haferml.blend.config import Config
from haferml.sync.local import prepare_folders

load_dotenv()

@click.command()
@click.option(
    "-c",
    "--config",
    type=str,
    default=os.getenv("CONFIG_FILE"),
    help="Path to config file",
)
def extract(config):

    base_folder = os.getenv("BASE_FOLDER")
    _CONFIG = Config(config, base_folder=base_folder)

    etl_trip_data_config = _CONFIG.get(["etl", "raw", "trip_data"])
    logger.info(f"Using config: {etl_trip_data_config}")
    # create folders
    prepare_folders(etl_trip_data_config["local"], base_folder)
    # if not os.path.exists(etl_trip_data_config["local"]):
    #     os.makedirs(etl_trip_data_config["local"])

    # Download Raw Data
    source_link = etl_trip_data_config["source"]
    logger.info(f"Will download from {source_link}")
    page = _get_page_html(source_link).get("data", {})
    page_extractor = DataLinkHTMLExtractor(page)
    links = page_extractor.get_data_links()
    logger.info(f"Extracted links from {source_link}: {links}")

    # Download data
    dld = DataDownloader(links, data_type="zip", folder=etl_trip_data_config["local_absolute"])
    dld.run()


if __name__ == "__main__":
    extract()
```