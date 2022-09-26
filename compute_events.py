import datetime
import csv

from skyfield import api as skyfieldapi, eclipselib, almanac # noqa
import requests


ts = skyfieldapi.load.timescale()

# grab the ephemeris file that covers the year range
eph = skyfieldapi.load('de440.bsp')


def get_equinox_sols(start_date, end_date):

    '''
        Get datetimes of solstices and equinoxes between start_date and end_date # noqa
        
        Ref:
            https://rhodesmill.org/skyfield/almanac.html#the-seasons
    '''

    eq_sol = []

    t, y = almanac.find_discrete(
        ts.utc(
            start_date.year,
            start_date.month,
            start_date.day,
            start_date.hour,
            start_date.minute
        ),
        ts.utc(
            end_date.year,
            end_date.month,
            end_date.day,
            end_date.hour,
            end_date.minute
        ),
        almanac.seasons(eph)
    )

    for yi, ti in zip(y, t):
        dt = ti.utc_datetime().isoformat(timespec='seconds')
        data_out = {
            'datetime': dt,
            'event_type': almanac.SEASON_EVENTS[yi],
            'all_day': True
        }
        eq_sol.append(data_out)

    return eq_sol


def get_full_moon(start_date, end_date):
    '''
        Get datetimes of full moons between start_date and end_date # noqa
        
        Ref:
            https://rhodesmill.org/skyfield/almanac.html#phases-of-the-moon
    '''

    full_moons = []

    t, y = almanac.find_discrete(
        ts.utc(
            start_date.year,
            start_date.month,
            start_date.day,
            start_date.hour,
            start_date.minute
        ),
        ts.utc(
            end_date.year,
            end_date.month,
            end_date.day,
            end_date.hour,
            end_date.minute
        ),
        almanac.moon_phases(eph)
    )

    for yi, ti in zip(y, t):
        phase = almanac.MOON_PHASES[yi]
        if phase.casefold() == 'full moon':
            dt = ti.utc_datetime().isoformat(timespec='seconds')
            data_out = {
                'datetime': dt,
                'event_type': almanac.MOON_PHASES[yi],
                'all_day': True
            }
            full_moons.append(data_out)

    return full_moons


def get_lunar_eclipses(start_date, end_date):
    '''
        Get datetimes of lunar eclipses between start_date and end_date # noqa
        
        Ref:
            https://rhodesmill.org/skyfield/almanac.html#lunar-eclipses
    '''

    lunar_eclipses = []

    t0 = ts.utc(
        start_date.year,
        start_date.month,
        start_date.day,
        start_date.hour,
        start_date.minute
    )

    t1 = ts.utc(
        end_date.year,
        end_date.month,
        end_date.day,
        end_date.hour,
        end_date.minute
    )

    t, y, details = eclipselib.lunar_eclipses(t0, t1, eph)

    for ti, yi in zip(t, y):
        dt = ti.utc_datetime().isoformat(timespec='seconds')
        data_out = {
            'datetime': dt,
            'event_type': eclipselib.LUNAR_ECLIPSES[yi] + ' lunar eclipse'
        }
        lunar_eclipses.append(data_out)

    return lunar_eclipses


def get_eclipses_solar(start_date, end_date):
    '''
        Find the datetimes of each predicted solar eclipse between two dates

        Ref:
            https://eclipse.gsfc.nasa.gov/5MCSE/5MCSEcatalog.txt
    '''

    solar_eclipses = []

    r = requests.get('https://eclipse.gsfc.nasa.gov/5MCSE/5MCSEcatalog.txt')
    lines = r.text.splitlines()

    # just want data from 1550-2649
    data = lines[8436:11047]

    # https://eclipse.gsfc.nasa.gov/SEcat5/catkey.html
    eclipse_type_map = {
        'P': 'Partial solar eclipse',
        'A': 'Annular solar eclipse',
        'T': 'Total solar eclipse',
        'H': 'Hybrid or annular/total solar eclipse'
    }

    fixed_width_map = {
        'date': slice(13, 24),
        'time': slice(26, 34),
        'eclipse_type': slice(56, 57),
        'duration': slice(-6, -1)
    }

    for line in data:
        date = line[fixed_width_map['date']]
        time = line[fixed_width_map['time']]
        date_and_time = f'{date} {time}'
        date_parsed = datetime.datetime.strptime(date_and_time, '%Y %b %d %H:%M:%S') # noqa
        date_parsed = date_parsed.replace(tzinfo=datetime.timezone.utc)
        eclipse_type = eclipse_type_map[line[fixed_width_map['eclipse_type']]]
        duration = line[fixed_width_map['duration']].strip()
        seconds, minutes = None, None
        if duration and duration != '-':
            seconds, minutes = duration.split('m')

        dt = date_parsed.isoformat(timespec='seconds')
        
        data_out = {
            'datetime': dt,
            'event_type': eclipse_type,
            'duration_minutes': minutes,
            'duration_seconds': seconds
        }
        solar_eclipses.append(data_out)

    return solar_eclipses


if __name__ == '__main__':

    min_date, max_date = (
        datetime.datetime(1550, 1, 5, 0, 0, 0),
        datetime.datetime(2649, 12, 31, 23, 59, 59)
    )

    data_map = {
        'solstices-and-equinoxes': get_equinox_sols(min_date, max_date),
        'lunar-eclipses': get_lunar_eclipses(min_date, max_date),
        'solar-eclipses': get_eclipses_solar(min_date, max_date),
        'full-moons': get_full_moon(min_date, max_date)
    }

    data_combined = []
    headers_all = set()

    for key in data_map:
        data = data_map[key]
        data_combined.extend(data)

        filepath = f'data/{key}.csv'
        print(f'Writing data for {filepath} ...')

        headers = data[0].keys()
        headers_all.update(headers)

        with open(filepath, 'w') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

    combo_filepath = 'data/celestial-almanac.csv'

    print(f'Writing {combo_filepath} ...')
    with open(combo_filepath, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers_all)
        writer.writeheader()
        writer.writerows(data_combined)
