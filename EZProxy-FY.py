import re, glob, os
from datetime import date, datetime
import csv
import pandas as pd
from matplotlib import pyplot as plt

## Get the date
tdy = str(date.today())
year = tdy[2:4]
m = int(tdy[5:7]) 
if len(str(m)) == 1:
  month = '0' + str(m)
else:
  month = str(m)

# Create variables for filenames and titles
stats = 'EZproxy_20' + year
stats_title = '20' + year + ' YTD'

# Location of directories to create for report files
statdirs = 'C:\\Statistics\\' + stats
chartdirs = 'C:\\Statistics\\' + stats + '\\charts\\'

# Create the directories for report files
os.makedirs(statdirs)
os.makedirs(chartdirs)

# Create files for report file and pretty log
statfile = 'C:\\Statistics\\' + stats + '\\' + stats + '.csv'
htmlfile = 'C:\\Statistics\\' + stats + '\\' + stats + '.html'

# Open statfile to unpack
output = open(statfile,'w')

# Find userfile and open
userfile = 'C:\\Statistics\\users.csv'
user_reader = csv.reader(open(userfile, 'r'))
users = {}

# Create user array
# We don't use this, but left the code and file intact just in case
for user_row in user_reader:
  k, v = user_row
  users[k] = v

# Find database file and open
dbfile = 'C:\\Statistics\\dblist.csv'
db_reader = csv.reader(open(dbfile, 'r'))

# Create database array
dbs = {}

for db_row in db_reader: # For each row in the dblist.csv
  a, b = db_row # Looks for rows in this format: URL key,Database Name i.e. EBSCOHost.com,EBSCO
  dbs[a] = b

# Create keys for each row in database array to match with log
dblist = list(dbs.keys())

# Create weekday array list and months array list to translate for pretty log
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

# Write row title for pretty log
# IMPORTANT - This is used to identify columns for charts and tables
output.write('Date,Weekday,Hour,IP,Location,Requested_url')

# Find the EZProxy log folder to unpack
ezproxy_logs = 'C:\\Statistics\\ezproxy_logs\\'
ezproxy_stats = []

## Unpack stats from EZproxy logfiles
for filename in glob.glob(os.path.join(ezproxy_logs, '*')):
  lines = [line.strip() for line in open(filename)]
  for line in lines:
    log = line.split()
    
## IP
    ip = log[0] # IP address is in log array position 0 (first)

## date - weekday - hour
    timestamp = log[1] # Timestamp is in log array position 1
    timestamp = timestamp[1:] # Creates array of timestamp data to further split
    ts = timestamp.split('/')
    ddate = ts[0]
    month = ts[1]
    month_no = months[month]
    yeartime = ts[2]
    year = yeartime[0:4]
    hour = yeartime[5:7]
    weekday_no = datetime(int(year), month_no, int(ddate)).weekday()
    weekday = weekdays[weekday_no]

## username
    username = log[3] # If found gets username from log array position 3 - This includes library card numbers; we aren't using this data for any reports

## location
    location = log [6]  # Gets location from log array position 6 - EZProxy writes local or proxy
    if location == 'local': # Location is local if proxy wasn't used - checks blacklist IP range from EZProxy config
      location = 'In Library' # Give a prettier name to local users
    elif location == 'proxy': # Location is proxy if EZProxy was used
      location = 'Not In Library' # Give a prettier name to proxy users
    else:
      location = 'Unknown'  # If neither is provided - likely to occur in old log files
      
## requested_url   
    requested_url = log[5] # Gets requested database URL from log array position 5
    requested_url = re.sub('https:\/\/ezproxy1.salpublib.org\/login\?url=', '', requested_url)
    requested_url = re.sub('https:\/\/ezproxy1.salpublib.org\/login\?qurl=', '', requested_url)
    requested_url = re.sub('http:\/\/ezproxy1.salpublib.org:2048\/login\?qurl', '', requested_url)
    requested_url = re.sub('.ezproxy1.salpublib.org', '', requested_url)
# Breaks down the URL further. Commenting out to allow us to take bits of the way further down identifiers for databases
#    requested_url = requested_url.split('=',1)[0]
#    requested_url = requested_url.split('%',1)[0]
    req = 'Unknown'
    if requested_url == '':
      req = 'EZproxy Login'
    else:
      for x in dblist: # Checks for URL key from dblist.csv
        if x in requested_url:
          req = dbs[x]

# Create new line
# Write translated data from old log file to new log file
    output.write('\n')
    output.write(str(ddate) + ',' + str(weekday) + ',' + str(hour) + ',' + str(ip) + ',' + str(location) + ',' + str(req))

# Close new log file
output.close()

## Create charts and HTML file
html = open(htmlfile,'w')
html.write('<html><head><title>EZproxy Logfile Analysis - ' + stats_title + '</title><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css"><script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script><style>table{width:65%;}th{display:none;}td{text-align:center;}</style></head><body><div class="container"><h1>EZproxy Logfile Analysis - ' + stats_title + '</h1><br><br>')


df = pd.read_csv(statfile)

# Unique IP address count
ip_count = df["IP"].nunique()
title11 = 'Unique Users by IP'
html.write('<div class="row"><center><h2>' + title11 + '</h2><br>')
html.write(str(ip_count) + '<br><br></div>')

