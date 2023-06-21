"""Ross Dobson 2023-06-15, rdobson@ing.iac.es"""

import sys
from datetime import date, timedelta

if len(sys.argv) != 3:
    raise Exception("Usage: get_ids_fit.py detector obstype YYYYMMDD")

arg_detector = sys.argv[1]
arg_obstype = sys.argv[2]
arg_date = sys.argv[3]


def date_range_list(start_date, end_date):
    # Return list of datetime.date objects (inclusive) between start_date and end_date (inclusive).
    date_list = []
    curr_date = start_date
    while curr_date <= end_date:
        date_list.append(curr_date)
        curr_date += timedelta(days=1)
    return date_list

start_date = date(year=int(start_date_string[0:4]), month=int(start_date_string[4:6]), day=int(start_date_string[6:8]))
stop_date = date(year=int(stop_date_string[0:4]), month=int(stop_date_string[4:6]), day=int(stop_date_string[6:8]))
date_list = date_range_list(start_date, stop_date)

#for d in date_list:
#    print(d.strftime("%Y%m%d"))

# step 2: make a directory for this day. copy all the fits files into it
from pathlib import Path
import shutil

obsdata_inta = Path("/obsdata/inta")

for d in date_list:
    d_str = d.strftime("%Y%m%d")
    print(f"\n{d_str}")

    # find corresponding day's folder on INT system
    todays_INT_path = obsdata_inta / d_str
    print("DEBUG INT path:", todays_INT_path)

    # check that INT folder exists
    if not Path.exists(todays_INT_path):
        raise Exception(f"INT path {todays_INT_path} not found")

    # make a list of fit files in the INT folder
    todays_INT_fits = list(todays_INT_path.glob("*.fit"))

    # check INT folder is not empty. If empty, move on to tomorrow
    if len(todays_INT_fits) == 0:
        print(f"No .fit files in {todays_INT_fits}, skipping this day")
        continue

    # make a working directory for this date's fits file
    todays_dir = Path.cwd() / d_str
    try:
        todays_dir.mkdir()
        print(f"Creating dir {todays_dir}")
    except FileExistsError:
        print(f"{todays_dir} already exists")

    # copy the fits from INT to local home
    for INT_fit_file in todays_INT_fits:
        local_fit_file = todays_dir/INT_fit_file.name
        print("Copying", INT_fit_file, "to", local_fit_file)
        shutil.copyfile(INT_fit_file, local_fit_file)
