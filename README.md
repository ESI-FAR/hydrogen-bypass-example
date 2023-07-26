# Comparing the Implementation of a Hydrogen Bypass Energy System Model

This repository contains different implementations of the same energy system model.
They can serve as simple examples to help get started with a particular framework, and to ease comparisons between frameworks.

The current frameworks included are [PyPSA] and [Calliope]


## The Model

The base model simulates two locations over the course of one day: a wind power generation location, and a city with a gas power plant to fulfill any unmatched demand.
The city has a power demand ranging from about 380 MW to around 700 MW.
Wind power generation varies from over 1400 MW down to under 600 MW at the end of the day.
Power transmission from the wind generation to the city is limited at 400 MW.

To make better use of the extra wind capacity, the model is extended with a hydrogen bypass.
At the wind power generation location, an electrolyzer can create hydrogen at 70% efficiency by consuming up to 500 MW of power.
This hydrogen is then stored in a large storage facility, before being used at the city to generate up to 250 MW of extra power at 50% efficiency.
In the extended model, usage of the gas power plant is reduced to a minimum, with hydrogen taking over most of the otherwise unfulfilled demand. 


## Installation

After cloning the repository, it is recommended to create a separate Python environment for each framework.
Popular examples include Conda, venv/virtualenv and pyenv.
The relevant dependencies are listed in a `<FRAMEWORK_NAME>-requirements.txt` per framework folder and can be installed as follows:
```bash
cd <FRAMEWORK_NAME>
# activate your favorite (virtual) environment
pip install -r <FRAMEWORK_NAME>-requirements.txt
```

### Using a single environment

<details>
<summary>
Since PyPSA and Calliope have some 'officially' conflicting dependencies, you can use the following command at your own risk to install all dependencies in one environment:
</summary>

```bash
pip install --no-deps -r all-requirements.txt
```
</details>



### PyPSA

To run the PyPSA model:
```bash
cd pypsa
# install dependencies if needed, see Installation
python hydrogen_bypass.py
```

The results are saved as `.png` plots in the `pypsa/` folder. 


### Calliope

To run the Calliope model:
```bash
cd calliope
# install dependencies if needed, see Installation
python run.py
```

The results are saved as interactive `.html` plots in the `calliope/` folder.


[PyPSA]: https://pypsa.org/
[Calliope]: https://www.callio.pe/

