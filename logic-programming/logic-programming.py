from kanren import Relation, facts, run, eq, membero, var, conde
x = var()
y = var()
z = var()

# Question 1: Modeling Star Wars family relations
parent = Relation()
facts(parent, ("Darth Vader", "Luke Skywalker"),
              ("Darth Vader", "Leia Organa"),
              ("Leia Organa",  "Kylo Ren"),
              ("Han Solo",  "Kylo Ren"))


# Question 2: Queries about the family
# Who is parent of Luke Skywalker
print('Question 2:', run(1, x, parent(x, "Luke Skywalker")))
# Who are the children of Darth Vader
print('Question 2:', run(2, x, parent("Darth Vader", x)))


# Question 3: Define the grandparent relation
def grandparent(x, z):
    y = var()
    return conde((parent(x, y), parent(y, z)))


print('Question 3:', run(1, x, grandparent(x, "Kylo Ren")))


# Question 4: Answers questions 1, 2 and 3 using default python
print('Question 4:')


def create_person (name, parent, children):
    return {"name": name, "parent": parent, "children": children}


people = [create_person("Darth Vader", "", ["Luke Skywalker", "Leia Organa"]),
          create_person("Luke Skywalker", "Darth Vader", []),
          create_person("Leia Organa", "Darth Vader", ["Kylo Ren"]),
          create_person("Han Solo", "", ["Kylo Ren"])]


def parents_of(name):
    parents = []
    for person in people:
        if name in person['children']:
            parents.append(person['name'])
    return parents


def children_of(name):
    for person in people:
        if person['name'] == name:
            return person['children']


def grandparents_of(name):
    grandparents = []
    parents = parents_of(name)
    for parent_ in parents:
        grandparents += parents_of(parent_)
    return grandparents


print(parents_of("Luke Skywalker"))
print(children_of("Darth Vader"))
print(grandparents_of("Kylo Ren"))
