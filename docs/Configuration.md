# Configuration of KAPy

Configuration of KAPy is based around a series of YAML and TSV files that specify all of the necessary options. KAPy is built with the fundamental design philosophy that as much as possible should be configurable via configuration files, and with a minimal (preferably no) degree of hard-coding.

The primary configuration file in KAPy is the `config.yaml`file. KAPy looks for this file in two locations and uses the first file found:
* `./config/config.yaml` 
* `./config.yaml`

`config.yaml` also draws in configuration tables defining other configuration options, including inputs, indicators and variables. In practice, the user will work with all sets of configuration files. 

Configuration options are validated using JSON schemas, which can be found in the directory `./workflow/schemas/`. These files specify the allowed configuration options and also  contain the corresponding documentation. Markdown versions of these schema, including description of what each option does, can be found in the following files:

* [./docs/configuration/config.md](./docs/configuration/config.md) Options for the primary configuration file, `config.yaml`
* [./docs/configuration/indicators.md](./docs/configuration/indicators.md) Indicator configuration table
* [./docs/configuration/inputs.md](./docs/configuration/inputs.md) Input configuration table
* [./docs/configuration/periods.md](./docs/configuration/periods.md) Period configuration table
* [./docs/configuration/scenarios.md](./docs/configuration/scenarios.md) Emission scenario configuration table
* [./docs/configuration/seasons.md](./docs/configuration/seasons.md) Season configuration table


