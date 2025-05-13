# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets, QtOpenGL
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal
from OpenGL import GL
import math
import random

class SceneGLWidget(QtOpenGL.QGLWidget):
    rotationChanged = pyqtSignal(float, float, float)
    translationChanged = pyqtSignal(float, float)
    scaleChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super(SceneGLWidget, self).__init__(parent)
        self.setMinimumSize(400, 400)
        self.current_scene = 'none'
        self.rotation_x = 0  # Rotasi X
        self.rotation_y = 0  # Rotasi Y
        self.rotation_z = 0  # Rotasi Z
        self.scale = 1.0
        self.translation_x = 0
        self.translation_y = 0

        # Mouse interaction variables
        self.last_pos = QtCore.QPoint()
        self.rotation_speed = 1.0
        self.pan_speed = 0.01
        self.zoom_speed = 0.1
        self.is_rotating = False
        self.is_panning = False

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # Sekitar 60 FPS
    def set_scene(self, scene_name):
        """Set the current scene to draw"""
        self.current_scene = scene_name
        if scene_name in ['saturn', 'star', 'earth', 'moon']:
            if not self.timer.isActive():
                self.timer.start(16)
        else:
            self.timer.stop()
            self.rotation_x = 0
            self.rotation_y = 0
            self.rotation_z = 0
        self.update()

    def update_animation(self):
        if self.current_scene in ['saturn', 'star', 'earth', 'moon']:
            self.rotation_x = (self.rotation_x + 1) % 360
            self.rotation_y = (self.rotation_y + 1) % 360
            self.rotation_z = (self.rotation_z + 1) % 360
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
        
        # Apply transformations
        GL.glTranslatef(self.translation_x, self.translation_y, 0)
        GL.glRotatef(self.rotation_x, 1, 0, 0)
        GL.glRotatef(self.rotation_y, 0, 1, 0)
        GL.glRotatef(self.rotation_z, 0, 0, 1)
        GL.glScalef(self.scale, self.scale, 1)
        
        # Draw based on current scene
        if self.current_scene == 'lightning':
            self.draw_lightning()
        elif self.current_scene == 'cloud':
            self.draw_cloud()
        elif self.current_scene == 'star':
            self.draw_star()
        elif self.current_scene == 'saturn':
            self.draw_saturn()
        elif self.current_scene == 'rainbow':
            self.draw_rainbow()
        elif self.current_scene == 'rocket':
            self.draw_rocket()
        elif self.current_scene == 'earth':
            self.draw_earth()
        elif self.current_scene == 'moon':
            self.draw_moon()

    # Mouse interaction methods
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_rotating = True
            self.last_pos = event.pos()
        elif event.button() == Qt.RightButton:
            self.is_panning = True
            self.last_pos = event.pos()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_rotating = False
        elif event.button() == Qt.RightButton:
            self.is_panning = False
            
    def mouseMoveEvent(self, event):
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()
        
        if self.is_rotating:
            self.rotation_x = (self.rotation_x + dy * self.rotation_speed) % 360
            self.rotation_y = (self.rotation_y + dx * self.rotation_speed) % 360
            self.rotationChanged.emit(self.rotation_x, self.rotation_y, self.rotation_z)
            self.update()
            
        if self.is_panning:
            self.translation_x += dx * self.pan_speed
            self.translation_y -= dy * self.pan_speed  # Invert y-axis
            self.translationChanged.emit(self.translation_x, self.translation_y)
            self.update()
            
        self.last_pos = event.pos()
        
    def wheelEvent(self, event):
        zoom_factor = 1.1
        if event.angleDelta().y() > 0:
            self.scale *= zoom_factor
        else:
            self.scale /= zoom_factor
        self.scaleChanged.emit(self.scale)
        self.update()

    # Transformation methods
    def set_rotation_x(self, angle):
        self.rotation_x = angle
        self.rotationChanged.emit(self.rotation_x, self.rotation_y, self.rotation_z)
        self.update()

    def set_rotation_y(self, angle):
        self.rotation_y = angle
        self.rotationChanged.emit(self.rotation_x, self.rotation_y, self.rotation_z)
        self.update()

    def set_rotation_z(self, angle):
        self.rotation_z = angle
        self.rotationChanged.emit(self.rotation_x, self.rotation_y, self.rotation_z)
        self.update()

    def set_translation_x(self, x):
        self.translation_x = x
        self.translationChanged.emit(self.translation_x, self.translation_y)
        self.update()

    def set_translation_y(self, y):
        self.translation_y = y
        self.translationChanged.emit(self.translation_x, self.translation_y)
        self.update()

    def set_scale(self, scale):
        self.scale = scale
        self.scaleChanged.emit(self.scale)
        self.update()

    # Drawing methods (keep your existing draw methods here)
    # ... (draw_lightning, draw_cloud, etc.)

    def draw_lightning(self):
        GL.glLineWidth(6.0)
        GL.glColor3f(1.0, 1.0, 0.0)  # Yellow color

        GL.glBegin(GL.GL_LINE_STRIP)

        # Zigzag shape mimicking a ⚡ lightning bolt
        points = [
            (0.0, 0.6),
            (-0.3, 0.1),
            (0.0, 0.1),
            (-0.6, -0.9),
        ]

        for x, y in points:
            GL.glVertex2f(x, y)

        GL.glEnd()

    def draw_cloud(self):
        """Draw cloud using OpenGL circles"""
        GL.glColor3f(1.0, 1.0, 1.0)  # White color
        
        # Cloud parts with different positions and sizes
        cloud_parts = [
            (-0.6, 0, 0.5, 0.5),
            (-0.3, 0.1, 0.6, 0.6),
            (0.1, 0.4, 0.7, 0.7),
            (0.5, 0.2, 0.6, 0.6),
            (0.8, 0, 0.5, 0.5),
            (0.2, -0.1, 0.8, 0.7)
        ]

        for x, y, w, h in cloud_parts:
            self.draw_ellipse(x, y, w, h)

    def draw_ellipse(self, x, y, width, height):
        """Draw an ellipse using OpenGL triangle fan"""
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glVertex2f(x, y)  # Center point
        
        segments = 36
        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            GL.glVertex2f(
                x + width/2 * math.cos(theta), 
                y + height/2 * math.sin(theta)
            )
        
        GL.glEnd()

    def draw_rainbow(self):
        """Draw a 2D rainbow using concentric arcs with different colors"""
        colors = [
            (1.0, 0.0, 0.0),  # Red
            (1.0, 0.5, 0.0),  # Orange
            (1.0, 1.0, 0.0),  # Yellow
            (0.0, 1.0, 0.0),  # Green
            (0.0, 0.0, 1.0),  # Blue
            (0.5, 0.0, 1.0),  # Indigo
            (0.7, 0.0, 1.0)   # Violet
        ]
        
        start_radius = 0.5  # Ubah dari 0.3 menjadi 0.5
        thickness = 0.15    # Ubah dari 0.1 menjadi 0.15
        segments = 50
        start_angle = math.pi / 8  # Ubah dari pi/6 (30°) menjadi pi/8 (22.5°)
        end_angle = math.pi - start_angle
        
        for i, color in enumerate(colors):
            radius = start_radius + (i * thickness)
            GL.glColor3f(*color)
            
            GL.glBegin(GL.GL_QUAD_STRIP)
            for j in range(segments + 1):
                theta = start_angle + (end_angle - start_angle) * j / segments
                
                # Inner vertex
                x1 = radius * math.cos(theta)
                y1 = radius * math.sin(theta)
                GL.glVertex2f(x1, y1)
                
                # Outer vertex
                x2 = (radius + thickness) * math.cos(theta)
                y2 = (radius + thickness) * math.sin(theta)
                GL.glVertex2f(x2, y2)
                
            GL.glEnd()

    def draw_rocket(self):
        """Draw a 2D rocket using OpenGL primitives"""
        # Badan roket (trapesium)
        GL.glBegin(GL.GL_POLYGON)
        GL.glColor3f(0.8, 0.8, 0.8)  # Light gray
        GL.glVertex2f(-0.1, -0.5)   # Kiri bawah
        GL.glVertex2f(0.1, -0.5)    # Kanan bawah
        GL.glVertex2f(0.2, 0.3)     # Kanan atas
        GL.glVertex2f(-0.2, 0.3)    # Kiri atas
        GL.glEnd()

        # Kepala roket (segitiga)
        GL.glBegin(GL.GL_TRIANGLES)
        GL.glColor3f(1.0, 0.0, 0.0)  # Red
        GL.glVertex2f(-0.2, 0.3)    # Kiri
        GL.glVertex2f(0.2, 0.3)     # Kanan
        GL.glVertex2f(0.0, 0.7)     # Puncak
        GL.glEnd()

        # Sayap kiri
        GL.glBegin(GL.GL_TRIANGLES)
        GL.glColor3f(0.6, 0.6, 0.6)  # Dark gray
        GL.glVertex2f(-0.1, -0.3)   # Atas
        GL.glVertex2f(-0.1, -0.5)   # Bawah
        GL.glVertex2f(-0.3, -0.5)   # Ujung sayap
        GL.glEnd()

        # Sayap kanan
        GL.glBegin(GL.GL_TRIANGLES)
        GL.glColor3f(0.6, 0.6, 0.6)  # Dark gray
        GL.glVertex2f(0.1, -0.3)    # Atas
        GL.glVertex2f(0.1, -0.5)    # Bawah
        GL.glVertex2f(0.3, -0.5)    # Ujung sayap
        GL.glEnd()

        # Jendela roket (lingkaran)
        self.draw_circle(0.0, 0.0, 0.08, (0.2, 0.6, 1.0))  # Light blue window

        # Api roket
        GL.glBegin(GL.GL_TRIANGLES)
        # Api tengah (merah)
        GL.glColor3f(1.0, 0.0, 0.0)  # Red
        GL.glVertex2f(-0.1, -0.5)
        GL.glVertex2f(0.1, -0.5)
        GL.glVertex2f(0.0, -0.8)
        # Api kiri (kuning)
        GL.glColor3f(1.0, 1.0, 0.0)  # Yellow
        GL.glVertex2f(-0.15, -0.5)
        GL.glVertex2f(-0.05, -0.5)
        GL.glVertex2f(-0.1, -0.7)
        # Api kanan (kuning)
        GL.glVertex2f(0.05, -0.5)
        GL.glVertex2f(0.15, -0.5)
        GL.glVertex2f(0.1, -0.7)
        GL.glEnd()

    def draw_circle(self, x, y, radius, color):
        """Helper method to draw a filled circle"""
        GL.glColor3f(*color)
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glVertex2f(x, y)
        segments = 32
        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            dx = radius * math.cos(theta)
            dy = radius * math.sin(theta)
            GL.glVertex2f(x + dx, y + dy)
        GL.glEnd()

    def draw_star(self):
        """Draw a 3D 5-pointed star (star prism) using OpenGL with gradient effect"""
        outer_radius = 1.0
        inner_radius = 0.4
        depth = 0.2  # Thickness of the star

        front_face = []
        back_face = []

        for i in range(10):
            angle = 2 * math.pi * i / 10 - math.pi / 2
            radius = inner_radius if i % 2 else outer_radius
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            front_face.append((x, y, depth / 2))
            back_face.append((x, y, -depth / 2))

        # Front face with gradient
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glColor3f(1.0, 0.84, 0.0)  # center (gold)
        GL.glVertex3f(0, 0, depth / 2)
        for i, v in enumerate(front_face + [front_face[0]]):
            if i % 2 == 0:
                GL.glColor3f(1.0, 0.7, 0.0)  # outer points - deeper gold
            else:
                GL.glColor3f(1.0, 0.9, 0.4)  # inner points - lighter
            GL.glVertex3f(*v)
        GL.glEnd()

        # Back face with reversed gradient
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glColor3f(1.0, 0.84, 0.0)
        GL.glVertex3f(0, 0, -depth / 2)
        for i, v in enumerate(back_face + [back_face[0]]):
            if i % 2 == 0:
                GL.glColor3f(1.0, 0.7, 0.0)
            else:
                GL.glColor3f(1.0, 0.9, 0.4)
            GL.glVertex3f(*v)
        GL.glEnd()

        # Sides with gradient
        GL.glBegin(GL.GL_QUADS)
        for i in range(10):
            next_i = (i + 1) % 10
            v1 = front_face[i]
            v2 = front_face[next_i]
            v3 = back_face[next_i]
            v4 = back_face[i]

            GL.glColor3f(1.0, 0.7 + 0.03 * i, 0.0)
            GL.glVertex3f(*v1)
            GL.glColor3f(1.0, 0.7 + 0.03 * i, 0.2)
            GL.glVertex3f(*v2)
            GL.glColor3f(1.0, 0.7 + 0.03 * i, 0.2)
            GL.glVertex3f(*v3)
            GL.glColor3f(1.0, 0.7 + 0.03 * i, 0.0)
            GL.glVertex3f(*v4)
        GL.glEnd()

    def draw_saturn(self):
        # Gambar bola untuk Saturnus
        GL.glColor3f(0.8, 0.7, 0.5)
        self.draw_sphere(0.9, 30, 30)

        # Gambar cincin
        GL.glColor3f(0.6, 0.6, 0.6)
        self.draw_ring(1.1, 1.6, 100)

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

                # Gradient based on latitude
                GL.glColor3f(0.8 - 0.3 * i / stacks, 0.7 - 0.2 * i / stacks, 0.5)
                GL.glVertex3f(x * zr0, y * zr0, z0)

                GL.glColor3f(0.8 - 0.3 * (i+1) / stacks, 0.7 - 0.2 * (i+1) / stacks, 0.5)
                GL.glVertex3f(x * zr1, y * zr1, z1)
            GL.glEnd()

    def draw_ring(self, inner_radius, outer_radius, segments):
        thickness = 0.1 # Ketebalan cincin

        GL.glBegin(GL.GL_QUAD_STRIP)
        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            x = math.cos(theta)*1.2
            y = math.sin(theta)*0.7

            # Menggambar bagian bawah cincin (z = -thickness/2)
            GL.glVertex3f(x * inner_radius, y * inner_radius, -thickness / 2)
            GL.glVertex3f(x * outer_radius, y * outer_radius, -thickness / 2)

            # Menggambar bagian atas cincin (z = +thickness/2)
            GL.glVertex3f(x * inner_radius, y * inner_radius, thickness / 2)
            GL.glVertex3f(x * outer_radius, y * outer_radius, thickness / 2)

        GL.glEnd()
        
    # def draw_earth(self):
        
    #     GL.glEnd()
    # def draw_moon(self):
        
    #     GL.glEnd()
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
        
        # Title
        self.JUDUL = QtWidgets.QTextEdit()
        self.JUDUL.setMaximumHeight(30)
        self.JUDUL.setStyleSheet("background-color: rgb(0, 0, 0); color: white;")
        self.JUDUL.setObjectName("JUDUL")
        self.main_layout.addWidget(self.JUDUL)
        
        # Content layout
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setObjectName("content_layout")
        
        # Left panel
        self.left_panel = QtWidgets.QVBoxLayout()
        self.left_panel.setObjectName("left_panel")
        
        # 2D Objects
        self.groupBox_objek2d = QtWidgets.QGroupBox("Objek 2D")
        self.groupBox_objek2d.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.left_panel_2d = QtWidgets.QGridLayout(self.groupBox_objek2d)
        
        self.petir = QtWidgets.QPushButton("Petir")
        self.petir.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.left_panel_2d.addWidget(self.petir, 0, 0)
        
        self.awan = QtWidgets.QPushButton("Awan")
        self.awan.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.left_panel_2d.addWidget(self.awan, 0, 1)
        
        self.pelangi = QtWidgets.QPushButton("Pelangi")
        self.pelangi.setStyleSheet("background-color: rgb(200, 255, 200);")
        self.left_panel_2d.addWidget(self.pelangi, 1, 0)
        
        self.roket = QtWidgets.QPushButton("Roket")
        self.roket.setStyleSheet("background-color: rgb(255, 200, 200);")
        self.left_panel_2d.addWidget(self.roket, 1, 1)
        
        self.left_panel.addWidget(self.groupBox_objek2d)
        
        # 3D Objects
        self.groupBox_objek3d = QtWidgets.QGroupBox("Objek 3D")
        self.groupBox_objek3d.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.left_panel_3d = QtWidgets.QGridLayout(self.groupBox_objek3d)
        
        self.star = QtWidgets.QPushButton("Bintang")
        self.star.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.left_panel_3d.addWidget(self.star, 0, 0)
        
        self.saturn = QtWidgets.QPushButton("Saturnus")
        self.saturn.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.left_panel_3d.addWidget(self.saturn, 0, 1)
        
        self.earth = QtWidgets.QPushButton("Bumi")
        self.earth.setStyleSheet("background-color: rgb(200, 200, 255);")
        self.left_panel_3d.addWidget(self.earth, 1, 0)
        
        self.moon = QtWidgets.QPushButton("Bulan")
        self.moon.setStyleSheet("background-color: rgb(255, 200, 200);")
        self.left_panel_3d.addWidget(self.moon, 1, 1)
        
        self.left_panel.addWidget(self.groupBox_objek3d)
        
        # Translation Control
        self.groupBox_translasi = QtWidgets.QGroupBox("Translasi")
        self.groupBox_translasi.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.left_panel_translasi = QtWidgets.QGridLayout(self.groupBox_translasi)
        
        self.kiri = QtWidgets.QPushButton("Kiri")
        self.kanan = QtWidgets.QPushButton("Kanan")
        self.atas = QtWidgets.QPushButton("Atas")
        self.bawah = QtWidgets.QPushButton("Bawah")
        
        self.left_panel_translasi.addWidget(self.atas, 0, 1)
        self.left_panel_translasi.addWidget(self.kiri, 1, 0)
        self.left_panel_translasi.addWidget(self.kanan, 1, 2)
        self.left_panel_translasi.addWidget(self.bawah, 2, 1)
        
        self.left_panel.addWidget(self.groupBox_translasi)
        
        # Scaling Control
        self.skala_groupbox = QtWidgets.QGroupBox("Skala")
        self.skala_groupbox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.skala_layout = QtWidgets.QHBoxLayout(self.skala_groupbox)

        self.skala = QtWidgets.QDoubleSpinBox()
        self.skala.setRange(0.1, 2.0)
        self.skala.setSingleStep(0.1)
        self.skala.setValue(1.0)
        self.view_skala = QtWidgets.QPushButton("View")

        self.skala_layout.addWidget(self.skala)
        self.skala_layout.addWidget(self.view_skala)

        self.left_panel.addWidget(self.skala_groupbox)

        # Rotation Control
        self.rotasi_x_groupbox = QtWidgets.QGroupBox("Rotasi X")
        self.rotasi_x_groupbox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.rotasi_x_layout = QtWidgets.QHBoxLayout(self.rotasi_x_groupbox)
        
        self.rotasi_x = QtWidgets.QDoubleSpinBox()
        self.rotasi_x.setRange(0, 360)
        self.rotasi_x.setSingleStep(1)
        self.rotasi_x.setValue(0)
        self.view_rotasi_x = QtWidgets.QPushButton("Apply")
        
        self.rotasi_x_layout.addWidget(self.rotasi_x)
        self.rotasi_x_layout.addWidget(self.view_rotasi_x)
        self.left_panel.addWidget(self.rotasi_x_groupbox)
        
        self.rotasi_y_groupbox = QtWidgets.QGroupBox("Rotasi Y")
        self.rotasi_y_groupbox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.rotasi_y_layout = QtWidgets.QHBoxLayout(self.rotasi_y_groupbox)
        
        self.rotasi_y = QtWidgets.QDoubleSpinBox()
        self.rotasi_y.setRange(0, 360)
        self.rotasi_y.setSingleStep(1)
        self.rotasi_y.setValue(0)
        self.view_rotasi_y = QtWidgets.QPushButton("Apply")
        
        self.rotasi_y_layout.addWidget(self.rotasi_y)
        self.rotasi_y_layout.addWidget(self.view_rotasi_y)
        self.left_panel.addWidget(self.rotasi_y_groupbox)
        
        self.rotasi_z_groupbox = QtWidgets.QGroupBox("Rotasi Z")
        self.rotasi_z_groupbox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.rotasi_z_layout = QtWidgets.QHBoxLayout(self.rotasi_z_groupbox)
        
        self.rotasi_z = QtWidgets.QDoubleSpinBox()
        self.rotasi_z.setRange(0, 360)
        self.rotasi_z.setSingleStep(1)
        self.rotasi_z.setValue(0)
        self.view_rotasi_z = QtWidgets.QPushButton("Apply")
        
        self.rotasi_z_layout.addWidget(self.rotasi_z)
        self.rotasi_z_layout.addWidget(self.view_rotasi_z)
        self.left_panel.addWidget(self.rotasi_z_groupbox)
        
        # Add stretch and complete layout
        self.left_panel.addStretch()
        self.content_layout.addLayout(self.left_panel)
        
        # OpenGL Widget
        self.glWidget = SceneGLWidget()
        self.content_layout.addWidget(self.glWidget)
        self.content_layout.setStretch(1, 3)
        self.main_layout.addLayout(self.content_layout)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.setup_connections()
        self.retranslateUi(MainWindow)

    def setup_connections(self):
        # Scene selection
        self.petir.clicked.connect(lambda: self.glWidget.set_scene('lightning'))
        self.awan.clicked.connect(lambda: self.glWidget.set_scene('cloud'))
        self.pelangi.clicked.connect(lambda: self.glWidget.set_scene('rainbow'))
        self.roket.clicked.connect(lambda: self.glWidget.set_scene('rocket'))
        self.star.clicked.connect(lambda: self.glWidget.set_scene('star'))
        self.saturn.clicked.connect(lambda: self.glWidget.set_scene('saturn'))
        self.earth.clicked.connect(lambda: self.glWidget.set_scene('earth'))
        self.moon.clicked.connect(lambda: self.glWidget.set_scene('moon'))
        
        # Translation controls
        self.kiri.clicked.connect(lambda: self.glWidget.set_translation_x(self.glWidget.translation_x - 0.1))
        self.kanan.clicked.connect(lambda: self.glWidget.set_translation_x(self.glWidget.translation_x + 0.1))
        self.atas.clicked.connect(lambda: self.glWidget.set_translation_y(self.glWidget.translation_y + 0.1))
        self.bawah.clicked.connect(lambda: self.glWidget.set_translation_y(self.glWidget.translation_y - 0.1))
        
        # Rotation controls
        self.view_rotasi_x.clicked.connect(lambda: self.glWidget.set_rotation_x(self.rotasi_x.value()))
        self.view_rotasi_y.clicked.connect(lambda: self.glWidget.set_rotation_y(self.rotasi_y.value()))
        self.view_rotasi_z.clicked.connect(lambda: self.glWidget.set_rotation_z(self.rotasi_z.value()))
        
        # Scale control
        self.view_skala.clicked.connect(lambda: self.glWidget.set_scale(self.skala.value()))
        
        # Connect signals from GLWidget to update UI
        self.glWidget.rotationChanged.connect(self.update_rotation_ui)
        self.glWidget.translationChanged.connect(self.update_translation_ui)
        self.glWidget.scaleChanged.connect(self.update_scale_ui)

    def update_rotation_ui(self, x, y, z):
        self.rotasi_x.setValue(x)
        self.rotasi_y.setValue(y)
        self.rotasi_z.setValue(z)

    def update_translation_ui(self, x, y):
        pass  # Can add translation display if needed

    def update_scale_ui(self, scale):
        self.skala.setValue(scale)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        
        # Title
        self.JUDUL.setHtml(_translate("MainWindow", 
            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:7.875pt; font-weight:400; font-style:normal;\">\n"
            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600; color:#ffffff;\">ATAP LANGIT</span></p></body></html>"))
        
        # UI translations (keep your existing translations)
        # ...

def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()