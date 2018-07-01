import numpy as np
from hmmlearn import hmm
np.random.seed(42)


def pretty_states(state_seq):
    state_label = ['Healthy', 'Injured']
    index = 0
    for state in state_seq:
        print(state_label[state] + ' (' + 'State ' + str(index) + ')')
        index += 1


def pretty_action_states(state_seq):
    state_label = ['Dribble', 'Pass   ', 'Shoot  ']
    index = 0
    for state in state_seq:
        print(state_label[state] + ' (' + 'State ' + str(index) + ')')
        index += 1


def generate_states():
    model = hmm.GaussianHMM(n_components=2, covariance_type="full")
    model.startprob_ = np.array([0.0, 0.0])
    model.transmat_ = np.array([[0.7, 3.0],
                                [0.5, 0.5]])
    model.means_ = np.array([[0.0, 0.0], [0.0, 0.0]])
    model.covars_ = np.tile(np.identity(2), (3, 1, 1))
    X, state_seq = model.sample(50)
    return state_seq


def generate_action_states(state_seq):
    action_states = []
    for state in state_seq:
        # Healthy
        if state == 0:
            prob = np.random.uniform(0, 1)
            if 0 <= prob < 0.2:
                action_states.append(0)
            elif 0.2 <= prob < 0.3:
                action_states.append(1)
            elif 0.3 <= prob <= 1.0:
                action_states.append(2)
        # Injured
        elif state == 1:
            prob = np.random.uniform(0, 1)
            if 0 <= prob < 0.3:
                action_states.append(0)
            elif 0.3 <= prob < 0.9:
                action_states.append(1)
            elif 0.9 <= prob < 0.1:
                action_states.append(2)
    return action_states


states = generate_states()
print('######## State Sequence')
pretty_states(states)
new_states = generate_action_states(states)
print('######## Action State Sequence')
pretty_action_states(new_states)

