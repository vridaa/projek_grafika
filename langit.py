# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets, QtOpenGL
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal
from OpenGL import GL,GLU
import math
import random
from PIL import Image
import os

class SceneGLWidget(QtOpenGL.QGLWidget):
    rotationChanged = pyqtSignal(float, float, float)
    translationChanged = pyqtSignal(float, float)
    scaleChanged = pyqtSignal(float)
    colorChanged = pyqtSignal(float, float, float)

    def __init__(self, parent=None):
        super(SceneGLWidget, self).__init__(parent)
        self.setMinimumSize(400, 400)
        self.setFocusPolicy(Qt.StrongFocus)  # Enable keyboard focus
        self.current_scene = 'none'
        self.rotation_x = 0  # Rotasi X
        self.rotation_y = 0  # Rotasi Y
        self.rotation_z = 0  # Rotasi Z
        self.scale = 1.0
        self.translation_x = 0
        self.translation_y = 0
        
        self.object_color = {
            'lightning': (1.0, 1.0, 0.0),  # Yellow
            'cloud': (1.0, 1.0, 1.0),     # White
            'rainbow': None,               # Rainbow has multiple colors
            'rocket': (0.8, 0.8, 0.8),               # Rocket has multiple parts with different colors
        }
        self.current_color = (1.0, 1.0, 1.0)

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

        self.earth_texture = None
        self.moon_texture = None
        self.saturn_texture = None
        self.saturn_ring_texture = None  # Tambahkan variabel untuk tekstur cincin

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
        
    def set_object_color(self, r, g, b):
        """Set color for the current 2D object"""
        if self.current_scene in ['lightning', 'cloud', 'rocket']:  # Only for objects that support color change
            self.object_color[self.current_scene] = (r, g, b)
            self.current_color = (r, g, b)
            self.colorChanged.emit(r, g, b)
            self.update()

    def update_animation(self):
        if self.current_scene in ['saturn', 'star', 'earth', 'moon']:
            self.rotation_x = (self.rotation_x + 1) % 360
            self.rotation_y = (self.rotation_y + 1) % 360
            self.rotation_z = (self.rotation_z + 1) % 360
            self.update()

    def initializeGL(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)
        
        # Setup lighting
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        
        # Set light position and properties
        GL.glLight(GL.GL_LIGHT0, GL.GL_POSITION, (5.0, 5.0, 5.0, 1.0))
        GL.glLight(GL.GL_LIGHT0, GL.GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        GL.glLight(GL.GL_LIGHT0, GL.GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        
        # Load earth texture
        self.earth_texture = self.load_texture("textures/earth.png")
        self.moon_texture = self.load_texture("textures/moon.png")
        self.saturn_texture = self.load_texture("textures/saturn.png")
        self.saturn_ring_texture = self.load_texture("textures/saturn.png")  # Load tekstur cincin

    def load_texture(self, image_path):
        """Load texture from image file"""
        try:
            # Buka gambar menggunakan PIL
            image = Image.open(image_path)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = image.convert("RGBA").tobytes()
            
            # Generate texture ID
            texture_id = GL.glGenTextures(1)
            
            # Bind dan set parameter tekstur
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
            
            # Upload tekstur
            GL.glTexImage2D(
                GL.GL_TEXTURE_2D, 0, GL.GL_RGBA,
                image.width, image.height,
                0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, img_data
            )
            
            return texture_id
        except Exception as e:
            print(f"Error loading texture: {e}")
            return None

    def resizeGL(self, w, h):
        GL.glViewport(0, 0, w, h)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        aspect = w / h if h != 0 else 1
        GL.glOrtho(-2 * aspect, 2 * aspect, -2, 2, -10, 10)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def paintGL(self):
        # Reset state OpenGL
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glDisable(GL.GL_TEXTURE_2D)  # Disable texture by default
        GL.glColor3f(1.0, 1.0, 1.0)     # Reset color to white
        
        # Apply transformations
        GL.glTranslatef(self.translation_x, self.translation_y, 0)
        GL.glRotatef(self.rotation_x, 1, 0, 0)
        GL.glRotatef(self.rotation_y, 0, 1, 0)
        GL.glRotatef(self.rotation_z, 0, 0, 1)
        GL.glScalef(self.scale, self.scale, 1)
        
        # Draw based on current scene
        if self.current_scene == 'lightning':
            GL.glDisable(GL.GL_LIGHTING)  # Disable lighting for 2D objects
            self.draw_lightning()
        elif self.current_scene == 'cloud':
            GL.glDisable(GL.GL_LIGHTING)
            self.draw_cloud()
        elif self.current_scene == 'star':
            GL.glEnable(GL.GL_LIGHTING)   # Enable lighting for 3D objects
            self.draw_star()
        elif self.current_scene == 'saturn':
            GL.glEnable(GL.GL_LIGHTING)
            self.draw_saturn()
        elif self.current_scene == 'rainbow':
            GL.glDisable(GL.GL_LIGHTING)
            self.draw_rainbow()
        elif self.current_scene == 'rocket':
            GL.glDisable(GL.GL_LIGHTING)
            self.draw_rocket()
        elif self.current_scene == 'earth':
            GL.glEnable(GL.GL_LIGHTING)
            GL.glEnable(GL.GL_TEXTURE_2D)
            self.draw_earth()
            GL.glDisable(GL.GL_TEXTURE_2D)  # Disable texture after drawing earth
        elif self.current_scene == 'moon':
            GL.glEnable(GL.GL_LIGHTING)
            self.draw_moon()

        # Reset states after drawing
        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glDisable(GL.GL_LIGHTING)

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
            width = self.width()
            height = self.height()
            aspect = width / height if height != 0 else 1
            
            new_x = self.translation_x + dx * self.pan_speed
            new_y = self.translation_y - dy * self.pan_speed  # Invert y-axis
            
            # Batasi translasi
            self.translation_x = max(-2 * aspect, min(2 * aspect, new_x))
            self.translation_y = max(-2.0, min(2.0, new_y))
            
            self.translationChanged.emit(self.translation_x, self.translation_y)
            self.update()
            
        self.last_pos = event.pos()
        
    def wheelEvent(self, event):
        zoom_factor = 1.1
        if event.angleDelta().y() > 0:
            self.scale = min(2.0, self.scale * zoom_factor)  # Batas maksimal 2.0
        else:
            self.scale = max(0.1, self.scale / zoom_factor)  # Batas minimal 0.1
        self.scaleChanged.emit(self.scale)
        self.update()

    def keyPressEvent(self, event):
        """Handle keyboard input for rotation, scaling, and translation"""
        rotation_step = 5.0  # Jumlah derajat untuk setiap rotasi
        scale_step = 0.1     # Jumlah perubahan untuk scaling
        translation_step = 0.1  # Jumlah perubahan untuk translasi
        
        # Get window dimensions
        width = self.width()
        height = self.height()
        aspect = width / height if height != 0 else 1
            
        # Rotation controls
        if event.key() == Qt.Key_Left:
            self.rotation_y = (self.rotation_y - rotation_step) % 360
            self.rotationChanged.emit(self.rotation_x, self.rotation_y, self.rotation_z)
        elif event.key() == Qt.Key_Right:
            self.rotation_y = (self.rotation_y + rotation_step) % 360
            self.rotationChanged.emit(self.rotation_x, self.rotation_y, self.rotation_z)
        elif event.key() == Qt.Key_Up:
            self.rotation_x = (self.rotation_x - rotation_step) % 360
            self.rotationChanged.emit(self.rotation_x, self.rotation_y, self.rotation_z)
        elif event.key() == Qt.Key_Down:
            self.rotation_x = (self.rotation_x + rotation_step) % 360
            self.rotationChanged.emit(self.rotation_x, self.rotation_y, self.rotation_z)
        elif event.key() == Qt.Key_Q:
            self.rotation_z = (self.rotation_z - rotation_step) % 360
            self.rotationChanged.emit(self.rotation_x, self.rotation_y, self.rotation_z)
        elif event.key() == Qt.Key_E:
            self.rotation_z = (self.rotation_z + rotation_step) % 360
            self.rotationChanged.emit(self.rotation_x, self.rotation_y, self.rotation_z)
        # Scaling controls
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:  # Zoom in
            self.scale = min(2.0, self.scale + scale_step)
            self.scaleChanged.emit(self.scale)
        elif event.key() == Qt.Key_Minus:  # Zoom out
            self.scale = max(0.1, self.scale - scale_step)
            self.scaleChanged.emit(self.scale)
        # Translation controls
        # Translation controls
        elif event.key() == Qt.Key_A:  # Move left
            self.translation_x = max(-2 * aspect, self.translation_x - translation_step)
            self.translationChanged.emit(self.translation_x, self.translation_y)
        elif event.key() == Qt.Key_D:  # Move right
            self.translation_x = min(2 * aspect, self.translation_x + translation_step)
            self.translationChanged.emit(self.translation_x, self.translation_y)
        elif event.key() == Qt.Key_W:  # Move up
            self.translation_y = min(2.0, self.translation_y + translation_step)
            self.translationChanged.emit(self.translation_x, self.translation_y)
        elif event.key() == Qt.Key_S:  # Move down
            self.translation_y = max(-2.0, self.translation_y - translation_step)
            self.translationChanged.emit(self.translation_x, self.translation_y)
            self.update()
    def reset_transformations(self):
            """Reset all transformations to default values"""
            self.rotation_x = 0
            self.rotation_y = 0
            self.rotation_z = 0
            self.translation_x = 0
            self.translation_y = 0
            self.scale = 1.0
            
            # Emit signals to update UI
            self.rotationChanged.emit(0, 0, 0)
            self.translationChanged.emit(0, 0)
            self.scaleChanged.emit(1.0)
            
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
        width = self.width()
        height = self.height()
        aspect = width / height if height != 0 else 1
        self.translation_x = max(-2 * aspect, min(2 * aspect, x))
        self.translationChanged.emit(self.translation_x, self.translation_y)
        self.update()

    def set_translation_y(self, y):
        self.translation_y = max(-2.0, min(2.0, y))
        self.translationChanged.emit(self.translation_x, self.translation_y)
        self.update()

    def set_scale(self, scale):
        self.scale = max(0.1, min(2.0, scale))
        self.scaleChanged.emit(self.scale)
        self.update()

    def draw_lightning(self):
        GL.glLineWidth(6.0)
        color = self.object_color.get('lightning', (1.0, 1.0, 0.0))
        GL.glColor3f(*color)
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
        color = self.object_color.get('cloud', (1.0, 1.0, 1.0))
        GL.glColor3f(*color)
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
        body_color = self.object_color.get('rocket', (0.8, 0.8, 0.8))
        
        # Badan roket (trapesium)
        GL.glBegin(GL.GL_POLYGON)
        GL.glColor3f(*body_color)  # Use the selected color
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
        """Draw textured Saturn with rings"""
        if self.saturn_texture is None:
            return
            
        GL.glPushMatrix()
        
        # Gambar bola Saturnus dengan tekstur
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.saturn_texture)
        
        radius = 0.9
        stacks = 32
        slices = 32
        
        # Material properties untuk Saturnus
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        GL.glMaterialf(GL.GL_FRONT, GL.GL_SHININESS, 5.0)
        
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
            
            GL.glBegin(GL.GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j - 1) / slices
                
                # Koordinat tekstur
                s = float(j) / slices
                t1 = float(i) / stacks
                t2 = float(i + 1) / stacks
                
                # Vertex pertama
                x = math.cos(lng) * math.cos(lat0)
                y = math.sin(lng) * math.cos(lat0)
                z = math.sin(lat0)
                GL.glNormal3f(x, y, z)
                GL.glTexCoord2f(s, t1)
                GL.glVertex3f(x * radius, y * radius, z * radius)
                
                # Vertex kedua
                x = math.cos(lng) * math.cos(lat1)
                y = math.sin(lng) * math.cos(lat1)
                z = math.sin(lat1)
                GL.glNormal3f(x, y, z)
                GL.glTexCoord2f(s, t2)
                GL.glVertex3f(x * radius, y * radius, z * radius)
                
            GL.glEnd()
        
        GL.glDisable(GL.GL_TEXTURE_2D)
        
        # Gambar cincin
        GL.glColor3f(0.6, 0.6, 0.6)
        self.draw_ring(1.1, 1.6, 100)
        
        GL.glPopMatrix()

    def draw_ring(self, inner_radius, outer_radius, segments):
        """Draw Saturn's ring with texture"""
        if self.saturn_ring_texture is None:
            return
        
        thickness = 0.1  # Ketebalan cincin
        
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.saturn_ring_texture)
        
        # Material properties untuk cincin
        GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        GL.glMaterialf(GL.GL_FRONT_AND_BACK, GL.GL_SHININESS, 50.0)

        GL.glBegin(GL.GL_QUAD_STRIP)
        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            x = math.cos(theta) * 1.2
            y = math.sin(theta) * 0.7
            
            # Koordinat tekstur
            tex_s = float(i) / segments
            
            # Normal vector untuk pencahayaan yang lebih baik
            GL.glNormal3f(0, 0, 1)
            
            # Bagian dalam cincin
            GL.glTexCoord2f(tex_s, 0.0)
            GL.glVertex3f(x * inner_radius, y * inner_radius, -thickness / 2)
            
            # Bagian luar cincin
            GL.glTexCoord2f(tex_s, 1.0)
            GL.glVertex3f(x * outer_radius, y * outer_radius, -thickness / 2)
            
        GL.glEnd()
        
        # Gambar sisi belakang cincin
        GL.glBegin(GL.GL_QUAD_STRIP)
        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            x = math.cos(theta) * 1.2
            y = math.sin(theta) * 0.7
            
            tex_s = float(i) / segments
            GL.glNormal3f(0, 0, -1)
            
            # Bagian luar cincin
            GL.glTexCoord2f(tex_s, 1.0)
            GL.glVertex3f(x * outer_radius, y * outer_radius, thickness / 2)
            
            # Bagian dalam cincin
            GL.glTexCoord2f(tex_s, 0.0)
            GL.glVertex3f(x * inner_radius, y * inner_radius, thickness / 2)
            
        GL.glEnd()
        
        # Gambar sisi tepi cincin
        GL.glBegin(GL.GL_QUAD_STRIP)
        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            x = math.cos(theta) * 1.2
            y = math.sin(theta) * 0.7
            
            tex_s = float(i) / segments
            
            # Tepi luar
            GL.glTexCoord2f(tex_s, 0.0)
            GL.glVertex3f(x * outer_radius, y * outer_radius, -thickness / 2)
            GL.glTexCoord2f(tex_s, 1.0)
            GL.glVertex3f(x * outer_radius, y * outer_radius, thickness / 2)
            
        GL.glEnd()
        
        # Gambar sisi tepi dalam
        GL.glBegin(GL.GL_QUAD_STRIP)
        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            x = math.cos(theta) * 1.2
            y = math.sin(theta) * 0.7
            
            tex_s = float(i) / segments
            
            # Tepi dalam
            GL.glTexCoord2f(tex_s, 1.0)
            GL.glVertex3f(x * inner_radius, y * inner_radius, thickness / 2)
            GL.glTexCoord2f(tex_s, 0.0)
            GL.glVertex3f(x * inner_radius, y * inner_radius, -thickness / 2)
            
        GL.glEnd()
        
        GL.glDisable(GL.GL_TEXTURE_2D)
        
    def draw_earth(self):
        """Draw textured Earth sphere"""
        if self.earth_texture is None:
            return
            
        GL.glPushMatrix()
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.earth_texture)
        
        radius = 1.0
        stacks = 32
        slices = 32
        
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
            
            GL.glBegin(GL.GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j - 1) / slices
                
                # Koordinat tekstur
                s = float(j) / slices
                t1 = float(i) / stacks
                t2 = float(i + 1) / stacks
                
                # Vertex pertama
                x = math.cos(lng) * math.cos(lat0)
                y = math.sin(lng) * math.cos(lat0)
                z = math.sin(lat0)
                GL.glTexCoord2f(s, t1)
                GL.glVertex3f(x * radius, y * radius, z * radius)
                
                # Vertex kedua
                x = math.cos(lng) * math.cos(lat1)
                y = math.sin(lng) * math.cos(lat1)
                z = math.sin(lat1)
                GL.glTexCoord2f(s, t2)
                GL.glVertex3f(x * radius, y * radius, z * radius)
                
            GL.glEnd()
        
        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glPopMatrix()

    def draw_moon(self):
        """Draw moon shaped like a 3D crescent moon"""
        if self.moon_texture is None:
            return
            
        GL.glPushMatrix()
        
        # Enable texture and set material properties
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.moon_texture)
        
        # Material properties for moon
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        GL.glMaterialf(GL.GL_FRONT, GL.GL_SHININESS, 5.0)
        
        # Rotate to better view the crescent shape
        GL.glRotatef(30, 1, 0, 0)  # Tilt forward
        GL.glRotatef(20, 0, 1, 0)  # Rotate around y-axis
        
        # Draw the crescent shape
        self.draw_c_shape(0.8, 0.3, 36)
        
        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glPopMatrix()

    def draw_c_shape(self, radius, thickness, segments):
        """
        Draw a 3D crescent moon shape (true crescent, not just a C)
        - radius: outer radius of the crescent
        - thickness: maximum thickness in the middle of the crescent
        - segments: number of segments for circular parts
        """
        # Crescent parameters
        start_angle = math.radians(45)
        end_angle = math.radians(315)
        height = thickness
        angle_step = (end_angle - start_angle) / segments

        # Crescent offset (controls how much the inner circle is shifted)
        offset = radius * 0.45  # 0.4~0.5 gives a nice crescent

        # Draw outer surface (outer arc)
        GL.glBegin(GL.GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = start_angle + i * angle_step
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            s = float(i) / segments

            # Outer arc (front)
            GL.glNormal3f(cos_a, sin_a, 0)
            GL.glTexCoord2f(s, 0)
            GL.glVertex3f(radius * cos_a, radius * sin_a, -height/2)
            GL.glTexCoord2f(s, 1)
            GL.glVertex3f(radius * cos_a, radius * sin_a, height/2)
        GL.glEnd()

        # Draw inner surface (inner arc, shifted to create crescent)
        GL.glBegin(GL.GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = start_angle + i * angle_step
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            s = float(i) / segments

            # Inner arc (front, shifted)
            GL.glNormal3f(-cos_a, -sin_a, 0)
            GL.glTexCoord2f(s, 0)
            GL.glVertex3f((radius - thickness) * cos_a + offset, (radius - thickness) * sin_a, -height/2)
            GL.glTexCoord2f(s, 1)
            GL.glVertex3f((radius - thickness) * cos_a + offset, (radius - thickness) * sin_a, height/2)
        GL.glEnd()

        # Draw top face (between outer and inner arcs)
        GL.glBegin(GL.GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = start_angle + i * angle_step
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            s = float(i) / segments

            # Top face
            GL.glNormal3f(0, 0, 1)
            # Inner (shifted)
            GL.glTexCoord2f(s, 0)
            GL.glVertex3f((radius - thickness) * cos_a + offset, (radius - thickness) * sin_a, height/2)
            # Outer
            GL.glTexCoord2f(s, 1)
            GL.glVertex3f(radius * cos_a, radius * sin_a, height/2)
        GL.glEnd()

        # Draw bottom face (between outer and inner arcs)
        GL.glBegin(GL.GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = start_angle + i * angle_step
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            s = float(i) / segments

            # Bottom face
            GL.glNormal3f(0, 0, -1)
            # Outer
            GL.glTexCoord2f(s, 1)
            GL.glVertex3f(radius * cos_a, radius * sin_a, -height/2)
            # Inner (shifted)
            GL.glTexCoord2f(s, 0)
            GL.glVertex3f((radius - thickness) * cos_a + offset, (radius - thickness) * sin_a, -height/2)
        GL.glEnd()

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
        
        # Color Picker for 2D Objects
        self.color_groupbox = QtWidgets.QGroupBox("Warna Objek 2D")
        self.color_groupbox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.color_layout = QtWidgets.QHBoxLayout(self.color_groupbox)
        
        self.color_button = QtWidgets.QPushButton("Pilih Warna")
        self.color_button.setStyleSheet("background-color: rgb(200, 200, 255);")
        self.color_demo = QtWidgets.QFrame()
        self.color_demo.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.color_demo.setFixedSize(50, 30)
        
        self.color_layout.addWidget(self.color_button)
        self.color_layout.addWidget(self.color_demo)
        self.left_panel.addWidget(self.color_groupbox)
        
        
        # Reset button
        self.reset_button = QtWidgets.QPushButton("Reset Transformasi")
        self.reset_button.setStyleSheet("background-color: rgb(255, 200, 200);")
        self.left_panel.addWidget(self.reset_button)
        
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
        
        
        # Reset transformations
        self.reset_button.clicked.connect(self.reset_all_transformations)
        
        # Color picker
        self.color_button.clicked.connect(self.pick_color)
        
        # Connect signals from GLWidget to update UI
        self.glWidget.rotationChanged.connect(self.update_rotation_ui)
        self.glWidget.translationChanged.connect(self.update_translation_ui)
        self.glWidget.scaleChanged.connect(self.update_scale_ui)
        self.glWidget.colorChanged.connect(self.update_color_demo)
    
    
    def reset_all_transformations(self):
        """Reset all transformations and update UI"""
        self.glWidget.reset_transformations()
        
        # Reset UI controls
        self.rotasi_x.setValue(0)
        self.rotasi_y.setValue(0)
        self.rotasi_z.setValue(0)
        self.skala.setValue(1.0)
        
    def pick_color(self):
        """Open color dialog and set color for current 2D object"""
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            r, g, b, _ = color.getRgbF()
            self.glWidget.set_object_color(r, g, b)

    def update_color_demo(self, r, g, b):
        """Update color demo frame with current color"""
        self.color_demo.setStyleSheet(f"background-color: rgb({int(r*255)}, {int(g*255)}, {int(b*255)});")

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