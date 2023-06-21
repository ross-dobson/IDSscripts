#!/usr/bin/env python3

"""Copy IDS files from /obsdata/inta for given detector, obstype and day.

Script to automate copying IDS files from /obsdata/inta. You can choose
the detector type (REDPLUS2, EEV10, or BOTH detectors), the observation
type (ARC, BIAS, DARK, FLASH, FLAT, SKY, TARGET, or choose ALL types),
and the date (in format YYYYMMDD, or you can check ALL folders).

Usage: python3 copy_ids_fit.py DETECTOR OBSTYPE YYYYMMDD

Ross Dobson 2023-06-21
rdobson@ing.iac.es
"""

import sys
from datetime import date
from pathlib import Path
import shutil
from astropy.io import fits

path_obsdata_inta = Path("/obsdata/inta")

def copy_requested_fits(day, detector, obstype):
    """Copies IDS files for a given day, detector and obstype.

    Files from /obsdata/inta/yyyymmdd will be copied to ./yyyymmdd,
    creating the directory if it doesn't already exist.

    Args:
      day:
        String of format YYYYMMDD.
      detector:
        String matching the FITS header keyword 'DETECTOR', value EEV10 or
        REDPLUS2.
      obstype:
        String matching the FITS header keyword 'OBSTYPE', value ARC, BIAS,
        DARK, FLASH, SKY, TARGET.

    Returns:
      None

    Raises:
      FileNotFoundError: if /obsdata/inta/yyyymmdd not found.

    Notes:
      Will not overwrite existing file ./yyyymmdd/rXXXXXXX.fit if it exists.
      This method only exists so that it can be called repeatedly if multiple
      days were requested. I wouldn't call it outside of this script.
    """
    list_fits_final = []
    path_int_yyyymmdd = path_obsdata_inta / day
    if not Path.exists(path_int_yyyymmdd):
        raise FileNotFoundError(f"Dir {path_int_yyyymmdd} not found")
    print(f"\nLooking in {path_int_yyyymmdd}")

    # get list of all .fit file in the folders
    list_of_all_fits = list(path_int_yyyymmdd.glob("*.fit"))

    # get list of the .fit that match the requested detector and obstype
    for f in list_of_all_fits:
        hdul = fits.open(f)
        hdr0 = hdul[0].header

        # Check it is an IDS image
        try:
            hdr0_instrume = hdr0["INSTRUME"]
        except:
            print("DEBUG no hdr0 instrume", f)
            continue  # probably glance, scratch, AG0 image, ignore
        if not hdr0_instrume == "IDS":
            print(f"{f}: instrument type {hdr0_instrume}, skipping")
            continue  # probably WFC image (or maybe visitor image), ignore

        # check it matches Obstype and Detector
        hdr0_obstype = hdr0["OBSTYPE"]
        hdr0_detector = hdr0["DETECTOR"]
        print(f"{f}, requested obstype {obstype} detector {detector}, found {hdr0_obstype} {hdr0_detector}")
        if obstype in ("ALL", hdr0_obstype):
            if detector == "BOTH":
                if hdr0_detector in ("REDPLUS2", "EEV10"):
                    list_fits_final.append(f)
            elif detector == hdr0_detector:
                list_fits_final.append(f)

    if not list_fits_final:
        print(f"No fits files matching detector {detector}, obstype {obstype} "
              f"found for {day}")
        return
    else:
        print(f"Found {len(list_fits_final)} fits files matching "
              f"detector {detector}, obstype {obstype} for day {day}")

    # make a directory to store this date's fits files, at ./yyyymmdd
    path_cwd_yyyymmdd = Path.cwd() / day
    try:
        path_cwd_yyyymmdd.mkdir()
        print(f"Creating dir {path_cwd_yyyymmdd}")
    except FileExistsError:
        print(f"{path_cwd_yyyymmdd} already exists")

    # copy the fits files from /obsdata/inta/yyyymmdd to ./yyyymmdd
    for f in list_fits_final:
        intf = path_int_yyyymmdd / f.name
        cwdf = path_cwd_yyyymmdd / f.name
        if not cwdf.exists():
            print(f"Copying {intf} to {cwdf}")
            shutil.copyfile(intf, cwdf)
        else:
            print(f"File {cwdf} already exists")
    return

def main():
    # Step 1: Check command-line arguments
    if len(sys.argv) != 4:
        print("Usage: get_ids_fit.py detector obstype YYYYMMDD")
        sys.exit(1)

    if sys.argv[1] not in ("EEV10", "REDPLUS2", "BOTH"):
        raise ValueError("Detector type can be EEV10, REDPLUS2 or BOTH")
    arg_detector = sys.argv[1]

    if sys.argv[2] not in ("ARC", "BIAS", "DARK", "FLASH", "FLAT", "SKY", "TARGET",
                           "ALL"):
        raise ValueError("Obstype can be ARC, BIAS, DARK, FLASH, FLAT, SKY, TARGET"
        " or ALL.")
    arg_obstype = sys.argv[2]

    if not sys.argv[3] == "ALL":
        bool_all_dates = False
        arg_date = sys.argv[3]
        try:
            # easy way to check it's a valid ISO8601(ish) date: try make a datetime
            date(year=int(arg_date[0:4]), month=int(arg_date[4:6]),
                 day=int(arg_date[6:8]))
        except Exception as exc:
            raise ValueError("Date can be in format YYYYMMDD, or ALL") from exc
    else:
        arg_date = sys.argv[3]
        bool_all_dates = True

    print(f"Requested image types: \n"
          f"Detector: {arg_detector} \n"
          f"Obstype: {arg_obstype} \n"
          f"Date: {arg_date}\n")

    if not bool_all_dates:
        print("DEBUG1")
        copy_requested_fits(arg_date, arg_detector, arg_obstype)
        sys.exit(0)
    elif bool_all_dates:
        print("DEBUG2")
        # List all the directories in /obsdata/inta. From the paths, get the dir
        # name - this is in format yyyymmdd, so we can pass this into the function
        # as the day argument. We don't just glob for **/*.fit as it would be much
        # harder to copy in to (and if needed, mkdir) the local yyyymmdd directory.
        list_of_int_dirs = [x for x in path_obsdata_inta.iterdir() if x.is_dir()]
        print("DEBUG3", list_of_int_dirs)
        list_days = [d.parts[-1] for d in list_of_int_dirs]
        print("DEBUG4", list_days)
        for yyyymmdd in list_days:
            print("DEBUG5", yyyymmdd)
            if len(yyyymmdd) == 8:  # check dir name is yyyymmdd, not e.g. config
                print("DEBUG6")
                copy_requested_fits(yyyymmdd, arg_detector, arg_obstype)
    return

if __name__ == "__main__":
    main()
