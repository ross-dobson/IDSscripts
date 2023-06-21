"""Ross Dobson 2023-06-15, rdobson@ing.iac.es"""

import sys
from datetime import date, timedelta
from pathlib import Path
import shutil

obsdata_inta = Path("/obsdata/inta")

# 1: Check command-line arguments
if len(sys.argv) != 4:
    print("Usage: get_ids_fit.py detector obstype YYYYMMDD")
    sys.exit(1)

if not (sys.argv[1] =="EEV10" or sys.argv[1] =="REDPLUS2" or sys.argv[1] =="BOTH"):
    raise ValueError("Detector type can be EEV10, RED+2 or BOTH")
arg_detector = sys.argv[1]

if not (sys.argv[2] == "ARC" or sys.argv[2] == "BIAS" or sys.argv[2] == "DARK"
    or sys.argv[2] == "FLASH" or sys.argv[2] == "FLAT" or sys.argv[2] == "SKY"
    or sys.argv[2] == "TARGET"):
    raise ValueError("Obstype can be ARC, BIAS, DARK, FLASH, FLAT, SKY, TARGET or ALL.")
arg_obstype = sys.argv[2]

if not (sys.argv[3] == "ALL"):
    bool_all_dates = False
    try:
        arg_date = sys.argv[3]
        yyyymmdd = date(year=int(arg_date[0:4]), month=int(arg_date[4:6]), day=int(arg_date[6:8]))
    except:
        raise ValueError("Date can be in format YYYYMMDD, or ALL")
else:
    arg_date = sys.argv[3]
    bool_all_dates = True


print(sys.argv)
print(arg_detector, arg_obstype, arg_date)
sys.exit(0)

# step 2: make a directory for this day. copy all the fits files into it

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
