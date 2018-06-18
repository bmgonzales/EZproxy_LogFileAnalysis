import re, glob, os
from datetime import date, datetime
import requests
import json
import csv
import pandas as pd
from matplotlib import pyplot as plt

IP_ACCESS_KEY = 'ipstack_access_key'

## Set up
tdy = str(date.today())
year = tdy[2:4]
m = int(tdy[5:7]) - 1
if len(str(m)) == 1:
  month = '0' + str(m)
else:
  month = str(m)
stats = 'EZproxy_' + month + year
stats_title = month + '/' + year

statdirs = 'C:\\Statistics\\' + stats
chartdirs = 'C:\\Statistics\\' + stats + '\\charts\\'

os.makedirs(statdirs)
os.makedirs(chartdirs)

statfile = 'C:\\Statistics\\' + stats + '\\' + stats + '.csv'
htmlfile = 'C:\\Statistics\\' + stats + '\\' + stats + '.html'

output = open(statfile,'w')

userfile = 'C:\\Statistics\\users.csv'
user_reader = csv.reader(open(userfile, 'r'))
users = {}

for user_row in user_reader:
  k, v = user_row
  users[k] = v

dbfile = 'C:\\Statistics\\dblist.csv'
db_reader = csv.reader(open(dbfile, 'r'))
dbs = {}

for db_row in db_reader:
  a, b = db_row
  dbs[a] = b

dblist = list(dbs.keys())

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

output.write('Date,Weekday,Hour,Country,State,City,Location,Status,Requested_url,Referring_url')

ezproxy_logs = 'C:\\Statistics\\ezproxy_logs\\'
ezproxy_stats = []

## Mine stats from EZproxy logfiles
for filename in glob.glob(os.path.join(ezproxy_logs, '*')):
  lines = [line.strip() for line in open(filename)]
  for line in lines:
    log = line.split()
    ip = log[0]
    response = requests.get('http://api.ipstack.com/{0}?access_key={1}'.format(ip, IP_ACCESS_KEY))
    geolocation = json.loads(response.text)
    if geolocation['country_name'] == 'None':
      country = 'Unknown'
    else:
      country = geolocation['country_name']
    if geolocation['region_name'] == 'None':
      state == 'Unknown'
    else:
      state = geolocation['region_name']
    if geolocation['city'] == 'None':
      city == 'Unknown'
    else:
      city = geolocation['city'] + ', ' + geolocation['region_code']
    timestamp = log[1]
    timestamp = timestamp[1:]
    ts = timestamp.split('/')
    ddate = ts[0]
    month = ts[1]
    month_no = months[month]
    yeartime = ts[2]
    year = yeartime[0:4]
    hour = yeartime[5:7]
    weekday_no = datetime(int(year), month_no, int(ddate)).weekday()
    weekday = weekdays[weekday_no]
    username = log[3]
    if username in users:
      status = users[username]
    else:
      status = 'Unknown'
    location = log[7]
    if location == 'local':
      location = 'On Campus'
      country = 'United States'
      state = 'Texas'
      city = 'San Antonio'
    elif location == 'proxy':
      location = 'Off Campus'
    else:
      location = 'Unknown'
    referring_url = log[8]
    referring_url = re.sub('https:\/\/ezproxy.ollusa.edu\/login\?url=', '', referring_url)
    referring_url = re.sub('https:\/\/login.ezproxy.ollusa.edu\/login\?qurl=', '', referring_url)
    referring_url = re.sub('http:\/\/ezproxy.ollusa.edu:2048\/login\?qurl', '', referring_url)
    referring_url = re.sub('.ezproxy.ollusa.edu', '', referring_url)
    referring_url = referring_url.split('=',1)[0]
    referring_url = referring_url.split('%',1)[0]
    ref = 'Unknown'
    if referring_url == '':
      ref = 'EZproxy Login'
    else:
      for x in dblist:
        if x in referring_url:
          ref = dbs[x]
    requested_url = log[5]
    requested_url = re.sub('https:\/\/ezproxy.ollusa.edu\/login\?url=', '', requested_url)
    requested_url = re.sub('https:\/\/login.ezproxy.ollusa.edu\/login\?qurl=', '', requested_url)
    requested_url = re.sub('http:\/\/ezproxy.ollusa.edu:2048\/login\?qurl', '', requested_url)
    requested_url = re.sub('.ezproxy.ollusa.edu', '', requested_url)
    requested_url = requested_url.split('=',1)[0]
    requested_url = requested_url.split('%',1)[0]
    req = 'Unknown'
    if requested_url == '':
      req = 'EZproxy Login'
    else:
      for x in dblist:
        if x in requested_url:
          req = dbs[x]

    output.write('\n')
    output.write(str(ddate) + ',' + str(weekday) + ',' + str(hour) + ',' + str(country) + ',' + str(state) + ',' + str(city) + ',' + str(location) + ',' + str(status) + ',' + str(req) + ',' + str(ref))

