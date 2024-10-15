# Contributing

Firstly, thanks for your interest in KAPy, and for wanting to contribute to our project. We value all contributions, big and small - everything from fixing a typo in the documentation to adding new features is encouraged and welcomed. The goal of this guide is to layout a recipes and a few standards for how to best do this, so as to streamline the process and make development as efficient as possible. 

Very little of this document is new - it is based on standards and approaches seen elsewhere in the open source community. Nevertheless, it is a good idea to read it through before starting to modify the code in any detail.

## GitHub Flow

The basic workflow for contributing here follows the so-called GitHub Flow, using the https://github.com/Klimaatlas/KAPy GitHub repository as the core. A description of GitHub flow can be found here: https://docs.github.com/en/get-started/quickstart/github-flow
We have also provided a step-by-step recipe as to how we have implemented this in the context of KAPy.

1. *Identify the problem* What is the problem that you are going to solve? Be clear about this right from the very start, and only solve one problem at a time. The GitHub issue list https://github.com/Klimaatlas/KAPy/issues serves as both our todo list, but also our archive of what we have done. If the problem that you are trying to solve is already listed there, please assign the issue to your self. Otherwise, if it is an entirely new problem, please create an issue describing the problem and potential solutions (and then assign it to your self). Discussing the issue with the administrators is often a good idea before diving into coding, but is not strictly necessary. Note the issue number(s) that you will be working on - you will need them below.

2. *Fork the repository* Create a local fork of the main repository into your private GitHub repo. It's best to fork from the development branch ("dev") of the repository, to make sure that you're starting from the very latest version. Read more about how to do that here: https://docs.github.com/en/get-started/quickstart/fork-a-repo. If you already have a fork, make sure that you synchronise it with the main repo before going any further.

3. *Clone the fork* Create a local copy of your forked repo by cloning it to your local machine where you are going to do the work. See here for details: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository Cloning via SSH is recommended. Now you have a local version of KAPy, ready to edit

4. *Make it so* (in the words of Jean Luc Picard). Make the edits to the code.

5. *Check that change* Does the change actually work? Does it behave like it should? Have you considered edge cases? Have you tested it against the testing data sets? Are the code changes documented internally? The more work you put into testing and checking that your changes work, the better the whole project functions and the less time that will be spent swatting bugs in the future. Please don't neglect this step.

6. *Commit!* Now you're ready to start getting your changes back into the main branch. Start by committing your code to your local repository - see here for some details if you're not familar: https://github.com/git-guides/git-commit Make sure that your commit message is informative and in particular that it references the issue number with a # mark e.g. "Add support for irregular grids to fix #16". You don't have to solve evertything in one commit - indeed, breaking the problem into smaller commits makes it easier to debug and track changes in the future.

7. *Push* Once you've got all of your changes in place, and are convinced that the code is working, you can push your commits back to your private fork on GitHub: https://docs.github.com/en/get-started/using-git/pushing-commits-to-a-remote-repository 

8. *Request a pull* Now there is a publically available copy of your changes in your own private fork. To get these into the main repo, and thereby into KAPy, you need to ask the administrators to merge your changes - this is done via a "pull request". See here for details https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request 

9. *Revisions* Now we go through the code review process - an administrator or another member of the community will review your code. And just like a scientific paper (almost) never gets accepted on the first submission, you may get feedback from the administrators asking you to make changes to your code. This is normal, and indeed is the key quality control process in the project. There may be a need to iterate several times here.

10. *Merged* Once the administrator / review is happy with the changes, they will merge it into the development branch of the project, and ultimately into the main branch, and close the associated issue. And we're done. Well done! And thanks for your (first?) contribution to KAPy!

## Other Notes
* KAPy follows the semantic versioning approach to version numbers - see here for more details https://semver.org/
* The KAPy repository has two branchs - "main", which is the latest released version, and "dev", which is the cutting edge where new features are developed and tried out before being released on the main branch. Use "main" for production, use "dev" for development.
* A development version of the KAPy conda environment can be found in the repository in [./workflow/envs/dev.yaml](./workflow/envs/dev.yaml). This environment builds on top of the standard `KAPy`environment, adding additional libraries that can be useful for development purposes, but aren't relevant in a general production process.
