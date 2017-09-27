#!/usr/bin/python3

""" USAGE: wekatokaggle.py (csv | xml) predictions image_names [output]
    
    This script converts the given weka output predictions to the format
    that is acceptable for the "The Nature Conservancy Fisheries 
    Monitoring" competition.
    
    Parameters:
    
    (csv | xml) : Format of the weka output predictions.
    predictions : Weka output predictions.
    image_names : Names of the images seperated by newline.
                  The order of the names must correspond to the order of
                  the output predictions.
    output      : Path of the CSV file containing the predictions in the
                  format that is acceptable by the "The Nature Conservancy 
                  Fisheries Monitoring" competition.
                  If not defined, it is stored under the current working
                  directory with the name "output.csv".
"""

import sys
import os
from enum import Enum

# Global Constants #
USAGE = (
    "USAGE: wekatokaggle.py (csv | xml) predictions image_names [output]"
    )

OUTPUT = "output.csv"
CSV_COLS = "image","ALB","BET","DOL","LAG","NoF","OTHER","SHARK","YFT"
CSV_COLS_MAP = {label:index for index,label in enumerate(CSV_COLS)}
CSV_TITLE = ",".join(CSV_COLS)

class Mode(Enum):
    """
    Enumeration class representing the two modes of this script: csv and
    xml.
    """
    CSV = "csv"
    XML = "xml"

def parse_args():
    """
    Parses the command line arguments and returns a tuple containing the
    mode ("train" or "test"), the input directory and the output 
    directory paths in this order.
    
    :returns: a tuple containing the mode ("train" or "test"), the Weka
              predictions path, the image names path and the output
              path in this order.
              
    :raises ValueError: if called with illegal or wrong number of
                        arguments.
    """
    
    argvlen = len(sys.argv)

    # Argument Check
    if argvlen not in (4,5) :
        raise ValueError("Wrong number of arguments")

    mode = sys.argv[1]

    # Check if legal value was passed for the first positional argument
    try:
        modeEnum = Mode(mode)
    except ValueError:
        raise ValueError('Invalid mode: "{}"'.format(mode))
    
    predictions = sys.argv[2]
    
    image_names = sys.argv[3]
    
    paths = [ path for path in (predictions,image_names) 
                       if not os.path.isfile(predictions)]
    
    if paths: raise ValueError(", ".join(paths))

       
    # Set output
    if argvlen == 5:
        output = sys.argv[4]
    else:
        # default name of output directory
        output = OUTPUT
  
    
    return (modeEnum, predictions, image_names, output)
    
def parse_image_names(image_names):
    """
    Parses the image names given the path of the file that holds them.
    
    :param image_names: path of the image names file
    
    :returns: a list of the parsed image names
    """
    
    with open(image_names) as f:
        lines = f.readlines()
    return lines

def parse_predictions_csv(predictions):
    """
    Parses the Weka CSV formatted output predictions.
    
    :param predictions: path of the weka output predictions
    
    :returns: A list containing the class predictions
    """
    
    predictions = []
    
    with open(predictions) as f:
        # for each line in the file, get the third value (prediction)
        for line in f:
            val3 = line.split(",")[2]
            
            # from the prediction, get the second value (label)
            label = label.split(":")[1]
            
            predictions.append(label)
        
       
    del predictions[0]  # delete CSV title
    
    return predictions 
        
def image_names_iter(image_names_file):
    """
    Iterates over the names of the images that are stored in the
    given file.
    
    :param image_names_file: file containing the image names
    
    :returns: a generator object for iterating through the image names
    """
    
    for line in image_names_file:
        yield line.strip()

def predictions_csv_iter(predictions_file):
    """
    Iterates over the lines of the Weka CSV formatted output
    predictions file, fetching the prediction class of each instance.
    The CSV title, if any, must be discarded beforehand.
    
    :param predictions_file: file containing the Weka CSV formatted
                             output predictions.
    
    :returns: a generator object for iterating through the image names
    """
    
    for line in predictions_file:
        val3 = line.split(",")[2]
        
        # from the prediction, get the second value (label)
        label = val3.split(":")[1]
        
        yield label

def create_kaggle_file(title, output_path):
    """
    Creates a file template that conforms to the the "The Nature 
    Conservancy Fisheries Monitoring" competition output predictions
    format.
    
    :param title: Title of the CSV that contains the image name and
                  the predictied labels.
    :param output_path: path of the file template to be output.
    
    :returns: the file object of the created file.
    """
    
    output = open(output_path, "w")
    output.write(title)
    
    return output

def to_kaggle_record(csv_cols, image_name, prediction):
    """
    Creates a record that conforms to the "The Nature Conservancy
    Fisheries Monitoring" competition.
    
    :param csv_cols:   record columns
    :param image_name: name of the image
    :param prediction: prediction class
    
    :returns: the record as a list object
    """
    
    # initialize record to a list of zeros
    record = [0] * len(CSV_COLS)
    
    # set first record column to the image name
    record[0] = image_name
    
    record[CSV_COLS_MAP[prediction]] = 1
    
    return record

def weka_csv_to_kaggle(image_names_path, predictions_path, output_path):
    """
    Parses the Weka CSV formatted output predictions and given the
    names of the images of the predictions in a separate file,
    it exports a file that is acceptable for the "The Nature 
    Conservancy Fisheries Monitoring" competition.
    
    :param image_names_path: path containing the image names
    :param predictions_path: path containing the Weka CSV formatted
                             output predictions.
    :param output_path:      path of the output file
    """
    
    # open files containining the images names and the Weka predictions
    with open(image_names_path) as (image_names_file
      ), open(predictions_path) as (predictions_file
      ), open(output_path, "w") as (output_file):
        
       
        output_file.write(CSV_TITLE + "\n")
        
        predictions_file.readline() # discard first (title) line
        
        # iterate over each line of the file synchronously
        for image_name, prediction in zip(
                image_names_iter(image_names_file),
                predictions_csv_iter(predictions_file)
            ):
            
            # construct the file record
            record = to_kaggle_record(CSV_COLS, image_name, prediction)
            
            # write file record to output file
            output_file.write(",".join(map(str, record)) + "\n")
            
def run():
    mode, predictions, image_names, output = parse_args()
    if mode == Mode.CSV:
        weka_csv_to_kaggle(image_names, predictions, output)
    elif mode == Mode.XML:
        raise NotImplementedError

   
if __name__ == "__main__":
    try:
        run()
    except Exception as ex:
        print(ex)
        print(USAGE)
