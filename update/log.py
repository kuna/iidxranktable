logs = []
def Log(log):
    v = log
    if (isinstance(log,int)):
        v = str(log)
    global logs
    logs.append(v)
    if (len(logs) > 100):
        logs = logs[50:]

def Print(s):
    Log(s)
    print s

def getLogs():
    global logs
    return logs
