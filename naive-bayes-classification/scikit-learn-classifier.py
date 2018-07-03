from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from os import listdir
from os.path import isfile, join


features = ['awful', 'bad', 'boring', 'dull', 'effective', 'enjoyable', 'great', 'hilarious']

use_multinomial = False


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
            if use_multinomial:
                feature_vector[feature_index] = count
            else:
                feature_vector[feature_index] = (1 if count > 0 else 0)
            feature_index = feature_index + 1
        # Add feature vector to feature vector list
        feature_vector_list[file_index] = feature_vector
        file_index = file_index + 1

    return feature_vector_list


negative_feature_matrix = compute_feature_vectors('/Users/giancarlokc/Repositories/ai-projects/naive-bayes-classification/dataset/review_polarity/txt_sentoken/neg')
positive_feature_matrix = compute_feature_vectors('/Users/giancarlokc/Repositories/ai-projects/naive-bayes-classification/dataset/review_polarity/txt_sentoken/pos')

X = negative_feature_matrix + positive_feature_matrix
Y = []
Y[0:1000] = [0] * 1000
Y[1000:2000] = [1] * 1000

average_correct = 0
for i in range(10):
    print('\n\n')
    print('Cross Validation: ', i)

    train_X = X[:]
    del train_X[i*100:(i+1)*100]
    del train_X[1000+(i*100):1000+((i+1)*100)]
    test_X = X[i*100:(i+1)*100] + X[1000+(i*100):1000+((i+1)*100)]

    train_Y = Y[:]
    del train_Y[i*100:(i+1)*100]
    del train_Y[1000+(i*100):1000+((i+1)*100)]

    clf = MultinomialNB() if use_multinomial else BernoulliNB()
    clf.fit(train_X, train_Y)
    if use_multinomial:
        BernoulliNB(alpha=1.0, binarize=0.0, class_prior=None, fit_prior=True)
    else:
        MultinomialNB(alpha=1.0, class_prior=None, fit_prior=True)
    prediction = clf.predict(test_X)

    # Calculate % of correct negatives
    total_correct = 0
    for p in prediction[0:100]:
        total_correct += 1 if p == 0 else 0
    print('Correct negatives:', total_correct)
    average_correct += total_correct

    # Calculate % of correct positives
    total_correct = 0
    for p in prediction[100:200]:
        total_correct += 1 if p == 1 else 0
    print('Correct positives:', total_correct)
    average_correct += total_correct

print(float(average_correct)/2000)