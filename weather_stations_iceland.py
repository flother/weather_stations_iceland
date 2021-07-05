import scrapy


class WeatherStationsSpider(scrapy.Spider):
    """
    Scrape Icelandic weather stations from Veðurstofan's website.

    The scraper starts at <https://en.vedur.is/weather/stations/> and
    follows each station's "Info." link. The links lead to pages like
    <https://en.vedur.is/weather/stations/?s=eyrar>. These contain a
    table of metadata on individual weather stations, including
    information such as name, location, and height above sea-level.

    A station's metadata is converted into a JSON object and returned
    for Scrapy to handle. For details on what Scrapy does and what you
    can do with it, see the Scrapy documentation:

    - <https://docs.scrapy.org/en/2.5/>
    - <https://docs.scrapy.org/en/2.5/topics/spiders.html>
    - <https://docs.scrapy.org/en/2.5/topics/items.html>
    """

    name = "weather_stations"
    start_urls = ["https://en.vedur.is/weather/stations/"]

    def parse(self, response):
        # The seventh `td` element in each row contains a station's "Info." link. The
        # page it links to gives us the metadata we need. Example metadata page:
        # <https://en.vedur.is/weather/stations/?s=eyrar>
        for station_info in response.css("table td:nth-child(7) a"):
            yield response.follow(station_info, self.parse_station)

    def parse_station(self, response):
        # A station's table of metadata has a row for each attribute and they're always
        # in the same order. We can loop through the rows and use the text in the last
        # `td` child as the attribute value.
        (
            name,
            type,
            station_number,
            wmo_number,
            abbreviation,
            forecast_region,
            location,
            elevation,
            start_year,
            owner,
        ) = [t.get() for t in response.css("table.infotable tr>td:last-child::text")]

        station_number = int(station_number)
        wmo_number = int(wmo_number)
        # The location is a string like "63°52.152', 21°09.611' (63.8692, 21.1602)". We
        # can parse the decimal degrees by getting the text within the brackets and
        # splitting on the comma. Note that the longitude is west of Greenwich but is
        # given without a minus sign (e.g. 21.1602 needs to be converted to -21.1602).
        latitude, longitude = [
            float(l.strip(")")) for l in location.split("(", 1)[1].split(",", 1)
        ]
        if longitude > 0:
            longitude = -longitude
        # The region is something like "South(su)" so we want to remove the "(su)".
        forecast_region = forecast_region.split("(")[0]
        # Elevation is given as e.g. "3.0 m a.s.l." and we only want the number.
        elevation = float(elevation.split(" ")[0])
        start_year = int(start_year)

        yield {
            "name": name,
            "type": type,
            "station_number": station_number,
            "wmo_number": wmo_number,
            "abbreviation": abbreviation,
            "region": forecast_region,
            "longitude": longitude,
            "latitude": latitude,
            "elevation": elevation,
            "start_year": start_year,
            "owner": owner,
        }
