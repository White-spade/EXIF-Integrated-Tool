import os
import EXIFA_Classes
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Uisetter(QWidget):

    def __init__(self):
        super().__init__()
        self.dragNdrop = EXIFA_Classes.DragNDrop()
        self.initUI()
        
    def initUI(self):
        
        #File Tree UI Setting
        self.now_path = str(os.getcwd())
        self.model_file_system = QFileSystemModel()
        self.model_file_system.setRootPath(self.now_path)
        self.model_file_system.setReadOnly(False)

        self.tree_view = EXIFA_Classes.FileTreeView()
        self.tree_view.setModel(self.model_file_system)
        self.tree_view.setRootIndex(self.model_file_system.index(self.now_path))
        self.tree_view.doubleClicked.connect(lambda index : self.item_double_clicked(index))

        self.tree_view.setDragEnabled(True)
        self.tree_view.setColumnWidth(0, 300)

        backbtn = QPushButton("Go Parent Directory")
        backbtn.clicked.connect(self.go_parent_dir)

        fileLO = QVBoxLayout()
        fileLO.addWidget(backbtn)
        fileLO.addWidget(self.tree_view)


        #Drag N Drop, Image Parsing UI setting
        btn = QPushButton('Browse')
        btn.clicked.connect(self.dragNdrop.open_image)

        ImgLO = QVBoxLayout()
        ImgLO.addWidget(self.dragNdrop.photo)
        ImgLO.addWidget(btn)
        
        BasicLO = QVBoxLayout()
        BasicLO.addWidget(self.dragNdrop.ImgAnalyze.basLb)

        Img_BasicLO = QVBoxLayout()
        Img_BasicLO.addLayout(ImgLO, stretch=1)
        Img_BasicLO.addLayout(BasicLO, stretch=2)

        PrmptCopyBtn = QPushButton("Copy [Gendration Prompt]")
        PrmptCopyBtn.clicked.connect(lambda : QClipboard.setText(QGuiApplication.clipboard(),self.dragNdrop.ImgAnalyze.AiAnalyze.prmptLb.text().replace("[Generate Prompts]\n\n","")))
        NgPrmptCopyBtn = QPushButton("Copy [Negative Prompt]")
        NgPrmptCopyBtn.clicked.connect(lambda : QClipboard.setText(QGuiApplication.clipboard(),self.dragNdrop.ImgAnalyze.AiAnalyze.ngPrmptLb.text().replace("[Negative Prompts]\n\n","")))
        OptionLO = QVBoxLayout()
        OptionLO.addWidget(PrmptCopyBtn)
        OptionLO.addWidget(self.dragNdrop.ImgAnalyze.AiAnalyze.prmptLb)
        OptionLO.addWidget(NgPrmptCopyBtn)
        OptionLO.addWidget(self.dragNdrop.ImgAnalyze.AiAnalyze.ngPrmptLb)
        OptionLO.addWidget(self.dragNdrop.ImgAnalyze.AiAnalyze.optLb)


        #Frame & Splitters Setting
        frame_0 = QFrame()
        frame_0.setFrameShape(QFrame.Panel | QFrame.Plain)
        frame_2 = QFrame()
        frame_2.setFrameShape(QFrame.Panel | QFrame.Plain)
        frame_3 = QFrame()
        frame_3.setFrameShape(QFrame.Panel | QFrame.Plain)

        frame_0.setLayout(fileLO)
        frame_2.setLayout(Img_BasicLO)
        frame_3.setLayout(OptionLO)

        mspliter = QSplitter(Qt.Horizontal)
        mspliter.addWidget(frame_0)
        mspliter.addWidget(frame_2)
        mspliter.addWidget(frame_3)

        #[파일트리 : 일반 EXIF분석기 : AI분석기] 의 비율을 [2:5:3] 으로 설정
        mspliter.setSizes([int(mspliter.size().width() * 0.2),int(mspliter.size().width() * 0.5), int(mspliter.size().width() * 0.3)])

        #전체 레이아웃인 QHBOX Mlo(Main Lay out) 을 self.layout으로 설정, Main py에 전달한다
        Mlo =  QHBoxLayout()
        Mlo.addWidget(mspliter)
        self.setAcceptDrops(True)
        self.dragNdrop.setAcceptDrops(True)
        self.setLayout(Mlo)


    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            filename = event.mimeData().urls()[0].toLocalFile()
            event.accept()
            self.dragNdrop.ImgAnalyze.analyize_image(filename)
            self.dragNdrop.open_image(filename)
        else:
            event.ignore()

    def item_double_clicked(self, index):
        if(os.path.isfile(self.model_file_system.filePath(index))):
            #file이 Img인지는 open_image 함수 안에서 처리해준다
            self.dragNdrop.open_image(self.model_file_system.filePath(index))

        elif(os.path.isdir(self.model_file_system.filePath(index))):
            self.now_path = self.model_file_system.index(self.model_file_system.filePath(index))
            self.tree_view.setRootIndex(self.now_path)

        else:
            return
        
    def go_parent_dir(self):
        if(isinstance(self.now_path, str)):
            self.now_path = os.path.abspath(os.path.join(self.now_path, os.pardir))
            self.model_file_system.setRootPath(self.now_path)
            self.tree_view.setRootIndex(self.model_file_system.index(self.now_path))
        else:
            self.now_path = self.now_path.parent()
            self.tree_view.setRootIndex(self.now_path)