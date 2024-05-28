# Configuration of KAPy

 KAPy is built upon the fundamental design philosophy that as much as possible should be configurable via configuration files, and with a minimal (preferably no) degree of hard-coding. Configuration of KAPy takes place via a collection  of YAML and TSV files that specify all of the necessary options.

The primary configuration file in KAPy is the `config.yaml`file, found in `./config/config.yaml`. This choice of naming structure follows common conventions used in the Snakemake community. `config.yaml` also draws in configuration tables defining other configuration options, including inputs, indicators and variables. In practice, the user will work with all sets of configuration files. 

Configuration options are validated using JSON schemas, which can be found in the directory `./workflow/schemas/`. These files specify the allowed configuration options and also  contain the corresponding documentation. Human-readbile versions of these schema, including description of what each option does, can be found in the following files:

* [config.md](./configuration/config.md) Options for the primary configuration file, `config.yaml`
* [indicators.md](./configuration/indicators.md) Indicator configuration table
* [inputs.md](./configuration/inputs.md) Input configuration table
* [periods.md](./configuration/periods.md) Period configuration table
* [scenarios.md](./configuration/scenarios.md) Emission scenario configuration table
* [seasons.md](./configuration/seasons.md) Season configuration table


