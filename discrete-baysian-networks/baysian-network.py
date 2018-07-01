from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import numpy as np
from pgmpy.factors.discrete import JointProbabilityDistribution

model = BayesianModel([('Difficulty', 'Rating'),
                       ('Musicianship', 'Rating'),
                       ('Musicianship', 'Exam'),
                       ('Rating', 'Letter')])

cpd_difficulty = TabularCPD(variable='Difficulty', variable_card=2, values=[[0.6], [0.4]])
cpd_musicianship = TabularCPD(variable='Musicianship', variable_card=2, values=[[0.7], [0.3]])

cpd_rating = TabularCPD(variable='Rating', variable_card=3,
                        values=[[0.30, 0.05, 0.90, 0.50],
                                [0.40, 0.25, 0.08, 0.30],
                                [0.30, 0.70, 0.02, 0.20]],
                        evidence=['Musicianship', 'Difficulty'],
                        evidence_card=[2, 2])

cpd_exam = TabularCPD(variable='Exam', variable_card=2,
                      values=[[0.95, 0.20],
                              [0.05, 0.80]],
                      evidence=['Musicianship'],
                      evidence_card=[2])

cpd_letter = TabularCPD(variable='Letter', variable_card=2,
                        values=[[0.10, 0.40, 0.99],
                                [0.90, 0.60, 0.01]],
                        evidence=['Rating'],
                        evidence_card=[3])

model.add_cpds(cpd_difficulty, cpd_musicianship, cpd_rating, cpd_exam, cpd_letter)
is_valid = model.check_model()
print('Is valid:', is_valid)


    infer = VariableElimination(model)
    q = infer.query(variables=['Letter'])

# q = infer.query(variables=['Letter'], evidence={'Musicianship': 0})
print(q['Letter'])


# P(m = strong)
m_prob = model.get_cpds('Musicianship').values[1]
# P(d = low)
d_prob = model.get_cpds('Difficulty').values[0]
# P(r = ** | m = strong, d = low)
r_prob = model.get_cpds('Rating').values[1][0][1]
# P(e = high | m = strong)
e_prob = model.get_cpds('Exam').values[1][1]
# P(letter = weak | **)
l_prob = model.get_cpds('Letter').values[0][1]
print(m_prob, d_prob, r_prob, e_prob, l_prob)
# Total probability
print(m_prob * d_prob * r_prob * e_prob * l_prob)
