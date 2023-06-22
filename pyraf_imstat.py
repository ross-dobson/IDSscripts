"""Automatic IRAF analysis of bias and science images.

Ross Dobson 2023-06-15, rdobson@ing.iac.es
"""

import os
from astropy.io import fits
from pyraf import iraf
from pathlib import Path
from datetime import date

dir_results = Path.cwd() / "Results"
if not (dir_results.exists() and dir_results.is_dir()):
    dir_results.mkdir()

# get list of image directories
list_dirs = [d for d in Path.cwd().iterdir() if d.is_dir()]

# iterate through each image directory
for img_dir in list_dirs:
    # lists to store the names of each bias or science file.
    # This will get saved in the image directory, for future reference.
    list_bias = []
    list_science = []

    # make a list of all the fits files in this directory
    list_fits_files = list(img_dir.glob("*.fit"))
    if not list_fits_files:
        continue  # if no FITS found, move on to next directory
    print(f"\nLooking in {img_dir}")

    for fits_file in list_fits_files:
        # open the FITS header
        hdul = fits.open(fits_file)
        hdr0 = hdul[0].header
        try:
            obstype = hdr0['OBSTYPE']
            name_dir = fits_file.parent.stem
            name_img = fits_file.name

            if obstype == "BIAS":
                print(obstype, name_img)
                list_bias.append(name_img + "[1]")
            elif obstype == "TARGET":
                print(obstype, name_img)
                list_science.append(name_img + "[1][145:165,2033:2053]")
            else:
                print(obstype, name_img)
        except KeyError:
            # image may not have an obstype (glance or acquisition camera etc)
            # just catch the exception and move on
            continue


    # Lets look at the science images (if any)
    if list_science:

        # Save names of science images in img dir as scienceindexYYYYMMMDD.lst
        name_list_science = "scienceindex" + name_dir + ".lst"
        path_list_science = img_dir / name_list_science
        with open(path_list_science, "w") as fobj:
            print(f"Writing names of science images to {path_list_science}")
            for science in list_science:
                fobj.write(science + "\n")  # save each image name on a new line

        # make a python list of each image path, for imstat
        list_paths_science = [name_dir + "/" + name_science for name_science in list_science]

        # Ideally, we'd only run imstat once. But if the list of images is over
        # 999 chars, imstat crashes. So we run one image at a time. However,
        # each run of imstat returns two lines: the column headers and the
        # results for that one image. So, unless it is the first run, strip
        # the header line from the output. Then, combine all the lines into one
        # list, and save to the results directory.
        list_results_science = []
        for i,path_science in enumerate(list_paths_science):
            imstat_result_science = iraf.imstat(path_science, Stdout=True)
            if i == 0:
                list_results_science.append(imstat_result_science[0])
                list_results_science.append(imstat_result_science[1])
            else:
                list_results_science.append(imstat_result_science[1])

        # This is a bit of a mess: imstat can only operate in the current
        # working directory, but each image is in a child directory YYYYMMDD.
        # So, we need to get a list of the full path YYYYMMDD/rxxxxxxx.fit, to
        # pass in to iraf.imstat. However, we don't want the full path in the
        # final results lists, just the image name alone, so we will sanitise
        # the input and strip the path before we write to the final list file.
        name_results_science = "science" + name_dir + ".lst"
        path_results_science = dir_results / name_results_science
        with open(path_results_science, "w") as fobj:
            print(f"Writing results of science images to {path_results_science}")
            for i,line in enumerate(list_results_science):
                if i == 0:
                    fobj.write(line + "\n")
                else:
                    fobj.write(line.split("/")[-1] + "\n")


    # Lets look at the bias images (if any)
    if list_bias:

        # Save list of the bias image names, in the image directory: biasindexYYYYMMMDD.lst
        name_list_bias = "biasindex" + name_dir + ".lst"
        path_list_bias = img_dir / name_list_bias
        with open(path_list_bias, "w") as fobj:
            print(f"Writing names of bias images to {path_list_bias}")
            for bias in list_bias:
                fobj.write(bias + "\n")  # save each image name on a new line

        # This is a bit of a mess as imstat can only operate in the current
        # working directory, but each image is in a child directory YYYYMMDD.
        # So, we need to get a list of the full path YYYYMMDD/rxxxxxxx.fit, to
        # pass in to iraf.imstat. However, we don't want the full path in the
        # final results lists, just the image name alone, so we will sanitise
        # the input and strip the path before we write to the final list file.

        # make a python list of each image path, for imstat
        list_paths_bias = [name_dir + "/" + name_bias for name_bias in list_bias]

        # Ideally, we'd only run imstat once. But if the list of images is over
        # 999 chars, imstat crashes. So we run one image at a time. However,
        # each run of imstat returns two lines: the column headers and the
        # results for that one image. So, unless it is the first run, strip
        # the header line from the output. Then, combine all the lines into one
        # list, and save to the results directory.
        list_results_bias = []
        for i,path_bias in enumerate(list_paths_bias):
            imstat_result_bias = iraf.imstat(path_bias, Stdout=True)
            if i == 0:
                list_results_bias.append(imstat_result_bias[0])
                list_results_bias.append(imstat_result_bias[1])
            else:
                list_results_bias.append(imstat_result_bias[1])

        name_results_bias = "bias" + name_dir + ".lst"
        path_results_bias = dir_results / name_results_bias
        with open(path_results_bias, "w") as fobj:
            print(f"Writing results of bias images to {path_results_bias}")
            for i,line in enumerate(list_results_bias):
                if i == 0 :  # the first line is the header. We dont need to change this, so write it as is
                    fobj.write(line + "\n")
                else:  # else, we need to strip the image directory from the "name" column of the results, so split around / and take the final element, to get just the image name
                    fobj.write(line.split("/")[-1] + "\n")


    else:
        print(f"No bias or science images found")
