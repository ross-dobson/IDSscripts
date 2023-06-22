#!/usr/bin/env python3
"""Automated IRAF imstat of IDS EEV10 bias and science images.

Script to automatically run IRAF's imstat command on bias and science images
from the EEV10 detector. Imstat is run on all images with FITS header OBSTYPE
keyword value of BIAS or TARGET. Imstat runs on the entire image for bias 
images, and section [145:165,2033:2053] for science images. The script runs on
all images found in subdirectories of format YYYYMMDD (I recommend using this
script in tandem with copy_ids_fits.py).

Ross Dobson 2023-06-22
rdobson@ing.iac.es
"""

from pathlib import Path
from datetime import date
from astropy.io import fits
from pyraf import iraf

dir_results = Path.cwd() / "Results"

def main():
    if not (dir_results.exists() and dir_results.is_dir()):
        dir_results.mkdir()

    # get list of all sub directories
    list_sub_dirs = [d for d in Path.cwd().iterdir() if d.is_dir()]

    # check if the subdir is an image dir - check its name is format YYYYMMDD
    list_img_dirs = []
    for sub_dir in list_sub_dirs:
        dir_name = sub_dir.parts[-1]  # get the name of the image directory
        try:  # easiest way to check its a valid YYYYMMDD date? Try make a date!
            date(year=int(dir_name[0:4]), month=int(dir_name[4:6]),
                         day=int(dir_name[6:8]))
            list_img_dirs.append(sub_dir)
        except ValueError:
            continue  # not an image directory (probably Results or pyraf dir)

    # iterate through each image directory
    for img_dir in list_img_dirs:
        # lists to store the names of each bias or science file.
        # This will get saved in the image directory, for future reference.
        list_bias = []
        list_science = []

        # make a list of all the fits files in this directory
        list_fits_files = list(img_dir.glob("*.fit"))
        if not list_fits_files:
            continue  # if no FITS found, move on to next directory
        print(f"\nFound {len(list_fits_files)} total images in {img_dir}")

        for fits_file in list_fits_files:
            # open the FITS header
            hdul = fits.open(fits_file)
            hdr0 = hdul[0].header
            try:
                obstype = hdr0['OBSTYPE']
                name_dir = fits_file.parent.stem
                name_img = fits_file.name

                if obstype == "BIAS":
                    list_bias.append(name_img + "[1]")
                elif obstype == "TARGET":
                    list_science.append(name_img + "[1][145:165,2033:2053]")
                else:
                    continue
            except KeyError:
                # image may not have an obstype (glance or acquisition camera etc)
                # just catch the exception and move on
                continue


        # Lets look at the science images (if any)
        if list_science:
            print(f"Found {len(list_science)} science images")

            # Save list of the science image names, in the image dir: scienceindexYYYYMMMDD.lst
            name_list_science = "scienceindex" + name_dir + ".lst"
            path_list_science = img_dir / name_list_science
            with open(path_list_science, mode="w", encoding="ascii") as fobj:
                print(f"Writing names of science images to {path_list_science}")
                for science in list_science:
                    fobj.write(science + "\n")  # save each image name on a new line

            # This section is a bit of a bodge: imstat can only operate in the
            # current working directory, but each image is in a child directory
            # YYYYMMDD. So, IRAF needs the relative path YYYYMMDD/rxxxxxxx.fit, for
            # each image. However, we don't want that long path in the final imstat
            # results lists, we just want the image name rxxxxxxx.fit alone. So,
            # once we have the imstat output, we will strip the directory name from
            # each line before we write to the final list file.

            # Make list of each relative path from the working directory, for imstat
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

            # Write the imstat results to a .lst file. As mentioned above, we need
            # to strip the "NAME" column so that it is just rxxxxxxx.fit, not
            # YYYYMMDD/rxxxxxxx.fit. To do this, we split around the "/" character,
            # and only keep everything after the "/". However, we don't do this for
            # the very first line, as that is the imstat column headers, not a line
            # of results.
            name_results_science = "science" + name_dir + ".lst"
            path_results_science = dir_results / name_results_science
            with open(path_results_science, mode="w", encoding="ascii") as fobj:
                print(f"Writing imstat results for science images to {path_results_science}")
                for i,line in enumerate(list_results_science):
                    if i == 0 :  # the first line is the header. No change needed
                        fobj.write(line + "\n")
                    else:  # else, only keep everything after the "/" in the path
                        fobj.write(line.split("/")[-1] + "\n")


        # Lets look at the bias images (if any)
        if list_bias:
            print(f"Found {len(list_bias)} bias images")

            # Save list of biases, in the image directory: biasindexYYYYMMMDD.lst
            name_list_bias = "biasindex" + name_dir + ".lst"
            path_list_bias = img_dir / name_list_bias
            with open(path_list_bias, mode="w", encoding="ascii") as fobj:
                print(f"Writing names of bias images to {path_list_bias}")
                for bias in list_bias:
                    fobj.write(bias + "\n")  # save each image name on a new line

            # This section is a bit of a bodge: imstat can only operate in the
            # current working directory, but each image is in a child directory
            # YYYYMMDD. So, IRAF needs the relative path YYYYMMDD/rxxxxxxx.fit, for
            # each image. However, we don't want that long path in the final imstat
            # results lists, we just want the image name rxxxxxxx.fit alone. So,
            # once we have the imstat output, we will strip the directory name from
            # each line before we write to the final list file.

            # Make list of each relative path from the working directory, for imstat
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

            # Write the imstat results to a .lst file. As mentioned above, we need
            # to strip the "NAME" column so that it is just rxxxxxxx.fit, not
            # YYYYMMDD/rxxxxxxx.fit. To do this, we split around the "/" character,
            # and only keep everything after the "/". However, we don't do this for
            # the very first line, as that is the imstat column headers, not a line
            # of results.
            name_results_bias = "bias" + name_dir + ".lst"
            path_results_bias = dir_results / name_results_bias
            with open(path_results_bias, mode="w", encoding="ascii") as fobj:
                print(f"Writing imstat results for bias images to {path_results_bias}")
                for i,line in enumerate(list_results_bias):
                    if i == 0 :  # the first line is the header. No change needed
                        fobj.write(line + "\n")
                    else:  # else, only keep everything after the "/" in the path
                        fobj.write(line.split("/")[-1] + "\n")


        else:
            print("No bias or science images found")

if __name__ == "__main__":
    main()
