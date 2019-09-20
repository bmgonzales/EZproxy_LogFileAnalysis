# EZproxy_LogFileAnalysis
Python script to analyze EZproxy SPU logs [Forked]

Code4Lib article: https://journal.code4lib.org/articles/13918

Generally speaking, this script requires the following Python libraries to run:
- Pandas
- Matplotlib
The full list of dependencies are listed below.

I recommend installing Anaconda (https://www.anaconda.com/distribution/) to run the code and manage libraries

## Different report types
**Previous month**
Run the EZProxy-PrevMonth script to capture the data from the previous month (the script formats filenames and HTML based on the previous month)
**Full year**
Run the EZProxy-FY script to capture data for a larger period of time. This one doesn't create a By Day chart/table.

## Required libaries & bependencies
**Pandas**
- setuptools
- NumPy
- python-dateutil
- pytz
- numexpr
- bottleneck
**Matplotlib**
- Python
- FreeType
- libpng
- NumPy
- setuptools
- cycler
- dateutil
- kiwisolver
- pyparsing

## How to use
