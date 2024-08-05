#!/usr/bin/python
# -*-coding:Utf-8 -*
"""
"""
import sys,os
import json
from smartcard.scard import *
import smartcard.util
from modules import constant
from modules import tools
#from PyQt5.QtWidgets import *
#from PyQt5.QtCore import *
#from PyQt5.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
pyqtSignal=Signal #translate pyqt to Pyside

# Generic app container     
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
    
"""
App configuration
"""
__title__="Morphee lecteur de carte"
__version__="v0.1"    
#style_path = resource_path("resources\\style.txt")
__icon__=resource_path("resources/logo.png")

class MorpheeCardEncoder(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.width=650
        self.height=700
        
        self.resize(self.width, self.height)
        self.setWindowIcon(QIcon('resources/logo.png'))
        self.setWindowTitle('Morphee lecteur de carte')
        
        #center window on screen
        qr = self.frameGeometry()
        cp = QScreen().availableGeometry().center()
        qr.moveCenter(cp)
        
        #init layout
        centralwidget = QWidget(self)
        centralLayout=QHBoxLayout(centralwidget)
        self.setCentralWidget(centralwidget)
        
        #add connect group
        self.connectgrp=GroupClass(self)
        centralLayout.addWidget(self.connectgrp)
        
class CustomDialog(QDialog):
    def __init__(self, title, message):
        super().__init__()

        self.setWindowTitle(title)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.accepted.connect(self.accept)
        #self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(message)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class GroupClass(QGroupBox):
    def __init__(self,widget,title="Connection Configuration"):
        super().__init__(widget)
        self.widget=widget
        self.updateView = True
        self.style = ['music', 'zen', 'relax', 'love']
        self.animation = ['none', 'sparkpulse']
        self.init()
        self.updateViewChanged()

    def init(self):
        #self.setTitle(self.title)

        self.fields=QGridLayout()
        self.fields.setColumnMinimumWidth(0, 110)
        self.fields.setColumnMinimumWidth(0, 110)
        
        idxLine = 0
          
        self.readBtn = QPushButton("Decode")
        self.fields.addWidget(self.readBtn,idxLine,0,1,2)
        self.readBtn.clicked.connect(self.readCard)

        idxLine += 1
        styleLbl = QLabel("Style:")
        self.styleBox=QComboBox()
        self.styleBox.addItems(self.style)
        self.styleBox.setCurrentIndex(0)
        self.styleBox.currentTextChanged.connect(self.updateViewChanged)
        self.fields.addWidget(styleLbl,idxLine,0,1,1)
        self.fields.addWidget(self.styleBox,idxLine,1,1,1)

        idxLine += 1
        animLbl = QLabel("Animation:")        
        self.animBox=QComboBox()
        self.animBox.addItems(self.animation)
        self.animBox.setCurrentIndex(0)
        self.animBox.currentTextChanged.connect(self.updateViewChanged)
        self.fields.addWidget(animLbl,idxLine,0,1,1)
        self.fields.addWidget(self.animBox,idxLine,1,1,1)

        idxLine += 1
        pictoLbl = QLabel("Picto:")
        self.pictoEdit = QLineEdit("")
        self.pictoEdit.textChanged.connect(self.updateViewChanged)
        self.fields.addWidget(pictoLbl,idxLine,0,1,1)
        self.fields.addWidget(self.pictoEdit,idxLine,1,1,1)

        idxLine += 1
        sayLbl = QLabel("Titre parlé:")
        self.sayEdit = QLineEdit("")
        self.sayEdit.textChanged.connect(self.updateViewChanged)
        self.fields.addWidget(sayLbl,idxLine,0,1,1)
        self.fields.addWidget(self.sayEdit,idxLine,1,1,1)

        idxLine += 1
        urlLbl = QLabel("Url:")
        self.urlEdit = QLineEdit("")
        self.urlEdit.textChanged.connect(self.updateViewChanged)
        self.fields.addWidget(urlLbl,idxLine,0,1,1)
        self.fields.addWidget(self.urlEdit,idxLine,1,1,1)

        idxLine += 1
        self.keepLbl = QLabel("Pistes à garder:")
        self.keepSlider = QSlider(Qt.Orientation.Horizontal)
        self.keepSlider.setRange(1,100)
        self.keepSlider.setSingleStep(1)
        self.keepSlider.valueChanged.connect(self.keepSliderChanged)
        self.fields.addWidget(self.keepLbl,idxLine,0,1,1)
        self.fields.addWidget(self.keepSlider,idxLine,1,1,1)
        #keepSlider.sliderMoved.connect(self.slider_position)
        #keepSlider.sliderPressed.connect(self.slider_pressed)
        #keepSlider.sliderReleased.connect(self.slider_released)

        idxLine += 1
        self.limitLbl = QLabel("Temps limit (min): 2600")
        self.limitSlider = QSlider(Qt.Orientation.Horizontal)
        self.limitSlider.setRange(1,3600)
        self.limitSlider.setSingleStep(1)
        self.limitSlider.valueChanged.connect(self.limitSliderChanged)
        self.fields.addWidget(self.limitLbl,idxLine,0,1,1)
        self.fields.addWidget(self.limitSlider,idxLine,1,1,1)
        #limitSlider.sliderMoved.connect(self.slider_position)
        #limitSlider.sliderPressed.connect(self.slider_pressed)
        #limitSlider.sliderReleased.connect(self.slider_released)

        idxLine += 1
        onceLbl = QLabel("Unique:")
        self.onceCheckBox = QCheckBox()
        self.onceCheckBox.setCheckState(Qt.CheckState.Checked)
        self.onceCheckBox.stateChanged.connect(self.updateViewChanged)
        self.fields.addWidget(onceLbl,idxLine,0,1,1)
        self.fields.addWidget(self.onceCheckBox,idxLine,1,1,1)

        idxLine += 1
        shuffleLbl = QLabel("Aléatoire:")
        self.shuffleCheckBox = QCheckBox()
        self.shuffleCheckBox.setCheckState(Qt.CheckState.Unchecked)
        self.shuffleCheckBox.stateChanged.connect(self.updateViewChanged)
        self.fields.addWidget(shuffleLbl,idxLine,0,1,1)
        self.fields.addWidget(self.shuffleCheckBox,idxLine,1,1,1)

        idxLine += 1
        loopLbl = QLabel("Boucle:")
        self.loopCheckBox = QCheckBox()
        self.loopCheckBox.setCheckState(Qt.CheckState.Unchecked)
        self.loopCheckBox.stateChanged.connect(self.updateViewChanged)
        self.fields.addWidget(loopLbl,idxLine,0,1,1)
        self.fields.addWidget(self.loopCheckBox,idxLine,1,1,1)
      
        idxLine += 1
        datasLbl = QLabel("Données")
        self.datas = QTextEdit("")
        self.fields.addWidget(datasLbl,idxLine,0,1,1)
        self.fields.addWidget(self.datas,idxLine,1,1,1)


        idxLine += 1
        consoleLbl = QLabel("Log")
        self.console = QTextEdit("")
        self.fields.addWidget(consoleLbl,idxLine,0,1,1)
        self.fields.addWidget(self.console,idxLine,1,1,1)

        idxLine += 1
        self.writeBtn = QPushButton("Encode")
        self.writeBtn.clicked.connect(self.writeCard)
        self.fields.addWidget(self.writeBtn,idxLine,0,1,1)

        self.setLayout(self.fields)

    def updateViewChanged(self):
        if self.updateView:
            payload_object = {
                "anim": self.animBox.currentText(),
                "style": self.styleBox.currentText(),
                "picto": self.pictoEdit.text(),
                "once": self.onceCheckBox.isChecked(),
                "shuffle": self.shuffleCheckBox.isChecked(),
                "loop": self.loopCheckBox.isChecked(),
                "keep": self.keepSlider.value(),
                "limit": self.limitSlider.value(),
                "say": self.sayEdit.text(),
                "url": self.urlEdit.text()
            }
            
            self.datas.setText(json.dumps(payload_object, indent=2))      
            payload = json.dumps(payload_object)
            json_payload_bytes = smartcard.util.toASCIIBytes(payload)

    def keepSliderChanged(self):
        value = self.keepSlider.value()
        self.keepLbl.setText("Pistes à garder: " + str(value))
        self.updateViewChanged()
          
    def limitSliderChanged(self):
        value = self.limitSlider.value()
        self.limitLbl.setText("Temps limit (min): " + str(value))
        self.updateViewChanged()

    def readBlock(self, block):
        
        datas = []
        success = True
        message = ''
        
        hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
        
        if hresult == SCARD_S_SUCCESS:
        
          hresult, readers = SCardListReaders(hcontext, [])
        
          if len(readers) > 0:
        
            reader = readers[0]
        
            hresult, hcard, dwActiveProtocol = SCardConnect(
                hcontext,
                reader,
                SCARD_SHARE_SHARED,
                SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
        
            if hresult == SCARD_S_SUCCESS:
        
              # get id
              #hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0xCA,0x00,0x00,0x00])
        
              # load key
              hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0x82,0x00,0x00,0x06,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])
              if hresult == SCARD_S_SUCCESS:
        
                for sub in range(0, 3):
        
                  #auth block
                  hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0x86,0x00,0x00,0x05,0x01,0x00,int(block + sub),0x60,0x00])
                  if hresult == SCARD_S_SUCCESS:

                    self.console.append('Lecture du bloc: ' + str(block + sub))

                    hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF, 0xB0, 0x00, int(block + sub), 0x10])
                    if hresult == SCARD_S_SUCCESS:

                      response.pop()
                      response.pop()

                      datas.extend(response)

                      self.console.append(' - datas : ' + smartcard.util.toASCIIString(datas))
                      self.console.append(' - réussi')

                    else:
                      self.console.append(' - échoué')
                      message = "La lecture de la carte a echoué."
                      success = False
                      break
                  else:
                    message = "Impossible d'authentifier le bloc."
                    success = False
                    break
              else:
                message = "Impossible de récuperer la clef."
                success = False
            else:
              message = "Pas de carte présente."
              success = False
          else:
            message = "Impossible de trouver un lecteur."
            success = False
        else:
          message = "Impossible de créer le context."
          success = False
        
        if not success:
          datas = []
        
        return success, datas, message

    def readCard(self):

        self.updateView = False
        self.console.setText('')
        self.console.append('-'*100)
        self.datas.setText("")

        ready = True
        message = "Lecture de la carte echoué."

        payload_bytes = []
        for block in constant.BLOCKS:
            success, datas, message = self.readBlock(block)
            if success:
                payload_bytes.extend(datas)
            else:
                ready = False
                break

        if ready:
            payload = smartcard.util.toASCIIString(payload_bytes).rstrip(".!")
            payload_object = json.loads(payload)
            
            self.datas.setText(json.dumps(payload_object, indent=2))
            
            if "anim" in payload_object:
                index = self.animation.index(payload_object["anim"])
                self.animBox.setCurrentIndex(index)

            if "style" in payload_object:
               index = self.style.index(payload_object["style"])
               self.styleBox.setCurrentIndex(index)

            if "picto" in payload_object:
                if payload_object["picto"].strip() != "":
                    self.pictoEdit.setText(payload_object["picto"])

            if "once" in payload_object:
                if payload_object["once"]==1:
                    self.onceCheckBox.setChecked(True)
                else:
                    self.onceCheckBox.setChecked(False)

            if "shuffle" in payload_object:
                if payload_object["shuffle"]==1:
                    self.shuffleCheckBox.setChecked(True)
                else:
                    self.shuffleCheckBox.setChecked(False)

            if "loop" in payload_object:
                if payload_object["loop"]==1:
                    self.loopCheckBox.setChecked(True)
                else:
                    self.loopCheckBox.setChecked(False)

            if "limit" in payload_object:
                self.limitSlider.setValue(int(payload_object["limit"]))

            if "keep" in payload_object:
                self.keepSlider.setValue(int(payload_object["keep"]))

            if "say" in payload_object:
                self.sayEdit.setText(payload_object["say"])
               
            if "url" in payload_object:
                self.urlEdit.setText(payload_object["url"])

            QMessageBox.information(self, "Lecture de la carte", "Lecture de la carte réussi.")
            
            self.updateView = True

        else:
            QMessageBox.warning(self, "Lecture de la carte", message)

    def writeBlock(self, block, datas):
      
        success = True
        message = "Ecriture de la carte echoué."
    
        hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
        
        if hresult == SCARD_S_SUCCESS:
        
          hresult, readers = SCardListReaders(hcontext, [])
        
          if len(readers) > 0:
        
            reader = readers[0]
        
            hresult, hcard, dwActiveProtocol = SCardConnect(
                hcontext,
                reader,
                SCARD_SHARE_SHARED,
                SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
        
            if hresult == SCARD_S_SUCCESS:
    
              # load key
              hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0x82,0x00,0x00,0x06,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])
              if hresult == SCARD_S_SUCCESS:
    
                for sub in range(0, 3):
              
                  #auth block
                  hresult, response = SCardTransmit(hcard,dwActiveProtocol,[0xFF,0x86,0x00,0x00,0x05,0x01,0x00,int(block + sub),0x60,0x00])
                  if hresult == SCARD_S_SUCCESS:
    
                    block_datas = [0xFF, 0xD6, 0x00, int(block + sub), 0x10]
                    for bcl in range(0, 16):
                      block_datas.append(datas.pop(0))
    
                    self.console.append('Ecriture du bloc: ' + str(block + sub))
                    self.console.append(' - datas : ' + smartcard.util.toASCIIString(block_datas))

                    hresult, response = SCardTransmit(hcard, dwActiveProtocol, block_datas)
                    if hresult == SCARD_S_SUCCESS:
                      message = "Ecriture de la carte réussi."
                      self.console.append(' - réussi')
                    else:
                      self.console.append(' - echoué')
                      message = "Ecriture de la carte échoué."
                      success = False
                      break
    
                  else:
                    message = "Impossible d'authentifier le bloc."
                    success = False
                    break
    
              else:
                message = "Impossible de récuperer la clef."
                success = False
            else:
              message = "Pas de carte présente."
              success = False
          else:
            message = "Impossible de trouver un lecteur."
            success = False
        else:
          message = "Impossible de créer le context."
          success = False
    
        return success, message

    def writeCard(self):

        self.console.setText('')
        self.console.append('-'*100)

        ready = True
        message = "Ecriture de la carte echoué."

        payload_object = {
            "anim": self.animBox.currentText(),
            "style": self.styleBox.currentText(),
            "picto": self.pictoEdit.text(),
            "once": self.onceCheckBox.isChecked(),
            "shuffle": self.shuffleCheckBox.isChecked(),
            "loop": self.loopCheckBox.isChecked(),
            "keep": self.keepSlider.value(),
            "limit": self.limitSlider.value(),
            "say": self.sayEdit.text(),
            "url": self.urlEdit.text()
        }

        self.datas.setText(json.dumps(payload_object, indent=2))      
        payload = json.dumps(payload_object)
        json_payload_bytes = smartcard.util.toASCIIBytes(payload)

        total_blocks = len(constant.BLOCKS) * 48
        diff_blocks = total_blocks - len(json_payload_bytes)

        # complete paylod for all block
        for bcl in range(0, diff_blocks):
            json_payload_bytes.append(0)

        for block in constant.BLOCKS:
            datas = []
            for bcl in range(0, 48):
                datas.append(json_payload_bytes.pop(0))
        
            success, message = self.writeBlock(block, datas)
            if not success:
                ready = False
                break

        if ready:
            QMessageBox.information(self, "Ecriture de la carte", "Ecriture de la carte réussi.")
        else:
            QMessageBox.warning(self, "Ecriture de la carte", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    frame = MorpheeCardEncoder()
    frame.show()
    sys.exit(app.exec_())