# Removed ByDay chart/table

# ByWeekDay chart/table
days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
byweekday = df.groupby('Weekday').Date.count().reindex(days).reset_index()
byweekday = byweekday.sort_index(ascending=True)
byweekday.rename(columns={'Weekday':'Weekday', 'Date':'Sessions'},inplace=True)
byweekday['Percent'] = byweekday.Sessions / byweekday.Sessions.sum()
byweekday.Percent = byweekday.Percent.apply(lambda x: str(x)[2:4] + '.' + str(x)[4] + '%')
weekday_keys = byweekday.Weekday.tolist()
weekday_values = byweekday.Sessions.tolist()
title2 = 'EZproxy Sessions by Weekday'

plt.figure(figsize = (8,6))
ax2 = plt.subplot()
plt.barh(range(len(weekday_values)), weekday_values, align='center', alpha=0.5, color='#4A235A')
ax2.set_yticks(range(len(weekday_keys)))
ax2.set_yticklabels(weekday_keys)
ax2.set_xlabel('EZproxy Sessions')
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.title(title2)
plt.savefig(chartdirs + 'byweekday.png')

html.write('<div class="row"><center><h2>' + title2 + '</h2><img src="charts/byweekday.png" /><br><br><br>')
html.write(byweekday.to_html() + '<br><br></div>')

# ByHour chart/table
byhour = df.groupby('Hour').Date.count().reset_index()
byhour = byhour.sort_index(ascending=True)
byhour.rename(columns={'Hour':'Hour', 'Date':'Sessions'},inplace=True)
byhour['Percent'] = byhour.Sessions / byhour.Sessions.sum()
byhour.Percent = byhour.Percent.apply(lambda x: str(x)[2:4] + '.' + str(x)[4] + '%')
hour_keys = byhour.Hour.tolist()
hour_values = byhour.Sessions.tolist()
title3 = 'EZproxy Sessions by Hour'

plt.figure(figsize = (8,6))
ax3 = plt.subplot()
plt.barh(range(len(hour_values)), hour_values, align='center', alpha=0.5, color='#154360')
ax3.set_yticks(range(len(hour_keys)))
ax3.set_yticklabels(hour_keys)
ax3.set_xlabel('EZproxy Sessions')
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.title(title3)
plt.savefig(chartdirs + 'byhour.png')

html.write('<div class="row"><center><h2>' + title3 + '</h2><img src="charts/byhour.png" /><br><br><br>')
html.write(byhour.to_html() + '<br><br></div>')

# Removed ByCountry chart/table

# Removed ByState chart/table

# Removed ByCity chart/table

# ByLocation chart/table
bylocation = df.groupby('Location').Date.count().reset_index()
bylocation = bylocation.sort_values('Date',ascending=False)
bylocation.rename(columns={'Location':'Location', 'Date':'Sessions'},inplace=True)
bylocation['Percent'] = bylocation.Sessions / bylocation.Sessions.sum()
bylocation.Percent = bylocation.Percent.apply(lambda x: str(x)[2:4] + '.' + str(x)[4] + '%')
location_keys = bylocation.Location.tolist()
location_values = bylocation.Sessions.tolist()
title7 = 'EZproxy Sessions by Location'

plt.figure(figsize = (8,6))
ax7 = plt.subplot()
plt.barh(range(len(location_values)), location_values, align='center', alpha=0.5, color='#34495E')
ax7.set_yticks(range(len(location_keys)))
ax7.set_yticklabels(location_keys)
ax7.set_xlabel('EZproxy Sessions')
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.title(title7)
plt.savefig(chartdirs + 'bylocation.png')

html.write('<div class="row"><center><h2>' + title7 + '</h2><img src="charts/bylocation.png" /><br><br><br>')
html.write(bylocation.to_html() + '<br><br></div>')

# Removed ByStatus chart/table

# Requested_URL chart/able
req_urls = df.groupby('Requested_url').Date.count().reset_index()
req_urls = req_urls.sort_values('Date',ascending=False)
req_urls.rename(columns={'Requested_url':'Requested_url', 'Date':'Sessions'},inplace=True)
req_urls['Percent'] = req_urls.Sessions / req_urls.Sessions.sum()
req_urls.Percent = req_urls.Percent.apply(lambda x: str(x)[2:4] + '.' + str(x)[4] + '%')
req_keys = req_urls.Requested_url.tolist()
req_values = req_urls.Sessions.tolist()
title9 = 'Requested URLs'

plt.figure(figsize = (10,16))
ax9 = plt.subplot()
plt.barh(range(len(req_values)), req_values, align='center', alpha=0.5, color='#F1948A')
ax9.set_yticks(range(len(req_keys)))
ax9.set_yticklabels(req_keys)
ax9.set_xlabel('EZproxy Sessions')
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.title(title9)
plt.savefig(chartdirs + 'req.png')

html.write('<div class="row"><center><h2>' + title9 + '</h2><br><img src="charts/req.png" /><br>')
html.write(req_urls.to_html() + '<br><br></div>')

# Removed Referring_URLs chart/table

html.write('</div></body></html>')
html.close()
