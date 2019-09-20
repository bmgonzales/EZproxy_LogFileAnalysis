# EZproxy_LogFileAnalysis
Python script to analyze EZproxy SPU logs [Forked]

Code4Lib article: https://journal.code4lib.org/articles/13918

Generally speaking, this script requires the following Python libraries to run:
- Pandas
- Matplotlib
The full list of dependencies are listed below.

I recommend installing Anaconda (https://www.anaconda.com/distribution/) to run the code and manage libraries

## Different report types
**Previous month (usually just 1 log file)**
Run the EZProxy-PrevMonth script to capture the data from the previous month (the script formats filenames and HTML based on the previous month)

**Full year (or several log files)**
Run the EZProxy-FY script to capture data for a larger period of time. This one doesn't create a By Day chart/table.

## Required libaries & dependencies
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
**Setup Python**
1. Install Anaconda and ensure that all the libraries/dependencies listed above are included
2. Download files from Google Drive or Github
3. Create a folder in root C:\ called Statistics
4. Unpack files and move into root of C:\Statistics
5. Inside C:\Statistics, create another folder ezproxy_logs.

**Running the script**
1. Copy any number of logs you want to analyze into C:\Statistics\ezproxy_logs
2. Open the Python file you want to run in Spyder (the Python environment for Anaconda)
3. Press the PLAY button and the script will go through the logs.
4. When completed, you'll see the generated charts load in the bottom right console window.

**Opening results**
1. Navigate to C:\Statistics and find the folder the script generated with unpacked log stats.
2. You can delete the [date].csv file generated if you don't want to keep the translated log data.
3. Opening the [date].html file will display the generated charts and table results. The chart graphics are stored in the Charts folder.
