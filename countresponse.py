import re
from operator import itemgetter

def process_log(log):
    statcodes = get_logdata(log)
    status = get_status(statcodes)
    totals = status_occur(status)
    return totals

def get_logdata(f):
    log_line = f.read()
    pat = (r''
           '(\d+.\d+.\d+.\d+)\s-\s-\s' #IP address
           '\[(.+)\]\s' #datetime
           '"GET\s(.+)\s\w+/.+"\s' #requested file
           '(\d+)\s' #status
           '(\d+)\s' #bandwidth
           '"(.+)"\s' #referrer
           '"(.+)"' #user agent
        )
    logdata = find(pat, log_line)
    return logdata

def find(pat, text):
    match = re.findall(pat, text)
    if match:
        return match
    return False

def get_status(logdata):
    #get status codes with stat
    stat_code = []
    for stat in logdata:
        # stat[3] for status match, change to
        # data you want to count totals
        stat_code.append(stat[3])
    return stat_code

def status_occur(status):
    # status codes ocurrences
    d = {}
    for status in status:
        d[status] = d.get(status,0)+1
    return d

#nginx access log, standard format
log_file = open('/var/log/nginx/access.log', 'r')
# return dict of status and total response codes
stat_with_counts = process_log(log_file)
# sort them by total response codes descending
sorted_by_count = sorted(stat_with_counts.items(), key=itemgetter(1), reverse=True)
for stat, occur in sorted_by_count:
   print stat , "-" , occur
