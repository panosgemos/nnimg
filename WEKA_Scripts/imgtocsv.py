#!/usr/bin/python3

""" USAGE: imgtocsv.py (train | test) img_dir [output_dir] 
    
    This script creates an environment, appropriate for importing
    training and test sets of images into WEKA using the imageFilters
    package. This environment is comprised by a CSV file, named 
    "images-train.csv" or "images-test.csv", and a folder containing 
    symbolic links to the images, named "images-train" or "images-test"
    in the case of training and test set respectively.
    
    Training Set
    ------------
    The training set is comprised of labeled images organized in
    subfolders, named by their labels.
    
    Test Set
    --------
    The test set is a folder of images, with no other subfolder inside.
    
    File Structure
    --------------
    The CSV file's first line is a title describing the
    the columns. This is necessary in order to be read from the WEKA
    CSVLoader. The columns stored are the image filenames and their
    corresponding class. In the case of the test set, the class column
    is filled with the '?' symbol.
    
    Example of a CSV file of a training set:
    
        imgfile  , class
        img1.jpeg, CAR
        img2.jpeg, SHIP
        img3.jpeg, TRAIN
    
    Example of a CSV file of a test set:
    
        imgfile  , class
        img4.jpeg, ?
        img5.jpeg, ?
        img6.jpeg, ?
    
    The folder of symbolic links to the images is needed because the
    imageFilter package needs all the images to be inside one folder.
    The class information of each image is retrieved from the CSV file
    and not from the subfolder structure. In the test set though, the
    symbolic link folder is not necessary, because all images are inside
    one folder and therefore it is not created.
    
    The CSV and the symbolic link folder are stored in an output folder 
    which can be defined by the user. If not defined, then it is stored 
    by default in the current working directory with the name "output".
    
    Parameters
    ----------
    
    train           : indicates whether the training set of images is to
                      be imported.
                      
    test            : indicates whether the test set of images is to
                      be imported.
    
    labeled_img_dir : path of the directory that contains the subfolders
                      of the labeled images.
    output_dir      : path of the output directory
"""

import sys
import os
from enum import Enum

# Global Constants #
USAGE = "USAGE: imgtocsv.py (train | test) img_dir [output_dir]"
SYMLINK_DIR = "images"
OUTPUT_DIR = "output"
IMAGES_TRAIN_CSV = "images_train.csv"
IMAGES_TEST_CSV = "images_test.csv"
CSV_TITLE = "imgfile,class"

class Mode(Enum):
    """
    Enumeration class representing the two modes of this script: train and
    test.
    """
    TRAIN = "train"
    TEST  = "test"

def parse_args():
    """
    Parses the command line arguments and returns a tuple containing the
    mode ("train" or "test"), the input directory and the output 
    directory paths in this order.
    
    :returns: a tuple containing the mode ("train" or "test"), the input 
              directory and the output directory paths in this order.
              
    :raises ValueError: if called with illegal or wrong number of
                        arguments.
    """
    
    argvlen = len(sys.argv)

    # Argument Check
    if argvlen not in (3,4):
        raise ValueError("Wrong number of arguments")

    mode = sys.argv[1]

    # Check if legal value was passed for the first positional argument
    try:
        modeEnum = Mode(mode)
    except ValueError:
        raise ValueError('Invalid mode: "{}"'.format(mode))
        
    # Set output folder
    if argvlen == 4:
        output_dir = sys.argv[3]
    else :
        # default name of output directory
        output_dir = OUTPUT_DIR

    # directory containing the input folder (either subfolders of images
    # or just images in the case of the training or test set respectively)
    input_dir = sys.argv[2]
    
    return (modeEnum, input_dir, output_dir)

def get_subdirs(directory):
    """
    Gets the the names of the first level subdirectories of the given folder
    
    :returns: a list containing the subdirectories of the current folder.
    :raises ValueError: if there are no subfolders in the given folder
    """
    
    # Get all subdirectories of the input folder
    subdirs = [subdir for subdir in os.listdir(directory) 
                   if os.path.isdir(os.path.join(directory, subdir))]

    if len(subdirs) == 0 :
        raise ValueError("There were no subdirectories found under:\n"
                             + directory)
    
    return subdirs

def training_set_csv(input_dir):
    """
    Creates a CSV of the training set images that are stored in the given
    folder, organized in subfolders named by their label.
    
    :param input_dir: directory containing the training set images
                      organized in subfolders named by their label.
    """
    
    subdirs = get_subdirs(input_dir)
   
    # directory where the images' symbolic links will be stored
    try :
        os.mkdir(SYMLINK_DIR, 0o755)
    except FileExistsError:
        pass

    # The CSV file containing the names of the images and their class
    csvfile = open(IMAGES_TRAIN_CSV, "w")

    csvfile.write(CSV_TITLE + "\n")

    # Access the image files from their subdirectories
    for subdir in subdirs:
        subdir_path = os.path.join(input_dir, subdir)
        for img in os.listdir(subdir_path):
            img_path = os.path.join(subdir_path, img)
            if os.path.isfile(img_path):
                # write image name and its class (subdir name) to the CSV
                csvfile.write("{},{}\n".format(img, subdir))
                
                # create a symlink for current image to the symlink dir
                os.symlink(img_path, os.path.join(SYMLINK_DIR, img))

    csvfile.close()
    
def test_set_csv(input_dir):
    """
    Creates a CSV of the test set images that are stored in the given
    folder.
    
    :param input_dir: directory containing the test set images.
    """
    
    # The CSV file containing the names of the images and their class
    csvfile = open(IMAGES_TEST_CSV, "w")

    csvfile.write(CSV_TITLE + "\n")
    
    for img in sorted(os.listdir(input_dir)):
            img_path = os.path.join(input_dir, img)
            if os.path.isfile(img_path):
                # write image name and a '?' for its class to the CSV file
                csvfile.write("{},0\n".format(img))

    csvfile.close()

def run(mode, input_dir, output_dir="output"):

    """
    This function comprises the API that other Python scripts can use,
    in order to use the functionality of this script.

    :param mode: Can be either Mode.TRAIN or Mode.TEST indicating whether to
                 process the training or the test set.
    :param input_dir: The path of the input directory that contains the images.
    :param output_dir: The output directory where to put the CSV files and
                       the folder of the symlinks to the images (in the case
                      of the training set
    only).
    """

    # Check if input directory exists
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(input_dir + " is not a directory")
    input_dir = os.path.abspath(input_dir)  # convert to absolute path

    # Create the output folder if it does not exist
    try:
        os.mkdir(output_dir, 0o755)
    except FileExistsError:
        pass

    # Change current working directory to the output directory
    os.chdir(output_dir)

    if mode == Mode.TRAIN:
        training_set_csv(input_dir)
    elif mode == Mode.TEST:
        test_set_csv(input_dir)


def cli_run():

    """
    Runs this script in a cli environment.
    """

    # Parse arguments
    mode, input_dir, output_dir = parse_args()

    run(mode, input_dir, output_dir)


if __name__ == "__main__":
    try:
        cli_run()
    except Exception as ex:
        print(ex)
        print(USAGE)