output.close()

## Create charts and HTML file
html = open(htmlfile,'w')
html.write('<html><head><title>EZproxy Logfile Analysis - ' + stats_title + '</title><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css"><script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script><style>table{width:65%;}th{display:none;}td{text-align:center;}</style></head><body><div class="container"><h1>EZproxy Logfile Analysis - ' + stats_title + '</h1><br><br>')


df = pd.read_csv(statfile)

byday = df.groupby('Date').Weekday.count().reset_index()
byday = byday.sort_index(ascending=True)
byday.rename(columns={'Date':'Date', 'Weekday':'Sessions'},inplace=True)
byday['Percent'] = byday.Sessions / byday.Sessions.sum()
byday.Percent = byday.Percent.apply(lambda x: str(x)[2:4] + '.' + str(x)[4] + '%')
day_keys = byday.Date.tolist()
day_values = byday.Sessions.tolist()
title1 = 'EZproxy Sessions by Day of Month'

plt.figure(figsize = (8,6))
ax1 = plt.subplot()
plt.barh(range(len(day_values)), day_values, align='center', alpha=0.5, color='#641E16')
ax1.set_yticks(range(len(day_keys)))
ax1.set_yticklabels(day_keys)
ax1.set_xlabel('EZproxy Sessions')
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.title(title1)
plt.savefig(chartdirs + 'byday.png')

html.write('<div class="row"><center><h2>' + title1 + '</h2><img src="charts/byday.png" /><br><br><br>')
html.write(byday.to_html() + '<br><br></div>')

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

bycountry = df.groupby('Country').Date.count().reset_index()
bycountry = bycountry.sort_values('Date',ascending=False)
bycountry.rename(columns={'Country':'Country', 'Date':'Sessions'},inplace=True)
bycountry['Percent'] = bycountry.Sessions / bycountry.Sessions.sum()
bycountry.Percent = bycountry.Percent.apply(lambda x: str(x)[2:4] + '.' + str(x)[4] + '%')
country_keys = bycountry.Country.tolist()
country_values = bycountry.Sessions.tolist()
title4 = 'EZproxy Sessions by Country'

plt.figure(figsize = (8,6))
ax4 = plt.subplot()
plt.barh(range(len(country_values)), country_values, align='center', alpha=0.5, color='#0E6251')
ax4.set_yticks(range(len(country_keys)))
ax4.set_yticklabels(country_keys)
ax4.set_xlabel('EZproxy Sessions')
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.title(title4)
plt.savefig(chartdirs + 'bycountry.png')

html.write('<div class="row"><center><h2>' + title4 + '</h2><img src="charts/bycountry.png" /><br><br><br>')
html.write(bycountry.to_html() + '<br><br></div>')

bystate = df.groupby('State').Date.count().reset_index()
bystate = bystate.sort_values('Date',ascending=False).head(10)
bystate.rename(columns={'State':'State', 'Date':'Sessions'},inplace=True)
bystate['Percent'] = bystate.Sessions / bystate.Sessions.sum()
bystate.Percent = bystate.Percent.apply(lambda x: str(x)[2:4] + '.' + str(x)[4] + '%')
state_keys = bystate.State.tolist()
state_values = bystate.Sessions.tolist()
title5 = 'EZproxy Sessions by State'

plt.figure(figsize = (8,6))
ax5 = plt.subplot()
plt.barh(range(len(state_values)), state_values, align='center', alpha=0.5, color='#7D6608')
ax5.set_yticks(range(len(state_keys)))
ax5.set_yticklabels(state_keys)
ax5.set_xlabel('EZproxy Sessions')
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.title(title5)
plt.savefig(chartdirs + 'bystate.png')

