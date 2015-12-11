logs = []
def Log(log):
	global logs
	logs.append(str(log))
	if (len(logs) > 100):
		logs = logs[50:]

def Print(s):
	Log(s)
	print s

def getLogs():
	global logs
	return logs
