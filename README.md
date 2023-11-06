# CptS 350 - Symbolic Graph Project

Project for WSU CptS 350 using [PyEDA](https://pyeda.readthedocs.io/en/latest/) to convert graphs to Binary Decision Diagrams. PyEDA is a Python library for electronic design automation. Here, it is used for Boolean Algebra expressions to determine reachability over a graph.

## Installing Dependencies

Requires Python 3 and pip. From the root directory, run:

`pip3 install -r requirements.txt`


## Running Tests

Tests include converting nodes and graphs to their equivalent BDD, and a final "Statement A" which combines many concepts of operating on BDDs. From the root directory, run:

`python3 src/tests.py`
