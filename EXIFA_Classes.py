import os
import exiftool
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class DragNDrop(QWidget):

    def __init__(self):
        super().__init__()
        self.photo = PhotoLabel()
        self.ImgAnalyze = ImgAnalyze()

        self.setAcceptDrops(True)
        self.photo.setAcceptDrops(True)
        self.ImgAnalyze.setAcceptDrops(True)

        self.imglist = [".jpg",".jpeg",".png",".webp"]

    def open_image(self, filename=None):
        if not filename:
            filename, _ = QFileDialog.getOpenFileName(self, 'Select Photo', QDir.currentPath(), 'Images (*.png *.jpg)')
            if not filename:
                return
        #여기에 filename 처리기 넣어줘야 함
        if(os.path.splitext(filename)[1] not in self.imglist):
            self.photo.setText("Please put [.jpg .jpeg .png .webp] file")
            self.photo.setAlignment(Qt.AlignCenter)
            self.ImgAnalyze.AiAnalyze.prmptLb.setText("")
            self.ImgAnalyze.AiAnalyze.ngPrmptLb.setText("")
            return
        self.ImgAnalyze.analyize_image(filename)
        imgpix = QPixmap(filename)
        if(imgpix.width() >= imgpix.height()):
            self.photo.setPixmap(imgpix.scaled(int(self.width()/2),int(self.height()/2), Qt.KeepAspectRatio))
        else:
            self.photo.setPixmap(imgpix.scaledToWidth(int(self.width()/2)))


class PhotoLabel(QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumWidth(100)
        self.setText('\n\n Drop Image Here \n\n')
        self.setStyleSheet('''
        QLabel {
            border: 4px dashed #aaa;
        }''')

    def setPixmap(self, *args, **kwargs):
        super().setPixmap(*args, **kwargs)
        self.setStyleSheet('''
        QLabel {
            border: none;
        }''')


class FileTreeView(QTreeView):
    def __init__(self):
        super(QTreeView, self).__init__()

    def edit(self, index, trigger, event):
        return True


class ImgAnalyze(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.AiAnalyze = AiAnalyze()
        self.AiAnalyze.setAcceptDrops(True)

        #분석 결과 표시 라벨
        self.basLb = QLabel()
        self.basLb.setAlignment(Qt.AlignCenter)
        self.basLb.setText('\n\n Basic Image Informations \n\n')
        self.basLb.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
    
    def analyize_image(self, filename=None):
        if not filename:
            return
        parseData=""
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(filename)
            if "PNG:Parameters" in metadata[0]:
                self.AiAnalyze.analyze_PngAi(metadata[0])
                del metadata[0]["PNG:Parameters"]
            elif "EXIF:UserComment" in metadata[0]:
                self.AiAnalyze.analyze_WebpJpgAi(metadata[0])
                del metadata[0]["EXIF:UserComment"]
            else:
                self.AiAnalyze.prmptLb.setText("")
                self.AiAnalyze.ngPrmptLb.setText("")
                self.AiAnalyze.optLb.setText("Not an AI image\nOr\nNot generated by Stable diffusion\nOr\nEXIF may have been lost"+
                "\n\nIf you don't to use this\nYou can drag to close this")
                self.AiAnalyze.optLb.setAlignment(Qt.AlignCenter)

            for content in metadata[0]:
                parseData = (parseData+str(content)+" : "+str(metadata[0][content])+"\n\n")

        self.basLb.setText(parseData)
        self.basLb.setAlignment(Qt.AlignLeft)


class AiAnalyze(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initLabels()
    
    def initLabels(self):
        #Generation Prompt Label
        self.prmptLb = QLabel()
        self.prmptLb.setAlignment(Qt.AlignCenter)
        self.prmptLb.setText("No data")
        self.prmptLb.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.prmptLb.setMaximumWidth(400)
        self.prmptLb.setWordWrap(True)

        #Negative Prompt Label
        self.ngPrmptLb = QLabel()
        self.ngPrmptLb.setAlignment(Qt.AlignCenter)
        self.ngPrmptLb.setText("No data")
        self.ngPrmptLb.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.ngPrmptLb.setMaximumWidth(400)
        self.ngPrmptLb.setWordWrap(True)

        #Generation Environment Options
        self.optLb = QLabel()
        self.optLb.setAlignment(Qt.AlignCenter)
        self.optLb.setText("[AI parameters]\n\n"+"If you don't to use this\nYou can drag to close this")
        self.optLb.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.optLb.setMaximumWidth(400)
        self.optLb.setWordWrap(True)

    def analyze_PngAi(self, metaDict):
        Aiset = metaDict['PNG:Parameters']
        if 'Negative prompt:' not in Aiset:
            self.optLb.setText("Not an AI image\nOr\nNot generated by Stable diffusion\nOr\nEXIF may have been lost"+
                "\n\nBut have PNG Parameters\n\n"+str(Aiset))
            self.optLb.setAlignment(Qt.AlignCenter)
            self.prmptLb.setText("")
            self.ngPrmptLb.setText("")
            return

        #set Generate Prompts
        getPrmpt = Aiset.split('Negative prompt:')
        self.prmptLb.setText("[Generate Prompts]\n\n"+str(getPrmpt[0]).strip())

        #set Negative Prompts
        negPrmpt = getPrmpt[1].split("Steps:")
        self.ngPrmptLb.setText("[Negative Prompts]\n\n"+str(negPrmpt[0]).strip())

        #Set Generation Environment Options
        gen_env = negPrmpt[1].split(',')
        parseData="[Generation environment]\n\nSteps:"
        for envs in gen_env:
            parseData = (parseData+str(envs).strip()+"\n")
        self.optLb.setText(parseData)
        self.optLb.setAlignment(Qt.AlignLeft)

    def analyze_WebpJpgAi(self, metaDict):
        Aiset = metaDict['EXIF:UserComment']
        if 'Negative prompt:' not in Aiset:
            self.optLb.setText("Not an AI image\nOr\nNot generated by Stable diffusion\nOr\nEXIF may have been lost"+
                "\n\nBut have EXIF UserComments\n\n"+str(Aiset))
            self.optLb.setAlignment(Qt.AlignCenter)
            self.prmptLb.setText("")
            self.ngPrmptLb.setText("")
            return
        #set Generate Prompts
        getPrmpt = Aiset.split('Negative prompt:')
        self.prmptLb.setText("[Generate Prompts]\n\n"+str(getPrmpt[0]).strip())

        #set Negative Prompts
        negPrmpt = getPrmpt[1].split("Steps:")
        self.ngPrmptLb.setText("[Negative Prompts]\n\n"+str(negPrmpt[0]).strip())

        #Set Generation Environment Options
        gen_env = negPrmpt[1].split(',')
        parseData="[Generation environment]\n\nSteps:"
        for envs in gen_env:
            parseData = (parseData+str(envs).strip()+"\n")
        self.optLb.setText(parseData)
        self.optLb.setAlignment(Qt.AlignLeft)