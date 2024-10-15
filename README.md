# KAPy Pilot at MET
This is a fork of KAPy developed at the Danish Meteorological Institute, for the purpose of producing climate adaptation information. [See KAPy documentation here](./docs/README.md)

We have chosen to make a fork, rather than using submodule, because we need to develop functionality that is not yet supported in base KAPy. This includes:
- Setting and validation of FAIR metadata
- Quality Assurance across the pipeline

Our full pipeline with intended test cases is seen below:
![Flow chart with test cases Klimakverna](./flowchart.png)

# Getting started
(...)

# Git guidelines
- Create smaller manageable issues as you see fit.
- When working on an issue, create a branch and commit there.
- Always make a merge (pull) request when creating a branch.
- Always merge main into branch first before merging branch into main.
- Merge back into main branch regularly, ideally when completing an issue. If it takes longer, discuss with group
- Use pull requests for code review by assigning each other as reviewers.

# Folder structure
The main location of the repository is on PPI-ext, the user folder klimakverna is the base folder:
```
<base>/development/KAPy
```
We use the same conda environment, which we keep in a sister folder:
```
<base>/development/conda
```
In each test case, we regard Climate in Norway file locations as valid input. In this way, test cases should generally not depend on each other. Output is stored in appropriate subfolders here:
```
<base>/development/results
```