html.write('<div class="row"><center><h2>' + title5 + '</h2><img src="charts/bystate.png" /><br><br><br>')
html.write(bystate.to_html() + '<br><br></div>')

bycity = df.groupby('City').Date.count().reset_index()
bycity = bycity.sort_values('Date',ascending=False).head(10)
bycity.rename(columns={'City':'City', 'Date':'Sessions'},inplace=True)
bycity['Percent'] = bycity.Sessions / bycity.Sessions.sum()
bycity.Percent = bycity.Percent.apply(lambda x: str(x)[2:4] + '.' + str(x)[4] + '%')
city_keys = bycity.City.tolist()
city_values = bycity.Sessions.tolist()
title6 = 'EZproxy Sessions by City'

plt.figure(figsize = (8,6))
ax6 = plt.subplot()
plt.barh(range(len(city_values)), city_values, align='center', alpha=0.5, color='#6E2C00')
ax6.set_yticks(range(len(city_keys)))
ax6.set_yticklabels(city_keys)
ax6.set_xlabel('EZproxy Sessions')
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.title(title6)
plt.savefig(chartdirs + 'bycity.png')

html.write('<div class="row"><center><h2>' + title6 + '</h2><img src="charts/bycity.png" /><br><br><br>')
html.write(bycity.to_html() + '<br><br></div>')

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

bystatus = df.groupby('Status').Date.count().reset_index()
bystatus = bystatus.sort_values('Date',ascending=False)
bystatus.rename(columns={'Status':'Status', 'Date':'Sessions'},inplace=True)
bystatus['Percent'] = bystatus.Sessions / bystatus.Sessions.sum()
bystatus.Percent = bystatus.Percent.apply(lambda x: str(x)[2:4] + '.' + str(x)[4] + '%')
status_keys = bystatus.Status.tolist()
status_values = bystatus.Sessions.tolist()
title8 = 'EZproxy Sessions by OLLU Status'

plt.figure(figsize = (8,6))
ax8 = plt.subplot()
plt.barh(range(len(status_values)), status_values, align='center', alpha=0.5, color='#58D68D')
ax8.set_yticks(range(len(status_keys)))
ax8.set_yticklabels(status_keys)
ax8.set_xlabel('EZproxy Sessions')
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.title(title8)
plt.savefig(chartdirs + 'bystatus.png')

html.write('<div class="row"><center><h2>' + title8 + '</h2><img src="charts/bystatus.png" /><br><br><br>')
html.write(bystatus.to_html() + '</div>')

req_urls = df.groupby('Requested_url').Date.count().reset_index()
req_urls = req_urls.sort_values('Date',ascending=False)
req_urls.rename(columns={'Requested_url':'Requested_url', 'Date':'Sessions'},inplace=True)
req_urls['Percent'] = req_urls.Sessions / req_urls.Sessions.sum()
req_urls.Percent = req_urls.Percent.apply(lambda x: str(x)[2:4] + '.' + str(x)[4] + '%')
req_keys = req_urls.Requested_url.tolist()
req_values = req_urls.Sessions.tolist()
title9 = 'Requested URLs'

plt.figure(figsize = (8,6))
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

ref_urls = df.groupby('Referring_url').Date.count().reset_index()
ref_urls = ref_urls.sort_values('Date',ascending=False)
ref_urls.rename(columns={'Referring_url':'Referring_url', 'Date':'Sessions'},inplace=True)
ref_urls['Percent'] = ref_urls.Sessions / ref_urls.Sessions.sum()
ref_urls.Percent = ref_urls.Percent.apply(lambda x: str(x)[2:4] + '.' + str(x)[4] + '%')
ref_keys = ref_urls.Referring_url.tolist()
ref_values = ref_urls.Sessions.tolist()
title10 = 'Referring URLs'

plt.figure(figsize = (8,6))
ax10 = plt.subplot()
plt.barh(range(len(ref_values)), ref_values, align='center', alpha=0.5, color='#3498DB')
ax10.set_yticks(range(len(ref_keys)))
ax10.set_yticklabels(ref_keys)
ax10.set_xlabel('EZproxy Sessions')
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.title(title10)
plt.savefig(chartdirs + 'ref.png')

html.write('<div class="row"><center><h2>' + title10 + '</h2><img src="charts/ref.png" /><br><br><br>')
html.write(ref_urls.to_html() + '<br><br></div>')


html.write('</div></body></html>')
html.close()
