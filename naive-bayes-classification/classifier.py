from os import listdir
from os.path import isfile, join
import numpy as np
import re
import math


negative_path = '/Users/giancarlokc/Repositories/naive-bayes-classification/dataset/review_polarity/txt_sentoken/neg'
positive_path = '/Users/giancarlokc/Repositories/naive-bayes-classification/dataset/review_polarity/txt_sentoken/pos'
features = ['awful', 'bad', 'boring', 'dull', 'effective', 'enjoyable', 'great', 'hilarious']


def files_from_path(path):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    return files


def contents_from_file(path):
    f = open(path, "r")
    contents = f.read()
    return contents


def compute_feature_vectors(path):
    # Get list of negative files
    files = files_from_path(path)

    # Iterate on file list
    feature_vector_list = [None] * 1000
    file_index = 0
    for file in files:
        # Create feature vector for file
        feature_vector = [None] * 8
        feature_index = 0
        for feature in features:
            count = contents_from_file(path + '/' + file).lower().count(feature)
            feature_vector[feature_index] = (1 if count > 0 else 0)
            feature_index = feature_index + 1
        # Add feature vector to feature vector list
        feature_vector_list[file_index] = feature_vector
        file_index = file_index + 1

    return feature_vector_list


def split_non_alpha(s):
   pos = 1
   while pos < len(s) and s[pos].isalpha():
      pos+=1
   return s[:pos], s[pos:]


def compute_feature_probability(feature_vectors):
    sums = np.sum(feature_vectors, axis=0)
    sums = sums * 100 / len(feature_vectors)
    return sums


def extract_vocabulary_from_path(path):
    files = files_from_path(path)
    for f in files:
        f_contents = contents_from_file(path + '/' + f)
        split = re.split('[^a-zA-Z]', f_contents)
        return list(set([x for x in split if x]))


def extract_vocabulary():
    return list(set(extract_vocabulary_from_path(positive_path) + extract_vocabulary_from_path(negative_path)))



















def extract_vocabulary_from_file_contents(file_contents, available_words):
    split = re.split('[^a-zA-Z]', file_contents)
    return list(set([x for x in split if (x and x in available_words)]))


def count_files_containing_word(files, word):
    count = 0
    for _file in files:
        count += 1 if word in _file else 0
    return count


def train_bernoulli(_classes, vocabulary):
    class_probability = {}
    conditional_probability = {}

    # Calculate total file count
    total_file_count = 0
    for _class in _classes:
        total_file_count = total_file_count + len(_class['files'])

    for _class in _classes:
        class_probability[_class['name']] = len(_class['files']) / total_file_count
        conditional_probability[_class['name']] = {}
        for word in vocabulary:
            conditional_probability[_class['name']][word] = (count_files_containing_word(_class['files'], word) + 1) / (len(_class['files']) + 2)
    return class_probability, conditional_probability


def apply_bernouli(_classes, vocabulary, class_probability, conditional_probability, file_contents):
    # Extract terms from file
    file_vocabulary = extract_vocabulary_from_file_contents(file_contents, vocabulary)
    class_score = {}
    for _class in _classes:
        class_score[_class['name']] = math.log(class_probability[_class['name']])
        for word in vocabulary:
            prob = conditional_probability[_class['name']][word]
            class_score[_class['name']] += math.log(prob if word in file_vocabulary else (1 - prob))

    best = - float("inf")
    best_class = None
    for score in class_score:
        if class_score[score] > best:
            best = class_score[score]
            best_class = score

    return best_class


def run_simulation(train_data, test_data):

    # Train classifier
    prior_prob, cond_prob = train_bernoulli(train_data, features)

    # Run classifier
    correct_guesses_for = {}
    for _class in test_data:
        correct_guesses = 0
        for f in _class['files']:
            if apply_bernouli(test_data, features, prior_prob, cond_prob, f) == _class['name']:
                correct_guesses += 1
        correct_guesses_for[_class['name']] = correct_guesses
        print('Correct guesses for', _class['name'], ':', correct_guesses)


def format_data(class_names, class_files_path, include=[], exclude=[]):
    data = []

    # Prepare data
    class_name_index = 0
    for class_name in class_names:
        file_contents = []
        files = files_from_path(class_files_path[class_name_index])
        for f in files:
            file_id = int(f[2:5])
            if len(include) and file_id not in include:
                continue
            if len(exclude) and file_id in exclude:
                continue
            file_contents.append(contents_from_file(class_files_path[class_name_index] + '/' + f))
        data.append({'name': class_name, 'files': file_contents})
        class_name_index += 1

    return data


# Start
k_cross_validation = 10
for k in range(0, k_cross_validation):
    print('K=', k)

    test_range = []
    for i in range(0, 100):
        test_range.append(k * 100 + i)

    t_data = format_data(['positive', 'negative'], [positive_path, negative_path], [], test_range)
    r_data = format_data(['positive', 'negative'], [positive_path, negative_path], test_range, [])
    run_simulation(t_data, r_data)
