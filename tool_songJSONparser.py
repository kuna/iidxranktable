import io, json
import jsondata

def parseAndSave(url, outfile):
	print "%s parsing..." % url

	parsedata = jsondata.loadJSONurl(url)

	# remove scores
	del parsedata['userdata']
	del parsedata['status']
	for music in parsedata['musicdata']:
		del music['clear']
		del music['score']
		del music['miss']

	with io.open(outfile, 'wb') as f:
		f.write(json.dumps(parsedata).decode('utf8'))
		f.close()
		print "done!"

parseAndSave("http://json.iidx.me/delmitz/dp/level/8", "./data/song.dp.8.json")
parseAndSave("http://json.iidx.me/delmitz/dp/level/9", "./data/song.dp.9.json")
parseAndSave("http://json.iidx.me/delmitz/dp/level/10", "./data/song.dp.10.json")
parseAndSave("http://json.iidx.me/delmitz/dp/level/11", "./data/song.dp.11.json")
parseAndSave("http://json.iidx.me/delmitz/dp/level/12", "./data/song.dp.12.json")

parseAndSave("http://json.iidx.me/delmitz/sp/level/8", "./data/song.sp.8.json")
parseAndSave("http://json.iidx.me/delmitz/sp/level/9", "./data/song.sp.9.json")
parseAndSave("http://json.iidx.me/delmitz/sp/level/10", "./data/song.sp.10.json")
parseAndSave("http://json.iidx.me/delmitz/sp/level/11", "./data/song.sp.11.json")
parseAndSave("http://json.iidx.me/delmitz/sp/level/12", "./data/song.sp.12.json")