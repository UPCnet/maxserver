from sh import ps
import subprocess
import re

process = 'server.js'
psw = ps.bake('auxww')
lines = psw().stdout
pids = re.findall(r'\n\s*[\w\d]+\s*(\d+).*?%s.*' % process, lines)

command = 'top -p {} -d 0.5 -b'.format(','.join(pids))
print command

proc = subprocess.Popen(command.split(' '), bufsize=1,  stdout=subprocess.PIPE)

pids_stats = {}

while True:
    line = proc.stdout.readline()

    try:
        ff = re.findall(r'[^\s]+', line)
        if ff[0] in pids:
            #pids.setdefault(ff[0], {'max': 0, 'average': None})
            #if pids[pid]['min'] = None
            pid = ff[0]
            res = ff[5]
            cpu = ff[8]
        
            print '%s MEM: %s CPU: %s' % (pid, res, cpu)
    except:
        pass
