"""Ross Dobson 2023-06-20, rdobson@ing.iac.es"""

import sys
from datetime import date, timedelta
from pathlib import Path
import shutil
from astropy.io import fits

path_obsdata_inta = Path("/obsdata/inta")

# Step 1: Check command-line arguments
if len(sys.argv) != 4:
    print("Usage: get_ids_fit.py detector obstype YYYYMMDD")
    sys.exit(1)

if not (sys.argv[1] =="EEV10" or sys.argv[1] =="REDPLUS2" or sys.argv[1] =="BOTH"):
    raise ValueError("Detector type can be EEV10, RED+2 or BOTH")
arg_detector = sys.argv[1]

if not (sys.argv[2] == "ARC" or sys.argv[2] == "BIAS" or sys.argv[2] == "DARK"
    or sys.argv[2] == "FLASH" or sys.argv[2] == "FLAT" or sys.argv[2] == "SKY"
    or sys.argv[2] == "TARGET" or sys.argv[2] == "ALL"):
    raise ValueError("Obstype can be ARC, BIAS, DARK, FLASH, FLAT, SKY, TARGET or ALL.")
arg_obstype = sys.argv[2]

if not (sys.argv[3] == "ALL"):
    bool_all_dates = False
    arg_date = sys.argv[3]
    try:
        yyyymmdd = date(year=int(arg_date[0:4]), month=int(arg_date[4:6]), day=int(arg_date[6:8]))
    except:
        raise ValueError("Date can be in format YYYYMMDD, or ALL")
else:
    arg_date = sys.argv[3]
    bool_all_dates = True

print(f"Requested image types: \nDetector: {arg_detector} \nObstype: {arg_obstype} \nDate: {arg_date}")

# Step 2: get list of valid fits

def get_list_of_fits(day, detector, obstype):
    """docstring lolololol"""
    list_fits_final = []
    path_int_yyyymmdd = path_obsdata_inta / day
    if not Path.exists(path_int_yyyymmdd):
        raise Exception(f"Dir {path_int_yyyymmdd} not found")
    print(f"\nLooking in {path_int_yyyymmdd}")

    # get list of all .fit file in the folders
    list_of_all_fits = list(path_int_yyyymmdd.glob("*.fit"))

    # get list of the .fit that match the requested detector and obstype
    for f in list_of_all_fits:
        hdul = fits.open(f)
        hdr0 = hdul[0].header
        if not hdr0['INSTRUME'] == "IDS":
            continue
        hdr0_obstype = hdr0['OBSTYPE']
        hdr0_detector = hdr0['DETECTOR']

        if arg_obstype == "ALL" or arg_obstype == hdr0_obstype:
            if arg_detector == "BOTH":
                if hdr0_detector == "REDPLUS2" or hdr0_detector == "EEV10":
                    list_fits_final.append(f)
            elif arg_detector == hdr0_detector:
                list_fits_final.append(f)

    if len(list_fits_final) == 0:
        print(f"No fits files matching detector {detector}, obstype {obstype} found for {day}")
        return
    else:
        print(f"Found {len(list_fits_final)} fits files matching detector {detector}, obstype {obstype} for day {day}")

    # make a directory to store this date's fits files
    path_cwd_yyyymmdd = Path.cwd() / day
    try:
        path_cwd_yyyymmdd.mkdir()
        print(f"Creating dir {path_cwd_yyyymmdd}")
    except FileExistsError:
        print(f"{path_cwd_yyyymmdd} already exists")

    # copy the fits files from /obsdata/inta/yyyymmdd to the ./yyyymmdd directory
    for f in list_fits_final:
        intf = path_int_yyyymmdd / f.name
        cwdf = path_cwd_yyyymmdd / f.name
        if not cwdf.exists():
            print(f"Copying {intf} to {cwdf}")
            shutil.copyfile(intf, cwdf)
        else:
            print(f"File {cwdf} already exists")
    return

if not bool_all_dates:
    get_list_of_fits(arg_date, arg_detector, arg_obstype)
    sys.exit(0)
elif bool_all_dates:
    # List all the directories in /obsdata/inta. From the paths, get the dir
    # name - this is in format yyyymmdd, so we can pass this into the function
    # as the day argument. We don't just glob for **/*.fit as it would be much
    # hard to copy in to (and if needed, mkdir) the local yyyymmdd directory.
    list_of_int_dirs = [x for x in path_obsdata_inta.iterdir() if x.is_dir()]
    list_days = [d.parts[-1] for d in list_of_int_dirs]
    for day in list_days:
        get_list_of_fits(day, arg_detector, arg_obstype)
    sys.exit(0)

sys.exit(1)
