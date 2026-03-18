# Using KAPy as a module in a workflow

KAPy is primarily intended to be used as a library of functions supporting a Snakemake workflow. Both Git and Snakemake handle the use of submodules well, with a minimal amount of configuration. This README provides a basic introduction to how to use KAPy in a modular setting - for more details and more worked through example, see the [Tino-Pai project](https://github.com/Klimaatlas/TinoPai) on GitHub, which is a full working example of using KAPy as part of a climate service workflow, where all settings and configuration files are also placed under version control.

The following documentation provides to approaches to using this repository. The first, 'Quick Start', makes a local copy of the repository that can be used to get up and running as quickly as possible. Alternatively, 'Custom Configuration' shows how to create a fully customised instance of a pipeline using KAPy.

# Custom Configuration

1. First, create a directory where you wish to store your processing workflow on your local machine.

```
mkdir my_KAPy
cd my_KAPy
git init
```

2. Initialise git within that directory

```
git init
```

3. Create some directories to store your configurations, inputs and outputs. 
```
mkdir config
mkdir inputs
mkdir outputs
```

4. Now comes the key trick for integrating KAPy  - we add the KAPy repository as a git submodule, like so:
```
git submodule add git@github.com:Klimaatlas/KAPy.git
```
You can read lots more about exactly how Submodules work in Git here: https://git-scm.com/book/en/v2/Git-Tools-Submodules We're not going to go into the details, other than to note that they do work very nicely for this application.


5. Unfortunately snakemake isn't able to work with this setup directly, so we need to tell it how to use KAPy. We do this via a Snakefile, where KAPy is explicitly imported into the local workflow - an example of such a Snakefile that can be used directly can be found in the same folder as this README i.e. `./KAPy/workflow/modularisation/Snakefile`. Copy this file into the local installation

```
cp ./KAPy/workflow/modularisation/Snakefile . 
git add Snakefile
```

6. Commit the change
```
git commit -m 'Setup my_KAPy'
```

7. That's basically the core of it - everything else is handled in the same way as normal KAPy. The rest of the work is populating the repository, including input data and configuration files. The configuration files that come with KAPy can be used as a useful shortcut

```
cp ./KAPy/config/* ./config/
```

9. That's it - you've got your own version of KAPy running locally, with everything you need under version control. *Ka pai*!


## More reading
* [KAPy Tutorials](https://github.com/Klimaatlas/KAPy/blob/main/docs/tutorials/README.md) 
* [Snakemake modules](https://snakemake.readthedocs.io/en/stable/snakefiles/modularization.html#modules)
* [Git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)

