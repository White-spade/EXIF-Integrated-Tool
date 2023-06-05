import sys
import EXIFA_UIsetter
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Win(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dragNdrop = EXIFA_UIsetter.Uisetter()
        self.intitUI()
        self.show()

    def intitUI(self):
        #Application Title, Icon, Size
        self.setWindowTitle('EXIF Analyzer')
        self.setWindowIcon(QIcon('Dcon.png'))
        self.resize(1100, 700)

        #전체 Application의 스크롤을 가능하도록 설정
        sc_area = QScrollArea()
        sc_area.setWidget(self.dragNdrop)
        sc_area.setWidgetResizable(True)
        self.setCentralWidget(sc_area)
        self.setAcceptDrops(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Win()
    sys.exit(app.exec_()) 
