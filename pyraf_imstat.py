"""Ross Dobson 2023-06-15, rdobson@ing.iac.es"""

import os
from astropy.io import fits
from pyraf import iraf
from pathlib import Path

# get list of image directories
img_dirs = [d for d in Path.cwd().iterdir() if d.is_dir()]

# iterate through each image directory
for img_dir in img_dirs:

    print(f"\n{img_dir}")
    
    # lists to store the names of each bias or sky file. This will get saved in the image directory, for future reference.
    bias_list = []
    sky_list = []

    # make a list of all the fits files in this directory
    fits_files = [f for f in img_dir.glob("*.fit")]
    for fits_file in fits_files:
        # open the FITS header
        hdul = fits.open(fits_file)
        try:
            obstype = hdul[0].header['OBSTYPE']
            dir_name = fits_file.parent.stem
            img_name = fits_file.name


            if obstype == "BIAS":
                print(obstype, dir_name, img_name)
                bias_list.append(img_name + "[1]")

            if obstype == "SKY":
                print(obstype, dir_name, img_name)
                sky_list.append(img_name + "[1][145:165,2033:2053]")

            else:
                print(obstype, dir_name, img_name)
        except:
            # image may not have an obstype (glance or acquisition camera etc)
            # just catch the exception and move on
            continue

    # Lets look at the bias images (if any)
    if len(bias_list) != 0:

        # Save list of the bias image names, in the image directory: biasindexYYYYMMMDD.lst
        bias_list_name = "biasindex" + dir_name + ".lst"
        bias_list_path = img_dir / bias_list_name
        with open(bias_list_path, "w") as fobj:
            print(f"Writing names of bias images to {bias_list_path}")
            for bias in bias_list:
                fobj.write(bias + "\n")  # save each image name on a new line

        # This is a bit of a mess as imstat can only operate in the current directory, whereas each image is in a child directory YYYYMMDD
        # So we need to get a list of the full path YYYYMMDD/rXXXXXXX.fit, to pass in to iraf.imstat
        # However we don't want the full path in the final results list, so we will sanitise the input before we write to the final file

        # make a python list of each image path, for imstat
        bias_img_paths = [dir_name + "/" + bias_img for bias_img in bias_list]

        # Ideally, we'd only run imstat once. But if the list of images is over 999 chars, imstat crashes. So we run one at a time.
        # However, each imstat returns two lines: the column headers and the results. So unless it is the first run, strip the header line.
        # Then, combine all the lines into one list, and save.
        bias_results = []
        for i,bias_img_path in enumerate(bias_img_paths):
            bias_imstat_result = iraf.imstat(bias_img_path, Stdout=True)
            if i == 0:
                bias_results.append(bias_imstat_result[0])
                bias_results.append(bias_imstat_result[1])
            else:
                bias_results.append(bias_imstat_result[1])
        
        bias_results_name = "bias" + dir_name + ".lst"
        bias_results_path = Path.cwd() / bias_results_name
        with open(bias_results_path, "w") as fobj:
            for i,line in enumerate(bias_results):
                if i == 0 :  # the first line is the header. We dont need to change this, so write it as is
                    fobj.write(line + "\n")
                else:  # else, we need to strip the image directory from the "name" column of the results, so split around / and take the final element, to get just the image name
                    fobj.write(line.split("/")[-1] + "\n")
                    
    # Lets look at the sky images (if any)
    if len(sky_list) != 0:

        # Save list of the sky image names, in the image directory: skyindexYYYYMMMDD.lst
        sky_list_name = "skyindex" + dir_name + ".lst"
        sky_list_path = img_dir / sky_list_name
        with open(sky_list_path, "w") as fobj:
            print(f"Writing names of sky images to {sky_list_path}")
            for sky in sky_list:
                fobj.write(sky + "\n")  # save each image name on a new line

        # This is a bit of a mess as imstat can only operate in the current directory, whereas each image is in a child directory YYYYMMDD
        # So we need to get a list of the full path YYYYMMDD/rXXXXXXX.fit, to pass in to iraf.imstat
        # However we don't want the full path in the final results list, so we will sanitise the input before we write to the final file

        # make a python list of each image path, for imstat
        sky_img_paths = [dir_name + "/" + sky_img for sky_img in sky_list]

        # Ideally, we'd only run imstat once. But if the list of images is over 999 chars, imstat crashes. So we run one at a time.
        # However, each imstat returns two lines: the column headers and the results. So unless it is the first run, strip the header line.
        # Then, combine all the lines into one list, and save.
        sky_results = []
        for i,sky_img_path in enumerate(sky_img_paths):
            print("sky sanity check:", sky_img_path)
            sky_imstat_result = iraf.imstat(sky_img_path, Stdout=True)
            if i == 0:
                sky_results.append(sky_imstat_result[0])
                sky_results.append(sky_imstat_result[1])
            else:
                sky_results.append(sky_imstat_result[1])
        
        sky_results_name = "sky" + dir_name + ".lst"
        sky_results_path = Path.cwd() / sky_results_name
        with open(sky_results_path, "w") as fobj:
            for i,line in enumerate(sky_results):
                if i == 0 :  # the first line is the header. We dont need to change this, so write it as is
                    fobj.write(line + "\n")
                else:  # else, we need to strip the image directory from the "name" column of the results, so split around / and take the final element, to get just the image name
                    fobj.write(line.split("/")[-1] + "\n")
