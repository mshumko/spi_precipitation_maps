# Introduction
This package contains the software to create precipitation maps for the Space Precipitation and Impacts (SPI) ISFM project.

# Installation
To install as a developer run:

```bash
git clone git@github.com:mshumko/spi_precipitation_maps.git
cd spi_precipitation_maps
```

Then run  one of these (see comment in requirement.txt)
```bash
python3 -m pip install -e .
```
or 
```bash
python3 -m pip install -r requirements.txt 
```

# Configuration

## SAMPEX
To work with the `sampex_maps` package, you'll need to 
1. Download the [SAMPEX data](https://izw1.caltech.edu/sampex/DataCenter/data.html) 
2. Tell the [sampex](https://pypi.org/project/sampex/) dependency where to find the SAMPEX data by running `python3 -m sampex config`.

## Whats up with the `python3 -m ... config` step?
A lot of data science projects load data external to the source code (a good practice) so `project/__main__.py` creates a `project/config.ini` file that is loaded on import by `project/__init__.py`. In this case, replace `project` with `sampex_maps` or other package in this directory.

To execute `project/__main__.py`, first install `project` with the steps above and then run `python3 -m project config` and answer the prompt. You will now see a `project/config.ini` with two paths: one to this project and the other to the specified data directory. One loaded by `project/__init__.py`, this dictionary is accessed via `import project.config`.