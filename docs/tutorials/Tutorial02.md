# Tutorial 2 - Workflow control

## Goal

To familiarise yourself with snakemake and how the concepts of workflow control are implemented in KAPy.

## Point of departure

This tutorial follows on directly from the end of [Tutorial 1](Tutorial01.md).

## Instructions

1. In Tutorial 1, you should have performed a complete run of a KAPy pipeline, starting from a fresh installation. You can get an overview of the files that have been created using:
```
ls ./results/*
```

2. The status of the KAPy pipeline is maintained by a Python tool called Snakemake, which will be the focus of this Tutorial. Snakemake is conceptually very similar to GNU Make if you're familiar with that - the main difference is that it is implemented in Python and therefore allows the full range of the Python language to be used in describing the workflow. Both tools work by creating a conceptual model of all the files in workflow, and the relationship and dependencies between them, known as a [Directed Acyclic Graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph) (DAG for short). In Snakemake, these rules are specified in the "Snakefile" found in `./workflow/Snakefile`. Open it in a text editor and have a look at it. You don't need to worry about understanding it, and in most use cases you won't need to edit it, but it's good to know that it exists.

3. Snakemake is built up around a series of "targets" that can be built individually, or that can be chained together into a coherent pipeline. We can get a list of these targets with the following command. Compare the titles here with what you see in the Snakefile - they are the same because the targets are defined by the Snakefile.

```
snakemake -l
```

4. Snakemake has a handy visualisation tool that lets you examine the DAG. Try running this command, and then open `dag.png` in a graphics viewer or browser. You should be able to see the basic workflow of the pipeline, starting at the left from the primVar_files that serve as inputs, to the 101_files where the indicators are calculated, then aggregated into the ensemble stats, then the arealstats, and then finally the outbook notebook. This command uses the `dot` tool installed. If you don't have it installed, it can be installed in e.g. ubuntu as part of the `graphviz` package: `sudo apt install graphviz`. Make the DAG with the following command.

```
snakemake notebooks --dag | dot -Tpng -Grankdir=LR > dag.png
```

5. Ok, let's do something a bit more concrete. A natural start is to run the pipeline again with the command below. What do you think is going to happen? And what actually happens this time?

```
snakemake --cores 1
```

6. *Answer*: Nothing. Snakemake reports `Nothing to be done (all requested files are present and up to date).` This is perhaps surprising if you are thinking about KAPy as being a classical script. On the other hand, if you are thinking about it as a form of GNU Make, then you should have guessed the answer. What Snakemake has done here is to take the DAG specified in `Snakefile`and compare it with what actually exists on disk. When all the required files are present and correct, Snakemake is lazy and doesn't do anything.

7. Ok. So let's say then that something needs to be done - maybe we have, for example, updated our input data with a new version. Part of the way that Snakemake monitors changes and dependencies is via the modification time of the files - a downstream file should be "younger" (i.e. have a more recent modification date) than an "older" upstream file. We can throw the pipeline out of balance by modifying the time of one of the source files, to make it appear new:

```
touch resources/CORDEX/tas_AFR-22_NCC-NorESM1-M_rcp85_r1i1p1_GERICS-REMO2015_v1_mon_209101-210012.nc 
```

8. Snakemake will recognise this and want to update the pipeline. But, because it is smart (and lazy), it will only update the downstream files that are dependent on the input file. Try this:
```
snakemake -n
```

9. Only one of the primVar files will be updated, out of the six in total, which is smart. Let's do the update

```
snakemake --cores 1
```

10. We can illustrate this point further by damaging the state of the pipeline. Let's remove an individual file in the middle of the pipeline.
```
rm results/5.ensstats/101_CORDEX_rcp26_ensstats.nc 
```
11. What's going to happen when we run snakemake now? Try and form a hypothesis.

12. So, let's see. We can ask Snakemake what it's going to do by doing a "dry-run" `-n:

```
snakemake -n
```

13. *Answer*: Snakemake will only run the necessary parts of the pipeline, recreating the missing indicator file (the `ensstats_file` rule is going to be run). However, recreating this file creates a version of `101_CORDEX_rcp26_ensstats.nc` that is younger than the rest of the downstream dependencies, triggering a rebuild of them as well.

14. Run the pipeline to completion to finish. 

```
snakemake --cores 1
```

15. The concepts of workflow management are fundamental to a better understanding of KAPy and its strengths. While you probably won't need to manage or edit the workflow in daily usage (this is handled automatically as a result of the configuration), it is nevertheless good to have an idea of what is going on behind the scenes. Ka pai!


