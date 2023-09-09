<img title="tabs" alt="software resource tabs" src="images/tabs.png">


# Plot Tool Stats
**Authors:** Denise Kwong and Lorraine Hwang, UC Davis


## Description

This notebook provides a starting point to customize plots from data downloaded from Tool Stats tab from the Software Downloads landing pages on geodynamics.org.

Data is downloaded as a .json file and should be uploaded to the /json directory.

### Directory Structure

**Source files**

* notebooks/<br>
  Individual notebooks that are linked here.

**Input files**

* database/<br>
    hit_database is the legacy download data from 2012-2021 <br>
    ip_database is the data used to translate the legacy data decimal IPs to lat lon
    
* images/ <br>
    Images used in this notebook.
    
* json / <br>
    Recommended directory for downloaded json files.  
    
**Output files**

* csv/ <br>
    Recommended directory to write converted .csv files.  

### Output 

Use the plotly snapshot tool to *Download plot as png*. Default file name is `newplot.png`

You may also convert the .json files to .csv for export.  Files are written to /csv directory for download.

## Contributing

Help improve these plots for the community by contributing your changes to the repository.



## Dependencies

The following package msut be imported for all plots. These package are used in plotting, reading and converting data.


```python
# Import the libraries used for data, reading JSON, converting to csv
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import csv
```

The color palette is defined below.


```python
# CIG colors - used for graphs
colors = ['#1A3D59', '#00548A', '#007CBA', '#9A9400', '#6D3527', '#9F3122', '#D75E00', '#F98D29', '#B41782', '#EBAA20', '#E7417A']
```

### *Optional*
If you are printing out dataframes, you will want to reset the default to `None` to see all the data.

Use the *Create New View for Output* menu option (right click) to display output values in a separate window.


```python
# Optional
pd.set_option('display.max_rows', None)
```

---

## Table of Contents

* [Download Data](notebooks/map_download.ipynb)
* [Download Maps](notebooks/map_plot_revised.ipynb)
* [Author Contributions](notebooks/contributions.ipynb)
* [Commits](notebooks/commits.ipynb)
* [Issues](notebooks/issues.ipynb)
* [Pull Requests](notebooks/pull_requests.ipynb)
* [Asset Downloads](notebooks/assets.ipynb)


---
# Updating README.md

If you make any changes to this file, please update the README.md file by running the following command:


```python
!jupyter nbconvert --to markdown README.ipynb
```


```python

```
