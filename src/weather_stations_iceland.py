import scrapy


class WeatherStationsSpider(scrapy.Spider):
    name = "weather_stations"
    start_urls = ["https://en.vedur.is/weather/stations/"]

    def parse(self, response):
        for station_info in response.css("table td:nth-child(7) a"):
            yield response.follow(station_info, self.parse_station)

    def parse_station(self, response):
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
        latitude, longitude = [
            float(l.strip(")")) for l in location.split("(", 1)[1].split(",", 1)
        ]
        if longitude > 0:
            longitude = -longitude
        forecast_region = forecast_region.split("(")[0]
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
