# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets, QtOpenGL
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsPathItem
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QOpenGLShaderProgram, QOpenGLShader, QVector3D, QMatrix4x4
from OpenGL import GL
import math

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1175, 746)
        MainWindow.setStyleSheet("background-color: rgb(0, 0, 0);")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setObjectName("main_layout")
        
        # JUDUL - tetap di atas
        self.JUDUL = QtWidgets.QTextEdit()
        self.JUDUL.setMaximumHeight(30)
        self.JUDUL.setStyleSheet("background-color: rgb(0, 0, 0); gridline-color: rgb(0, 170, 255);")
        self.JUDUL.setObjectName("JUDUL")
        self.main_layout.addWidget(self.JUDUL)
        
        # Horizontal layout untuk konten utama
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setObjectName("content_layout")
        
        # Vertical layout untuk panel kiri (controls)
        self.left_panel = QtWidgets.QVBoxLayout()
        self.left_panel.setObjectName("left_panel")
        
        # Group boxes untuk panel kiri
        self.groupBox_objek2d = QtWidgets.QGroupBox()
        self.groupBox_objek2d.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.groupBox_objek2d.setObjectName("groupBox_objek2d")
        
        # Layout untuk groupBox_objek2d
        self.gridLayout_2d = QtWidgets.QGridLayout(self.groupBox_objek2d)
        self.petir = QtWidgets.QPushButton()
        self.petir.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.petir.setObjectName("petir")
        self.gridLayout_2d.addWidget(self.petir, 0, 0, 1, 1)
        
        self.roket = QtWidgets.QPushButton()
        self.roket.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.roket.setObjectName("roket")
        self.gridLayout_2d.addWidget(self.roket, 1, 1, 1, 1)
        
        self.awan = QtWidgets.QPushButton()
        self.awan.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.awan.setObjectName("awan")
        self.gridLayout_2d.addWidget(self.awan, 0, 1, 1, 1)
        
        self.pelangi = QtWidgets.QPushButton()
        self.pelangi.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.pelangi.setObjectName("pelangi")
        self.gridLayout_2d.addWidget(self.pelangi, 1, 0, 1, 1)
        
        self.left_panel.addWidget(self.groupBox_objek2d)
        
        # GroupBox_objek3d
        self.groupBox_objek3d = QtWidgets.QGroupBox()
        self.groupBox_objek3d.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.groupBox_objek3d.setObjectName("groupBox_objek3d")
        
        self.gridLayout_3d = QtWidgets.QGridLayout(self.groupBox_objek3d)
        self.moon = QtWidgets.QPushButton()
        self.moon.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.moon.setObjectName("moon")
        self.gridLayout_3d.addWidget(self.moon, 0, 1, 1, 1)
        
        self.saturn = QtWidgets.QPushButton()
        self.saturn.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.saturn.setObjectName("saturn")
        self.gridLayout_3d.addWidget(self.saturn, 1, 0, 1, 1)
        
        self.earth = QtWidgets.QPushButton()
        self.earth.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.earth.setObjectName("earth")
        self.gridLayout_3d.addWidget(self.earth, 0, 0, 1, 1)
        
        self.star = QtWidgets.QPushButton()
        self.star.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.star.setObjectName("star")
        self.gridLayout_3d.addWidget(self.star, 1, 1, 1, 1)
        
        self.left_panel.addWidget(self.groupBox_objek3d)
        
        # GroupBox_translasi
        self.groupBox_translasi = QtWidgets.QGroupBox()
        self.groupBox_translasi.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.groupBox_translasi.setObjectName("groupBox_translasi")
        
        self.gridLayout_translasi = QtWidgets.QGridLayout(self.groupBox_translasi)
        self.kanan = QtWidgets.QPushButton()
        self.kanan.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.kanan.setObjectName("kanan")
        self.gridLayout_translasi.addWidget(self.kanan, 0, 1, 1, 1)
        
        self.bawah = QtWidgets.QPushButton()
        self.bawah.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.bawah.setObjectName("bawah")
        self.gridLayout_translasi.addWidget(self.bawah, 1, 0, 1, 1)
        
        self.atas = QtWidgets.QPushButton()
        self.atas.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.atas.setObjectName("atas")
        self.gridLayout_translasi.addWidget(self.atas, 0, 0, 1, 1)
        
        self.kiri = QtWidgets.QPushButton()
        self.kiri.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.kiri.setObjectName("kiri")
        self.gridLayout_translasi.addWidget(self.kiri, 1, 1, 1, 1)
        
        self.left_panel.addWidget(self.groupBox_translasi)
        
        # Skala groupbox
        self.skala_groupbox_2 = QtWidgets.QGroupBox()
        self.skala_groupbox_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.skala_groupbox_2.setObjectName("skala_groupbox_2")
        
        self.horizontalLayout_skala = QtWidgets.QHBoxLayout(self.skala_groupbox_2)
        self.skala = QtWidgets.QSpinBox()
        self.skala.setObjectName("skala")
        self.horizontalLayout_skala.addWidget(self.skala)
        
        self.view_skala = QtWidgets.QPushButton()
        self.view_skala.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.view_skala.setObjectName("view_skala")
        self.horizontalLayout_skala.addWidget(self.view_skala)
        
        self.left_panel.addWidget(self.skala_groupbox_2)
        
        # Tambahkan spacer untuk mendorong semua ke atas
        self.left_panel.addStretch()
        
        # Tambahkan left panel ke content layout
        self.content_layout.addLayout(self.left_panel)
        
        # Vertical layout untuk panel kanan (graphics view dan controls bawah)
        self.right_panel = QtWidgets.QVBoxLayout()
        self.right_panel.setObjectName("right_panel")
        
        # GraphicsView - akan mengembang
        self.graphicsView = QtWidgets.QGraphicsView()
        self.graphicsView.setStyleSheet("background-color:rgb(224, 251, 255);")
        self.graphicsView.setObjectName("graphicsView")
        
        # Buat scene untuk graphicsView
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        
        self.right_panel.addWidget(self.graphicsView)
        
        # Horizontal layout untuk controls bawah
        self.bottom_controls = QtWidgets.QHBoxLayout()
        self.bottom_controls.setObjectName("bottom_controls")
        
        # Spacer di kiri
        self.bottom_controls.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        
        # GroupBox_color
        self.groupBox_color = QtWidgets.QGroupBox()
        self.groupBox_color.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.groupBox_color.setObjectName("groupBox_color")
        
        self.horizontalLayout_color = QtWidgets.QHBoxLayout(self.groupBox_color)
        self.fill_color = QtWidgets.QPushButton()
        self.fill_color.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.fill_color.setObjectName("fill_color")
        self.horizontalLayout_color.addWidget(self.fill_color)
        
        self.pushButton_10 = QtWidgets.QPushButton()
        self.pushButton_10.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.pushButton_10.setObjectName("pushButton_10")
        self.horizontalLayout_color.addWidget(self.pushButton_10)
        
        self.bottom_controls.addWidget(self.groupBox_color)
        
        # Spacer di tengah
        self.bottom_controls.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        
        # Rotasi groupbox
        self.rotasi_groupbox = QtWidgets.QGroupBox()
        self.rotasi_groupbox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.rotasi_groupbox.setObjectName("rotasi_groupbox")
        
        self.horizontalLayout_rotasi = QtWidgets.QHBoxLayout(self.rotasi_groupbox)
        self.rotasi = QtWidgets.QSpinBox()
        self.rotasi.setObjectName("rotasi")
        self.horizontalLayout_rotasi.addWidget(self.rotasi)
        
        self.view_rotasi = QtWidgets.QPushButton()
        self.view_rotasi.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.view_rotasi.setObjectName("view_rotasi")
        self.horizontalLayout_rotasi.addWidget(self.view_rotasi)
        
        self.bottom_controls.addWidget(self.rotasi_groupbox)
        
        # Spacer di kanan
        self.bottom_controls.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        
        # Tambahkan bottom controls ke right panel
        self.right_panel.addLayout(self.bottom_controls)
        
        # Tambahkan right panel ke content layout
        self.content_layout.addLayout(self.right_panel)
        
        # Set stretch factor untuk membuat graphicsView lebih besar
        self.content_layout.setStretch(1, 3)  # Right panel (terutama graphicsView) dapat 3x lebih banyak ruang
        
        # Tambahkan content layout ke main layout
        self.main_layout.addLayout(self.content_layout)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1175, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        
        # Hubungkan tombol-tombol dengan fungsi terkait
        self.petir.clicked.connect(self.draw_lightning)
        self.awan.clicked.connect(self.draw_cloud)
        self.saturn.clicked.connect(self.draw_saturn)
        self.star.clicked.connect(self.draw_star)
        
        # Connect resize event
        MainWindow.resizeEvent = self.on_resize
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.JUDUL.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:7.875pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600; color:#ffffff;\">LANGIT </span></p></body></html>"))
        self.groupBox_objek2d.setTitle(_translate("MainWindow", "objek 2d"))
        self.petir.setText(_translate("MainWindow", "petir"))
        self.roket.setText(_translate("MainWindow", "roket"))
        self.awan.setText(_translate("MainWindow", "awan"))
        self.pelangi.setText(_translate("MainWindow", "pelangi"))
        self.groupBox_objek3d.setTitle(_translate("MainWindow", "objek 3d"))
        self.moon.setText(_translate("MainWindow", "bulan sabit"))
        self.saturn.setText(_translate("MainWindow", "saturnus"))
        self.earth.setText(_translate("MainWindow", "bumi"))
        self.star.setText(_translate("MainWindow", "bintang"))
        self.groupBox_color.setTitle(_translate("MainWindow", "color"))
        self.fill_color.setText(_translate("MainWindow", "FILL"))
        self.pushButton_10.setText(_translate("MainWindow", "LINE"))
        self.rotasi_groupbox.setTitle(_translate("MainWindow", "rotasi"))
        self.view_rotasi.setText(_translate("MainWindow", "view"))
        self.groupBox_translasi.setTitle(_translate("MainWindow", "translasi"))
        self.kanan.setText(_translate("MainWindow", "kanan"))
        self.bawah.setText(_translate("MainWindow", "bawah"))
        self.atas.setText(_translate("MainWindow", "atas"))
        self.kiri.setText(_translate("MainWindow", "kiri"))
        self.skala_groupbox_2.setTitle(_translate("MainWindow", "skala"))
        self.view_skala.setText(_translate("MainWindow", "view"))

    def on_resize(self, event):
        """Handle window resize event"""
        # Adjust button sizes based on window size
        window_size = event.size()
        base_size = min(window_size.width(), window_size.height())
        
        # Set button sizes
        btn_size = int(base_size * 0.08)
        for btn in [self.petir, self.roket, self.awan, self.pelangi, 
                   self.moon, self.saturn, self.earth, self.star,
                   self.kanan, self.bawah, self.atas, self.kiri,
                   self.view_skala, self.fill_color, self.pushButton_10, self.view_rotasi]:
            btn.setMinimumSize(btn_size, btn_size)
            btn.setMaximumSize(btn_size, btn_size)
        
        # Set font sizes
        font_size = max(8, int(base_size * 0.005))
        font = QtGui.QFont()
        font.setPointSize(font_size)
        
        for widget in [self.groupBox_objek2d, self.groupBox_objek3d, self.groupBox_translasi,
                      self.skala_groupbox_2, self.groupBox_color, self.rotasi_groupbox]:
            widget.setFont(font)
            for child in widget.findChildren(QtWidgets.QWidget):
                child.setFont(font)
        
        # Redraw current object if any
        if hasattr(self, 'current_draw_method'):
            self.current_draw_method()
        
        event.accept()

    def draw_lightning(self):
        """Fungsi untuk menggambar petir di graphicsView"""
        self.scene.clear()
        self.current_draw_method = self.draw_lightning
        
        view_size = self.graphicsView.size()
        view_width = view_size.width()
        view_height = view_size.height()
        
        # Calculate base size based on view dimensions
        base_size = min(view_width, view_height) * 0.5
        
        path = QtGui.QPainterPath()
        start_x = view_width / 2
        start_y = view_height * 0.1
        path.moveTo(start_x, start_y)
        
        # Calculate points based on view size
        points = [
            QPointF(start_x - base_size*0.3, start_y + base_size*0.3),
            QPointF(start_x + base_size*0.2, start_y + base_size*0.4),
            QPointF(start_x - base_size*0.1, start_y + base_size*0.6),
            QPointF(start_x + base_size*0.2, start_y + base_size*0.8),
            QPointF(start_x - base_size*0.05, start_y + base_size),
            QPointF(start_x, start_y + base_size*1.2)
        ]
        
        for point in points:
            path.lineTo(point)
        
        path.lineTo(start_x + base_size*0.1, start_y + base_size*1.2)
        
        pen = QtGui.QPen(Qt.yellow)
        pen.setWidth(int(base_size * 0.05))
        self.scene.addPath(path, pen)

    def draw_cloud(self):
        self.scene.clear()
        self.current_draw_method = self.draw_cloud

        view_size = self.graphicsView.size()
        view_width = view_size.width()
        view_height = view_size.height()
        
        base_size = min(view_width, view_height) * 0.3

        center_x = view_width / 2
        center_y = view_height / 3

        brush = QtGui.QBrush(Qt.white)
        pen = QtGui.QPen(QtCore.Qt.NoPen)  # Tanpa outline

        # Daftar lingkaran untuk awan - ukuran relatif terhadap base_size
        cloud_parts = [
            (center_x - base_size*0.6, center_y, base_size*0.5, base_size*0.5),
            (center_x - base_size*0.3, center_y - base_size*0.1, base_size*0.6, base_size*0.6),
            (center_x + base_size*0.1, center_y - base_size*0.4, base_size*0.7, base_size*0.7),
            (center_x + base_size*0.5, center_y - base_size*0.2, base_size*0.6, base_size*0.6),
            (center_x + base_size*0.8, center_y, base_size*0.5, base_size*0.5),
            (center_x + base_size*0.2, center_y + base_size*0.1, base_size*0.8, base_size*0.7),  
        ]

        for x, y, w, h in cloud_parts:
            ellipse = QtWidgets.QGraphicsEllipseItem(x, y, w, h)
            ellipse.setBrush(brush)
            ellipse.setPen(pen)
            self.scene.addItem(ellipse)

    def draw_saturn(self):
        self.opengl_window = QtWidgets.QMainWindow()
        self.opengl_window.setWindowTitle("3D Saturnus")
        self.opengl_window.setGeometry(100, 100, 500, 500)
        self.gl_widget = SaturnGLWidget()
        self.opengl_window.setCentralWidget(self.gl_widget)
        self.opengl_window.show()


    def draw_star(self):
        """Fungsi untuk menggambar bintang 3D"""
        self.scene.clear()
        self.current_draw_method = self.draw_star
        
        view_size = self.graphicsView.size()
        view_width = view_size.width()
        view_height = view_size.height()
        
        base_size = min(view_width, view_height) * 0.3

        center_x = view_width / 2
        center_y = view_height / 2
        
        # Buat path untuk bintang 5 sudut
        path = QtGui.QPainterPath()
        
        outer_radius = base_size
        inner_radius = base_size * 0.4
        points = 5
        
        # Hitung titik-titik bintang
        for i in range(points * 2):
            angle = 2 * math.pi * i / (points * 2) - math.pi/2
            radius = inner_radius if i % 2 else outer_radius
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        
        path.closeSubpath()
        
        # Gradient untuk efek 3D
        gradient = QtGui.QRadialGradient(center_x, center_y, outer_radius)
        gradient.setColorAt(0, Qt.yellow)
        gradient.setColorAt(1, QtGui.QColor(255, 215, 0))  # Gold
        
        star_item = QGraphicsPathItem(path)
        star_item.setBrush(QtGui.QBrush(gradient))
        
        # Outline dengan warna lebih gelap
        pen = QtGui.QPen(QtGui.QColor(218, 165, 32))  # Golden rod
        pen.setWidth(int(base_size * 0.03))
        star_item.setPen(pen)
        
        self.scene.addItem(star_item)
        
        # Tambahkan efek glow/kilau
        for i in range(3):
            glow_radius = outer_radius - base_size * 0.1 * i
            glow = QGraphicsEllipseItem(center_x - glow_radius, center_y - glow_radius, 
                                      glow_radius*2, glow_radius*2)
            glow.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255, 30 - i*10)))
            glow.setPen(QtGui.QPen(Qt.transparent))
            self.scene.addItem(glow)

class SaturnGLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super(SaturnGLWidget, self).__init__(parent)
        self.setMinimumSize(400, 400)
        self.angle = 0

        # Timer untuk animasi rotasi
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_rotation)
        self.timer.start(16)  # sekitar 60fps

    def update_rotation(self):
        self.angle += 1
        self.update()

    def initializeGL(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)

    def resizeGL(self, w, h):
        GL.glViewport(0, 0, w, h)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        aspect = w / h if h != 0 else 1
        GL.glOrtho(-2 * aspect, 2 * aspect, -2, 2, -10, 10)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glRotatef(self.angle, 0, 1, 0)

        # Gambar bola untuk Saturnus
        GL.glColor3f(0.8, 0.7, 0.5)
        self.draw_sphere(1, 30, 30)

        # Gambar cincin
        GL.glColor3f(0.6, 0.6, 0.6)
        self.draw_ring(1.2, 1.8, 100)

    def draw_sphere(self, radius, slices, stacks):
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
            z0 = radius * math.sin(lat0)
            zr0 = radius * math.cos(lat0)
            z1 = radius * math.sin(lat1)
            zr1 = radius * math.cos(lat1)

            GL.glBegin(GL.GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j) / slices
                x = math.cos(lng)
                y = math.sin(lng)

                GL.glVertex3f(x * zr0, y * zr0, z0)
                GL.glVertex3f(x * zr1, y * zr1, z1)
            GL.glEnd()

    def draw_ring(self, inner_radius, outer_radius, segments):
        GL.glBegin(GL.GL_TRIANGLE_STRIP)
        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            x = math.cos(theta)
            y = math.sin(theta)
            GL.glVertex3f(x * inner_radius, y * inner_radius, 0)
            GL.glVertex3f(x * outer_radius, y * outer_radius, 0)
        GL.glEnd()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())