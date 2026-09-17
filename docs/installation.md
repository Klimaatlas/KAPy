# Installing KAPy

Welcome to KAPy! This guide walks you through installing KAPy and creating your first KAPy project.

You don't need to be an expert in Python, Conda, or Snakemake to get started. We will take things one step at a time, and explain what each step does along the way.

> **In short:** you will install Conda, use it to create a KAPy environment, and then use KAPy's project template to create a working project of your own.

## Before you start

KAPy is designed to run on Linux systems and uses [Conda](https://conda.io/projects/conda/en/latest/index.html) to manage its software environment.

Conda is a package and environment manager. You can think of a **Conda environment as a self-contained toolbox**: it contains the particular versions of Python and all the other software packages that KAPy needs. This means that installing KAPy does not require you to manually install each of its many dependencies.

If you already have Conda installed, you can skip to [Creating the KAPy environment](#creating-the-kapy-environment).

If you don't have Conda, don't worry — installing it is a one-time step and there are good instructions on the [official Conda website](https://conda.io/projects/conda/en/latest/index.html).

## Creating the KAPy environment

Once Conda is installed, we can create the environment that KAPy will use.

Open a terminal. If you are not familiar with the terminal, don't be put off by this! You only need to enter a few commands, and we explain what they do.

KAPy provides a ready-made Conda environment description containing all the packages needed to run KAPy. Conda can download this description directly from the KAPy GitHub repository.

Run:

```bash
conda env create -f https://raw.githubusercontent.com/Klimaatlas/KAPy/refs/heads/main/workflow/envs/env.yaml
```

Conda will now download and install the required packages. This may take a little while, particularly the first time you install KAPy.

When it has finished, you should see a message indicating that a new environment called **KAPy** has been created.

### What just happened?

The command above has created a Conda environment called `KAPy`. The environment contains:

* Python and the Python packages used by KAPy
* KAPy's workflow tools
* Snakemake
* Cookiecutter, which is used to create new KAPy projects
* Ncview, for visualisation of results
* Other software required by the KAPy workflow

You don't need to install these packages individually. They are all managed by Conda as part of the KAPy environment.

## Activating KAPy

Conda environments are normally kept separate from your main system environment. Before using KAPy, we therefore need to tell Conda that we want to work in the `KAPy` environment.

Run:

```bash
conda activate KAPy
```

You should now see something like `(KAPy)` at the beginning of your terminal prompt:

```text
(KAPy) user@computer:~$
```

This is a useful indication that you are working inside the KAPy environment.

> **Tip:** You will normally need to activate the KAPy environment whenever you start a new terminal session and want to work with KAPy. If you get an error saying the a command isn't recognised, check that the environment is activated. 

## Creating your first KAPy project

KAPy includes a **project template** that can be used to create a new project.

The template is provided using [Cookiecutter](https://cookiecutter.readthedocs.io/). Cookiecutter takes a standard project structure and customises it according to the choices you make.

This means that you don't have to manually create all the folders and configuration files needed for a KAPy project.

First, move to the directory where you would like to create your project. For example:

```bash
cd ~/projects
```

Then run:

```bash
cookiecutter --directory cookiecutter gh:Klimaatlas/KAPy
```

Cookiecutter will ask you a series of questions about your project.

For example, it may ask you for a project name or which configuration you would like to use. **You don't need to understand every option before getting started** — the prompts include explanations to help you make the appropriate choices.

When you have finished answering the questions, Cookiecutter will create a new directory containing your KAPy project.

For example, if you choose `My KAPy project` as your project name, you will end up with a directory similar to:

```text
~/projects/
└── my_kapy_project/
    ├── config/
    ├── inputs/
    ├── KAPy/
    ├── outputs/
    ├── profiles/
    ├── resources/
    ├── scripts/
    ├── Snakefile
    └── README.md
```

The exact contents depend on the options you select when creating the project.

### Why does KAPy create a project for you?

KAPy separates the **general KAPy framework** from the **project-specific configuration**.

The KAPy framework provides the processing logic and workflow components, while your project contains things such as:

* configuration
* input data
* output data
* your own processing scripts
* project-specific settings

This makes it possible to use the same KAPy framework for many different projects without having to copy or modify the KAPy source code itself.

Importantly, cookiecutter also sets up a local git repository for your project, so that you can easily track changes to your project. Running `git status` in your project directory will show you the status of your local repository.

## Running your project

Once Cookiecutter has finished, change into the new project directory.

For example:

```bash
cd my_kapy_project
```

You can then run the example workflow with Snakemake with the following command:

```bash
snakemake --cores 1
```

Snakemake will execute the workflow using one CPU core.

If everything has been installed correctly, the workflow should now start running.

🎉 **Ka pai! You have installed KAPy and run your first KAPy workflow!**

## Where to go next

The steps above are enough to get a KAPy project up and running, but there is much more to KAPy than the initial setup.

If you are new to KAPy, we recommend continuing with the tutorials in the  **Learning KAPy** section of the [documentation](./docs/README.md) directory. These introduce the KAPy concepts and workflow step by step and explain how to configure KAPy for your own work.   

If you are already familiar with KAPy and want to get straight to the details, the documentation also provides more information about the individual workflow components and configuration options.

If you want to link your project to a remote repository such as GitHub.com or a local GitLab installation, this is the ideal time to do it - read more about this in the [GitHub documentation](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github?utm_source=chatgpt.com).

## A quick recap

If you just want the commands in one place, the installation process is:

```bash
# Create the KAPy Conda environment
conda env create -f https://raw.githubusercontent.com/Klimaatlas/KAPy/refs/heads/main/workflow/envs/env.yaml

# Activate the environment
conda activate KAPy

# Create a new KAPy project
cookiecutter --directory cookiecutter gh:Klimaatlas/KAPy

# Move into your new project
cd <your-project-directory>

# Run the workflow
snakemake --cores 1
```

The important thing to remember is that **KAPy itself is managed through the Conda environment**, while **your work is carried out in the project created by Cookiecutter**. Once you understand that distinction, the rest of the KAPy documentation should be much easier to navigate.
