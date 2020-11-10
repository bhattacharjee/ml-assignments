#!/usr/local/bin/python3

import numpy as np
import argparse

g_normalize_to_zero_mean_and_unit_variance = False
g_scale_between_zero_and_one = True

def read_csv(filename:str)->np.ndarray:
    return np.genfromtxt(filename, dtype=float, delimiter=',')


def calculate_distances(allvalues:np.ndarray, row:np.ndarray)->np.ndarray:
    diff2 = np.square(allvalues - row)
    return np.sqrt(np.sum(diff2, axis=1))

def get_min_max(allvalues:np.ndarray)->tuple:
    amin = np.amin(allvalues, axis=0)
    amax = np.amax(allvalues, axis=0)
    return amin, amax

def normalize(array:np.ndarray, stdarray:np.ndarray, meanarray:np.ndarray):
    global g_normalize_to_zero_mean_and_unit_variance
    if g_normalize_to_zero_mean_and_unit_variance:
        x = (array - meanarray) / stdarray
        return x
    else:
        return array

def scale(array:np.ndarray, amin:np.ndarray, amax:np.ndarray)->np.ndarray:
    global g_scale_between_zero_and_one
    if g_scale_between_zero_and_one:
        x = array - amin
        scale = amax - amin
        return x / scale
    else:
        return array

def predict(train_features:np.ndarray, train_values:np.ndarray, test_features:np.ndarray, k:int, n:int)->np.ndarray:
    stddvarr = np.std(train_features, axis=0)
    meanarr = np.mean(train_features, axis=0)
    train_norm = normalize(train_features, stddvarr, meanarr) # Normalize
    amin, amax = get_min_max(train_norm)
    train_norm = scale(train_norm, amin, amax)                # Scale
    stddev = np.std(train_norm, axis=0)
    test_norm = normalize(test_features, stddvarr, meanarr)
    test_norm = scale(test_norm, amin, amax)        # Normalize
    test_norm = scale(test_features, amin, amax)    # Scale


    all_predictions = []

    for i in test_norm:
        distances = calculate_distances(train_norm, i)
        sorted_indices = np.argsort(distances)[0:k]
        nearest_distances = distances[sorted_indices]
        nearest_values = train_values[sorted_indices]

        nearest_weights = 1 /  nearest_distances
        nearest_weights = nearest_weights ** n
        prediction = np.sum(np.multiply(nearest_weights, nearest_values))
        prediction = prediction / np.sum(nearest_weights)

        all_predictions.append(prediction)

    return all_predictions

def calculate_r2(predicted:np.ndarray, actual:np.ndarray)->float:
    sum_square_residuals = np.sum(np.square(actual - predicted))
    mean_actual = np.mean(actual)
    sum_squares = np.sum(np.square(actual - mean_actual))
    return 1 - (sum_square_residuals / sum_squares)

    
    
def main(filename:str, testfilename=str):
    array = read_csv(filename)
    test = read_csv(testfilename)

    train_features = array[:,:-1]
    train_labels = array[:,-1]
    test_features = test[:,:-1]
    test_labels = test[:,-1]


    for n in range(1, 20, 1):
        predicted = predict(train_features, train_labels, test_features, 3, n)
        r2 = calculate_r2(predicted, test_labels)
        print(n, r2)



if "__main__" == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="File name", type=str, required=True)
    parser.add_argument("-tf", "--test-file", help="Test file name", type=str, required=True)
    args = parser.parse_args()

    file_name = args.file
    test_file_name = args.test_file

    main(file_name, test_file_name)
