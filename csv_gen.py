# Python program to convert
# JSON file to CSV


import json
import sys
import csv
import pdb
import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers

csv.field_size_limit(sys.maxsize)

# Opening JSON file and loading the data
# into the variable data
#  with open('data.json') as json_file:
    #  data = json.load(json_file)

#  employee_data = data['emp_details']

# now we will open a file for writing
data_file = open('data_file.csv', 'w')

# create the csv writer object
csv_writer = csv.writer(data_file)

shas = []

with open('running/shas', 'r') as filehandle:
    for line in filehandle:
        # remove linebreak which is the last character of the string
        currentPlace = line[:-1]

        # add item to the list
        shas.append(currentPlace)

print(shas)

def keras():
    dataframe = pd.read_csv('parsed_testing.csv')
    val_dataframe = dataframe.sample(frac=0.2, random_state=1337)
    train_dataframe = dataframe.drop(val_dataframe.index)

    print(
        "Using %d samples for training and %d for validation"
        % (len(train_dataframe), len(val_dataframe))
    )

    train_ds = dataframe_to_dataset(train_dataframe)
    val_ds = dataframe_to_dataset(val_dataframe)

def dataframe_to_dataset(dataframe):
    dataframe = dataframe.copy()
    labels = dataframe.pop("target")
    ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
    ds = ds.shuffle(buffer_size=len(dataframe))
    return ds

def parse_test_csv_into_data_csv():
    # Writing headers of CSV file
    testing_csv = open('testing.csv', 'r')
    parsed_tests_file = open('parsed_testing.csv', 'w', newline='')
    parsed_tests = csv.writer(parsed_tests_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    testing_csv_reader = csv.reader(testing_csv, delimiter=',', quotechar='|')

    count = 0
    # Strips the newline character
    for row in testing_csv_reader:
        if count == 0:
            parsed_tests.writerow(['sha', 'code', 'message', 'total', 'assertions', 'failures', 'fails'])
            count += 1
            continue

        diff = open(f'running/{row[0]}/kegmeister/diff', 'r')

        test_json = json.loads(json.loads(row[1]))
        status = test_json['status']
        parsed_tests.writerow([row[0], status.get('code'), status.get('message', 'No message'), test_json['statistics']['total'], test_json['statistics']['assertions'], test_json['statistics']['failures'], test_json['fails']])

def create_test_csv():
    count = 0
    error_count = 0
    brackets_count = 0
    open_bracket_count = 0
    fixed_string = ""

    testing_csv = open('testing.csv', 'w', newline='')
    testwriter = csv.writer(testing_csv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    testwriter.writerow(['sha', 'test_results'])

    for sha in shas:
        try:
            test_result = open(f'running/{sha}/kegmeister/test/test_results.json', 'r')
            results = test_result.read()
            reversed_results = results[::-1]
            start_index = reversed_results.find("}")
            brackets_count = 0
            total_brackets = 0

            for ri, char in enumerate(reversed_results):
                if (char == "}"):
                    brackets_count += 1
                    total_brackets += 1
                if (char == "{"):
                    brackets_count -= 1
                    total_brackets += 1

                if (total_brackets > 0 and brackets_count == 0):
                    fixed_string = reversed_results[start_index:ri + 1][::-1]
                    break

            if(len(fixed_string) > 0):
                testwriter.writerow([sha, json.dumps(fixed_string)])
                count += 1
        except (ValueError, FileNotFoundError) as e:
            error_count += 1
            print(e)
            print("Skipped")

    #  if count == 0:

        #  open(f'running/{sha}/kegmeister/test/test_result.json')
        #  Writing headers of CSV file
        #  header = emp.keys()
        #  csv_writer.writerow(header)
        #  count += 1

    #  Writing data of CSV file
    #  csv_writer.writerow(emp.values())

    data_file.close()
    print(f'Actual count {count}')
    print(f'Error count {error_count}')

parse_test_csv_into_data_csv()
