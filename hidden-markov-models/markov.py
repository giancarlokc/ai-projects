import numpy as np
from hmmlearn import hmm
from random import randint


model = hmm.MultinomialHMM(n_components=2)
model.startprob_ = np.array([1.0, 0.0])
model.transmat_ = np.array([[0.7, 3.0],
                            [0.5, 0.5]])
model.emissionprob_ = np.array([[0.2, 0.1, 0.7],
                                [0.3, 0.6, 0.1]])

remodel = hmm.MultinomialHMM(n_components=2)
tests = []
for i in range(100):
    X, state_seq = model.sample(300, randint(0, 255))
    m = remodel.fit(X)
    tests.append({'observations': X, 'states': state_seq, 'score': m.score(X), 'model': m})

best = tests[0]
for test in tests:
    if test['score'] > best['score']:
        best = test

print('Best Model:')
print('Score: ', best['score'])
print('Transmat: ', best['model'].transmat_)
print('Emission Prob: ', best['model'].emissionprob_)

# Get prediction
Z2 = best['model'].predict(best['observations'])
print('Predict:', Z2)
print(best['states'])

# Calculate errors in prediction
index = 0
total_errors = 0
for prediction in Z2:
    if prediction != best['states'][index]:
        total_errors += 1
    index += 1
print('Total errors: ', total_errors, 'Accuracy: ', (300.0 - float(total_errors)) / 300.0)
