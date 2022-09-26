# Celestial almanac, 1550-2649
[A Python script](https://github.com/cjwinchester/full-moons-soltices-equinoxes-eclipses/blob/main/compute_events.py) to compute data on full moons, solstices, equinoxes, solar eclipses and lunar eclipses between Jan. 5, 1550 and Dec. 31, 2649 -- 23,289 celestial events in all.

### Data sources
- Datetimes of full moons, solstices, equinoxes and lunar eclipses are calculated by the [Skyfield Python library](https://rhodesmill.org/skyfield/) using NASA's [`de440.bsp`](https://rhodesmill.org/skyfield/planets.html#choosing-an-ephemeris) ephemeris file
- Solar eclipse data comes from NASA's [Five Millenium Catalog of Solar Eclipses](https://eclipse.gsfc.nasa.gov/5MCSE/5MCSEcatalog.txt)

### Output
The `compute_events.py` script generates five CSVs in the `data` folder:
- `data/solstices-and-equinoxes.csv`
- `data/lunar-eclipses.csv`
- `data/solar-eclipses.csv`
- `data/full-moons.csv`
- `data/celestial-almanac.csv`

### Put it on a Google Calendar
Also included in this repo: [A Python script](https://github.com/cjwinchester/full-moons-soltices-equinoxes-eclipses/blob/main/upload_to_calendar.py) to upload the data to a Google Calendar via API. (Turns out the combined file is too big for the browser-based CSV import option.)

[Here's a link to the public Google Calendar I made](https://calendar.google.com/calendar/u/0?cid=YmMxYWU2ZGM2YjljZGVhZTIxNzQwMzIzZGM3Yjc4NjMxYzNmZDIzNTZlMzE1NTAwNDRkZDFiNTQwNTQ3MTVhMEBncm91cC5jYWxlbmRhci5nb29nbGUuY29t), if you'd like to subscribe. Otherwise, you can run the `upload_to_calendar.py` script to populate your own -- first you'd need to save your calendar's ID as an environment variable called `ALMANAC_CAL_ID` (or [otherwise swap in your calendar ID value here](https://github.com/cjwinchester/full-moons-soltices-equinoxes-eclipses/blob/main/upload_to_calendar.py#L16)).

### Running the code
- Clone or [download/unzip](https://github.com/cjwinchester/full-moons-soltices-equinoxes-eclipses/archive/refs/heads/main.zip) this repository
- `cd` into the folder and install the dependencies (preferably into a virtual environment, using your tooling of choice): `pip install -r requirements.txt`
- `python compute_events.py` to generate the CSV files
- `python upload_to_calendar.py` to populate your own calendar (takes awhile!)
