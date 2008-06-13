#!/usr/bin/env python
#coding: utf-8

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_editor import Ui_MainWindow
from newleveldialog import NewLevelDialog

import xmlwriter as xw

import options

class MainWindow(QMainWindow, Ui_MainWindow):
  def __init__(self, dbm, parent=None):
    QMainWindow.__init__(self, parent)
    Ui_MainWindow.setupUi(self, self)
    Ui_MainWindow.retranslateUi(self, self)

    self.propEd.autoApplyChanges = True
    self.setupConnections()
    self.setupActions()

    self.dbm = dbm

  def setupConnections(self):
    self.connect(self.levelView, SIGNAL('itemSelected(QGraphicsItem)'),
                 self.propEd.setFromItem)
    self.connect(self.levelView, SIGNAL('itemDeselected'),
                 self.propEd.setFromItem)

  def setupActions(self):
    self.connect(self.actionNew_level,
                 SIGNAL('triggered()'),
                 self.newLevel)
    self.connect(self.actionLoad,
                 SIGNAL('triggered()'),
                 self.load)
    self.connect(self.actionLoad_all,
                 SIGNAL('triggered()'),
                 self.loadAll)
    self.connect(self.actionSave_image,
                 SIGNAL('triggered()'),
                 self.saveImage)
    self.connect(self.actionAbout_Qt,
                 SIGNAL('triggered()'),
                 qApp.aboutQt)
    self.connect(self.actionSave_XML,
                 SIGNAL('triggered()'),
                 self.saveXML)

  def notImplementedYet(self):
    info = 'The feature you requested is not implemented yet.'
    QMessageBox.information(self,
                            self.trUtf8('Feature not implemented'),
                            self.trUtf8(info))

  def newLevel(self):
    size = NewLevelDialog.getLevelSize(self)
    if not size.isEmpty():
      self.levelView.newScene(size)

  def load(self, filenames = []):
    if not filenames:
      filenames = QFileDialog.getOpenFileNames(self,
                    self.trUtf8('Load'),
                    './',
                    'Editable files(*.png *.tiff *.jpg *.bmp *.xml)')

    unreadable = []
    for filename in filenames:
      if not filename.isEmpty() \
      and not self.loadImage(filename) \
      and not self.loadXML(filename):
        unreadable.append(filename)
        
    if unreadable:
      flist = ''
      for s in unreadable:
        flist += '\n' + s
      warn = str('Following files could not be loaded: %s' % flist)
      #print warn
      QMessageBox.warning(self,
                          self.trUtf8('Load'),
                          self.trUtf8(warn))

  def loadAll(self):
    files = [QString(os.path.join(options.terrain_path, f))
             for f in os.listdir(options.terrain_path)]
    files.extend([QString(os.path.join(options.db_path, f))
                  for f in os.listdir(options.db_path)])
    self.load(files)

  def loadImage(self, filename):
    newImage = QPixmap()
    if not newImage.load(filename):
      return False
    else:
      info = {}
      info['filename'] = os.path.basename(str(filename))
      info['name'] = info['filename'].rsplit('.', 1)[0]
      info['type'] = 'BackgroundItem'
      self.tileList.addItem(newImage, info)
      return True

  def loadXML(self, filename):
    try:
      # get the info list
      filename = str(filename)
      name = os.path.basename(filename).rsplit('.', 1)[0]
      imported = self.dbm.import_file(filename)
      info = imported['props']

      # craft that list
      del info['editor_enabled']
      info['name'] = name
      info['type'] = 'EventItem'
      k = imported['gfx'].keys()[0]
        # this is the image-resource name from XML
      info['filename'] = imported['gfx'][k]['file']
      
      # get the pixmap
      pixmap = QPixmap()
      if not pixmap.load(os.path.join(options.gfx_path, info['filename'])):
        return False

      self.tileList.addItem(pixmap, info)

      return True
#    except AttributeError, e:
#      print 'AttributeError:', e.message
#      return False
#    except KeyError, e:
#      print 'KeyError:', e.message
#      return False
    except Exception, e:
#      print 'Exception:', e.message
      return False

  def saveImage(self, filename = ''):
    if not filename:
      filename = QFileDialog.getSaveFileName(self,
                                  self.trUtf8('Save level as image'),
                                  './',
                                  'Image files(*.png *.tiff *.jpg *.bmp)')

    if not filename:
      return
    image = self.levelView.snapshot()
    if filename.indexOf('.') == -1:
      filename.append('.png')
    if not image.save(filename):
      QMessageBox.warning(self, self.trUtf8('Save level as image'),
                          self.trUtf8('The file could not be saved.'))

  def saveXML(self, filename = ''):
    if not filename:
      filename = QFileDialog.getSaveFileName(self,
                              self.trUtf8('Save level as XML'),
                              './',
                              'Extensible Markup Language files(*.xml)')
    
    if not filename:
      return
    if not filename.endsWith('.xml'):
      filename.append('.xml')
    if not xw.XMLWriter.writeEventsFile(filename, self.levelView.scene):
      warn = 'Could not write file:\n%s' %filename
      QMessageBox.warning(self,
                          self.trUtf8('Save as XML'),
                          self.trUtf8(warn))
