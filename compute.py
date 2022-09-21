from datetime import date, datetime, timedelta
import time
import csv

import ephem
import requests


min_date, max_date = (
    datetime(1700, 1, 1, 0, 0, 0),
    datetime(2100, 12, 31, 23, 59, 59)
)


def get_equinoxes_solstices(min_date, max_date):

    print()
    print('Grabbing equinoxes and solstices ...')

    equinoxes, solstices = [], []

    curr_date = min_date

    while curr_date <= max_date:
        eq = ephem.next_equinox(curr_date).datetime()
        if eq <= max_date:
            equinoxes.append(eq)
        curr_date = eq

    curr_date = min_date

    while curr_date <= max_date:
        eq = ephem.next_solstice(curr_date).datetime()
        if eq <= max_date:
            solstices.append(eq)
        curr_date = eq

    return (equinoxes, solstices)


def get_full_moon(min_date, max_date):

    print()
    print('Grabbing full moons ...')

    full_moons = []
    
    for year in range(min_date.year, max_date.year+1):
        url = f'https://aa.usno.navy.mil/api/moon/phases/year?year={year}'

        r = requests.get(url)
        r.raise_for_status()

        print(url)

        data = r.json()['phasedata']
        
        for day in data:
            if day['phase'].casefold() == 'full moon':
                hours, minutes = [int(x) for x in day['time'].split(':')]
                
                d = datetime(
                    day['year'],
                    day['month'],
                    day['day'],
                    hours,
                    minutes
                )

                full_moons.append(d)

        time.sleep(1)

    return full_moons


def get_eclipses_lunar(min_date, max_date):

    print()
    print('Grabbing lunar eclipses ...')

    eclipses = []

    # https://gist.github.com/priyadi/e5322666248ee22a81d8e56e84fe1bcb
    # initialize Moon, Sun & observer
    moon = ephem.Moon()
    sun = ephem.Sun()
    observer = ephem.Observer()
    observer.elevation = -6371000
    observer.pressure = 0

    # loop every hour
    while min_date <= max_date:
        observer.date = min_date

        # computer the position of the sun and the moon with respect to the observer  # noqa
        moon.compute(observer)
        sun.compute(observer)

        # calculate the separation between the moon and the sun, convert
        # it from radians to degrees, subtract it by 180°.
        # this is basically the separation of the moon from the Earth's
        # center of umbra
        sep = abs((float(ephem.separation(moon, sun)) / 0.01745329252) - 180)

        # eclipse occurs if the separation is less than 0.9°.
        # this should detect all total and partial eclipses, but is
        # hit-and-miss for penumbral eclipses.
        # the number is hardcoded for simplicity. for accuracy it should
        # be computed from the distance to the Sun and the Moon.
        if sep < 0.9:
            eclipses.append(min_date)
            # an eclipse cannot happen more than once in a day,
            # so we skip 24 hours when an eclipse is found
            min_date += timedelta(days=1)
        else:
            # advance an hour if eclipse is not found
            min_date += timedelta(hours=1)

    return eclipses


def get_eclipses_solar(start_year, end_year):

    print()
    print('Grabbing solar eclipses ...')

    eclipses = []

    for year in range(start_year, end_year+1):

        url = f'https://aa.usno.navy.mil/api/eclipses/solar/year?year={year}'

        r = requests.get(url)

        r.raise_for_status()

        print(url)

        data = r.json()['eclipses_in_year']

        eclipses.extend([datetime(x['year'], x['month'], x['day'], 0, 0) for x in data])  # noqa

        time.sleep(1)

    return eclipses


if __name__ == '__main__':
    full_moon = get_full_moon(min_date, max_date)
    equinoxes, solstices = get_equinoxes_solstices(min_date, max_date)
    ecl_solar = get_eclipses_solar(1800, 2050)
    ecl_lunar = get_eclipses_lunar(min_date, max_date)

    phenomena = {
        'lunar_eclipse': ecl_lunar,
        'solar_eclipse': ecl_solar,
        'full_moon': full_moon,
        'equinoxes': equinoxes,
        'solstices': solstices
    }

    headers = [
        'datetime',
        'year',
        'month',
        'day',
        'hour',
        'minutes',
        'phenomena'
    ]

    with open('celestial-calendar.csv', 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers)
        writer.writeheader()

        for key in phenomena:
            data = phenomena[key]
            for d in data:
                data_to_write = [
                    d.isoformat(),
                    d.year,
                    d.month,
                    d.day,
                    d.hour,
                    d.minute,
                    key
                ]
                writer.writerow(dict(zip(headers, data_to_write)))    
