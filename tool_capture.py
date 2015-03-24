import webkit2png

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

import sys
import signal




def onLoadFinished(result):
	print "loadFinished(%s)" % str(result)
	if not result:
		sys.exit(0) # this is the moment when we have to quit normally

	webpage.setViewportSize(webpage.mainFrame().contentsSize())
	 
	# Paint this frame into an image
	image = QImage(webpage.viewportSize(), QImage.Format_ARGB32)
	painter = QPainter(image)
	webpage.mainFrame().render(painter)
	painter.end()
	image.save("output.png")

app = QApplication(sys.argv)
signal.signal(signal.SIGINT, signal.SIG_DFL)

webpage = QWebPage()
webpage.connect(webpage, SIGNAL("loadFinished(bool)"), onLoadFinished)
webpage.mainFrame().load(QUrl("http://127.0.0.1/test"))

print 'test!'