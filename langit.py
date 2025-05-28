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
    translationChanged = pyqtSignal(float, float, float) # Ubah sinyal untuk menyertakan Z
    scaleChanged = pyqtSignal(float)
    scale3DChanged = pyqtSignal(float, float, float)  # Tambah sinyal untuk skala 3D
    colorChanged = pyqtSignal(float, float, float)


    def __init__(self, parent=None):
        super(SceneGLWidget, self).__init__(parent)
        self.setMinimumSize(400, 400)
        self.setFocusPolicy(Qt.StrongFocus)  # Enable keyboard focus
        self.current_scene = 'none'
        self.translation_x = 0
        self.translation_y = 0
        self.translation_z = 0  # Tambah translasi Z
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.scale = 1.0
        self.scale_x = 1.0  # Skala sumbu X
        self.scale_y = 1.0  # Skala sumbu Y
        self.scale_z = 1.0  # Skala sumbu Z
        
        
        self.object_color = {
            'lightning': (1.0, 1.0, 0.0),  # Yellow
            'cloud': (1.0, 1.0, 1.0),      # White
            'rainbow': None,               # Rainbow has multiple colors
            'rocket': (0.8, 0.8, 0.8),         # Rocket has multiple parts with different colors
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
        
        self.setFocusPolicy(Qt.StrongFocus)

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
        # Pastikan Anda memiliki folder 'textures' dengan gambar yang sesuai
        # Contoh: textures/earth.png, textures/moon.png, textures/saturn.png
        self.earth_texture = self.load_texture(os.path.join("textures", "earth.png"))
        self.moon_texture = self.load_texture(os.path.join("textures", "moon.png"))
        self.saturn_texture = self.load_texture(os.path.join("textures", "saturn.png"))
        self.saturn_ring_texture = self.load_texture(os.path.join("textures", "saturn.png"))  # Load tekstur cincin

    def load_texture(self, image_path):
        """Load texture from image file"""
        if not os.path.exists(image_path):
            print(f"Error: Texture file not found at {image_path}")
            return None
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
            print(f"Error loading texture from {image_path}: {e}")
            return None

    def resizeGL(self, w, h):
        GL.glViewport(0, 0, w, h)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        aspect = w / h if h != 0 else 1
        # Gunakan gluPerspective untuk efek 3D yang lebih baik pada translasi Z
        GLU.gluPerspective(45, aspect, 0.1, 100.0) # fovy, aspect, zNear, zFar
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        # Set posisi kamera awal (misalnya sedikit menjauh)
        GLU.gluLookAt(0, 0, 5,  # Posisi kamera (x, y, z)
                      0, 0, 0,  # Titik yang dilihat kamera (center of scene)
                      0, 1, 0)  # Vektor 'up'

    def paintGL(self):
        # Reset state OpenGL
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity() # Reset modelview matrix

        # Set posisi kamera awal (penting untuk perspektif)
        GLU.gluLookAt(0, 0, 5,  # Posisi kamera (x, y, z)
                      0, 0, 0,  # Titik yang dilihat kamera (center of scene)
                      0, 1, 0)  # Vektor 'up'
        
        GL.glDisable(GL.GL_TEXTURE_2D)  # Disable texture by default
        GL.glColor3f(1.0, 1.0, 1.0)      # Reset color to white
        
        # Apply transformations (translasi Z akan lebih terlihat dengan gluPerspective)
        GL.glTranslatef(self.translation_x, self.translation_y, self.translation_z)  # Tambah Z
        GL.glRotatef(self.rotation_x, 1, 0, 0)
        GL.glRotatef(self.rotation_y, 0, 1, 0)
        GL.glRotatef(self.rotation_z, 0, 0, 1)
        GL.glScalef(self.scale_x * self.scale, self.scale_y * self.scale, self.scale_z * self.scale)  # Skala 3D
        
        # Draw based on current scene
        if self.current_scene == 'lightning':
            GL.glDisable(GL.GL_LIGHTING)  # Disable lighting for 2D objects
            self.draw_lightning()
        elif self.current_scene == 'cloud':
            GL.glDisable(GL.GL_LIGHTING)
            self.draw_cloud()
        elif self.current_scene == 'star':
            GL.glEnable(GL.GL_LIGHTING)    # Enable lighting for 3D objects
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
            
            # Memberikan feedback melalui signal
            self.rotationChanged.emit(self.rotation_x, self.rotation_y, self.rotation_z)
            self.update()
            
        if self.is_panning:
            # Pan (X and Y translation)
            # Dapatkan matriks proyeksi saat ini untuk menghitung skala per pixel
            GL.glMatrixMode(GL.GL_PROJECTION)
            proj_matrix = GL.glGetDoublev(GL.GL_PROJECTION_MATRIX)
            GL.glMatrixMode(GL.GL_MODELVIEW)
            
            # Konversi perubahan pixel ke unit OpenGL
            # Ini akan lebih kompleks dengan proyeksi perspektif,
            # untuk kesederhanaan, kita bisa menggunakan pan_speed tetap
            
            new_x = self.translation_x + dx * self.pan_speed
            new_y = self.translation_y - dy * self.pan_speed  # Invert y-axis untuk intuisi natural
            
            # Batasi translasi
            # Batas ini perlu disesuaikan jika menggunakan gluPerspective
            self.translation_x = new_x
            self.translation_y = new_y
            
            self.translationChanged.emit(self.translation_x, self.translation_y, self.translation_z)
            self.update()
            
        self.last_pos = event.pos()
        
    def wheelEvent(self, event):
        zoom_factor = 1.1
        # Zooming in/out now affects Z translation (closer/farther)
        # Instead of scaling the object directly, move the object along Z
        
        if event.angleDelta().y() > 0: # Scroll up (zoom in)
            self.translation_z = max(-10.0, self.translation_z + self.zoom_speed) # Move closer (less negative Z)
        else: # Scroll down (zoom out)
            self.translation_z = min(10.0, self.translation_z - self.zoom_speed) # Move farther (more negative Z)
        
        self.translationChanged.emit(self.translation_x, self.translation_y, self.translation_z)
        self.update()

    def keyPressEvent(self, event):
        """Handle keyboard input for rotation, scaling, and translation"""
        print(f"Key pressed in GLWidget: {event.key()}") # Debugging: cek apakah event diterima

        rotation_step = 5.0
        scale_step = 0.1
        scale3d_step = 0.1  # Step untuk skala 3D
        translation_step = 0.1
        translation_z_step = 0.5  # Tambah step Z, nilai lebih besar agar terlihat

        # Reset transformation
        if event.key() == Qt.Key_R:
            self.reset_transformations()
            return
        
        # Translation controls (W, A, S, D, plus Maju/Mundur via Z-axis)
        elif event.key() == Qt.Key_A: # Kiri
            self.translation_x -= translation_step
        elif event.key() == Qt.Key_D: # Kanan
            self.translation_x += translation_step
        elif event.key() == Qt.Key_W: # Atas
            self.translation_y += translation_step
        elif event.key() == Qt.Key_S: # Bawah
            self.translation_y -= translation_step
        elif event.key() == Qt.Key_Plus: # Maju (Z+)
            self.translation_z += translation_z_step
        elif event.key() == Qt.Key_Minus: # Mundur (Z-)
            self.translation_z -= translation_z_step
            
        # Rotation controls
        elif event.key() == Qt.Key_Left:
            self.rotation_y = (self.rotation_y - rotation_step) % 360
        elif event.key() == Qt.Key_Right:
            self.rotation_y = (self.rotation_y + rotation_step) % 360
        elif event.key() == Qt.Key_Up:
            self.rotation_x = (self.rotation_x - rotation_step) % 360
        elif event.key() == Qt.Key_Down:
            self.rotation_x = (self.rotation_x + rotation_step) % 360
        elif event.key() == Qt.Key_Q:
            self.rotation_z = (self.rotation_z - rotation_step) % 360
        elif event.key() == Qt.Key_E:
            self.rotation_z = (self.rotation_z + rotation_step) % 360
            
        # Scaling controls (Uniform and 3D)
        # Tombol '+' dan '-' sudah digunakan untuk Z-translation,
        # jadi ubah kontrol skala uniform ke tombol lain atau modifikasi.
        # Misalnya, gunakan Ctrl+Plus/Minus untuk skala uniform.
        elif event.key() == Qt.Key_Equal and event.modifiers() & Qt.ShiftModifier: # Shift + = (Plus)
            self.scale = min(2.0, self.scale + scale_step)
        elif event.key() == Qt.Key_Underscore and event.modifiers() & Qt.ShiftModifier: # Shift + - (Minus)
            self.scale = max(0.1, self.scale - scale_step)
        
        # Skala 3D: X/Y/Z (Shift+X/Y/Z untuk sumbu)
        elif event.key() == Qt.Key_X and event.modifiers() & Qt.ShiftModifier:
            self.scale_x = min(2.0, self.scale_x + scale3d_step)
        elif event.key() == Qt.Key_Y and event.modifiers() & Qt.ShiftModifier:
            self.scale_y = min(2.0, self.scale_y + scale3d_step)
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ShiftModifier:
            self.scale_z = min(2.0, self.scale_z + scale3d_step)
        elif event.key() == Qt.Key_X and event.modifiers() & Qt.ControlModifier:
            self.scale_x = max(0.1, self.scale_x - scale3d_step)
        elif event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier:
            self.scale_y = max(0.1, self.scale_y - scale3d_step)
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            self.scale_z = max(0.1, self.scale_z - scale3d_step)
        else:
            super().keyPressEvent(event) # Panggil parent method jika tidak ditangani
            return

        # Update signals and redraw
        self.rotationChanged.emit(self.rotation_x, self.rotation_y, self.rotation_z)
        self.translationChanged.emit(self.translation_x, self.translation_y, self.translation_z) # Emit Z
        self.scaleChanged.emit(self.scale)
        self.scale3DChanged.emit(self.scale_x, self.scale_y, self.scale_z)
        self.update()

    def reset_transformations(self):
        """Reset all transformations to default values"""
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.translation_x = 0
        self.translation_y = 0
        self.translation_z = 0  # Reset Z
        self.scale = 1.0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale_z = 1.0
        
        # Emit signals to update UI
        self.rotationChanged.emit(0, 0, 0)
        self.translationChanged.emit(0, 0, 0) # Emit Z
        self.scaleChanged.emit(1.0)
        self.scale3DChanged.emit(1.0, 1.0, 1.0)
        
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
        self.translationChanged.emit(self.translation_x, self.translation_y, self.translation_z) # Emit Z
        self.update()

    def set_translation_y(self, y):
        self.translation_y = y
        self.translationChanged.emit(self.translation_x, self.translation_y, self.translation_z) # Emit Z
        self.update()

    def set_translation_z(self, z):
        # Batas translasi Z, sesuaikan dengan `gluPerspective` zNear dan zFar
        self.translation_z = max(-90.0, min(90.0, z)) # Sesuaikan rentang ini untuk perspektif
        self.translationChanged.emit(self.translation_x, self.translation_y, self.translation_z)
        self.update()

    def set_scale(self, scale):
        self.scale = max(0.1, min(2.0, scale))
        self.scaleChanged.emit(self.scale)
        self.update()

    def set_scale_x(self, sx):
        self.scale_x = max(0.1, min(2.0, sx))
        self.scale3DChanged.emit(self.scale_x, self.scale_y, self.scale_z)
        self.update()

    def set_scale_y(self, sy):
        self.scale_y = max(0.1, min(2.0, sy))
        self.scale3DChanged.emit(self.scale_x, self.scale_y, self.scale_z)
        self.update()

    def set_scale_z(self, sz):
        self.scale_z = max(0.1, min(2.0, sz))
        self.scale3DChanged.emit(self.scale_x, self.scale_y, self.scale_z)
        self.update()

    def draw_lightning(self):
        # Draw the filled lightning bolt
        GL.glColor3f(1.0, 0.9, 0.1)  # Warna kuning terang
        
        # Points defining a more classic lightning bolt shape
        points = [
            (0.0, 1.0),      # Titik atas
            (-0.2, 0.4),     # Miring ke kiri bawah
            (0.1, 0.4),      # Sedikit kanan
            (-0.3, -0.2),    # Miring ke kiri bawah
            (0.0, -0.2),     # Ke kanan
            (-0.5, -1.0)     # Ujung bawah
        ]
        
            # Gambar isi petir
        GL.glBegin(GL.GL_POLYGON)
        for x, y in points:
            GL.glVertex2f(x, y)
        GL.glEnd()
        # Glow yang lebih kompleks
        glow_layers = [
            (1.0, 1.0, 0.8, 0.4, 0.05),  # Cahaya terluar, sangat terang, transparan
            (1.0, 1.0, 0.6, 0.6, 0.03),  # Lapisan kedua
            (1.0, 0.9, 0.3, 0.8, 0.01)   # Lapisan terdalam, lebih padat
        ]

        # Aktifkan blending untuk transparansi
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        for r, g, b, a, offset in glow_layers:
            GL.glColor4f(r, g, b, a)
            # Ketebalan garis bisa diatur agar terlihat seperti "blur"
            GL.glLineWidth(5.0 * (1.0 - offset)) # Mengatur ketebalan berdasarkan offset

            GL.glBegin(GL.GL_LINE_LOOP)
            for x, y in points:
                # Menggeser titik untuk menciptakan efek glow
                GL.glVertex2f(x * (1.0 + offset), y * (1.0 + offset))
            GL.glEnd()

        GL.glDisable(GL.GL_BLEND) # Nonaktifkan blending setelah selesai

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
            (0.7, 0.0, 1.0)    # Violet
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
        GL.glVertex2f(-0.1, -0.5)    # Kiri bawah
        GL.glVertex2f(0.1, -0.5)     # Kanan bawah
        GL.glVertex2f(0.2, 0.3)      # Kanan atas
        GL.glVertex2f(-0.2, 0.3)     # Kiri atas
        GL.glEnd()

        # Kepala roket (segitiga)
        GL.glBegin(GL.GL_TRIANGLES)
        GL.glColor3f(1.0, 0.0, 0.0)  # Red
        GL.glVertex2f(-0.2, 0.3)     # Kiri
        GL.glVertex2f(0.2, 0.3)      # Kanan
        GL.glVertex2f(0.0, 0.7)      # Puncak
        GL.glEnd()

        # Sayap kiri
        GL.glBegin(GL.GL_TRIANGLES)
        GL.glColor3f(0.6, 0.6, 0.6)  # Dark gray
        GL.glVertex2f(-0.1, -0.3)    # Atas
        GL.glVertex2f(-0.1, -0.5)    # Bawah
        GL.glVertex2f(-0.3, -0.5)    # Ujung sayap
        GL.glEnd()

        # Sayap kanan
        GL.glBegin(GL.GL_TRIANGLES)
        GL.glColor3f(0.6, 0.6, 0.6)  # Dark gray
        GL.glVertex2f(0.1, -0.3)     # Atas
        GL.glVertex2f(0.1, -0.5)     # Bawah
        GL.glVertex2f(0.3, -0.5)     # Ujung sayap
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
        """Draw a 3D star with better depth and symmetry"""
        outer_radius = 1.0
        inner_radius = 0.4
        depth = 0.3

        # Create 10 points for star outline (alternating outer and inner)
        points = []
        for i in range(10):
            angle = math.radians(i * 36)  # 360/10 = 36 degrees per point
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            # Give subtle 3D contour using sine wave pattern
            z = math.sin(i * math.pi / 5) * (depth * 0.2)
            points.append((x, y, z))

        # --- Front face ---
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glColor3f(1.0, 0.84, 0.0)
        GL.glVertex3f(0, 0, depth)  # Center raised
        for i, (x, y, z) in enumerate(points + [points[0]]):
            if i % 2 == 0:
                GL.glColor3f(1.0, 0.7, 0.0)
            else:
                GL.glColor3f(1.0, 0.9, 0.4)
            GL.glVertex3f(x, y, z + depth * 0.1)
        GL.glEnd()

        # --- Back face ---
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glColor3f(1.0, 0.84, 0.0)
        GL.glVertex3f(0, 0, -depth)
        for i, (x, y, z) in enumerate(reversed(points + [points[-1]])):
            if i % 2 == 0:
                GL.glColor3f(1.0, 0.5, 0.0)
            else:
                GL.glColor3f(1.0, 0.8, 0.3)
            GL.glVertex3f(x, y, -z - depth * 0.1)
        GL.glEnd()

        # --- Sides ---
        GL.glBegin(GL.GL_QUAD_STRIP)
        for i in range(len(points) + 1):
            idx = i % len(points)
            x, y, z = points[idx]
            zf = z + depth * 0.1
            zb = -z - depth * 0.1

            color_factor = i / len(points)
            GL.glColor3f(1.0, 0.6 + 0.3 * color_factor, 0.2)
            GL.glVertex3f(x, y, zf)
            GL.glColor3f(1.0, 0.5 + 0.3 * color_factor, 0.0)
            GL.glVertex3f(x, y, zb)
        GL.glEnd()


    def draw_cone(self, base, direction, radius, length, color):
        """Helper function to draw a simple cone"""
        GL.glPushMatrix()
        GL.glTranslatef(*base)

        dir_len = math.sqrt(sum(d**2 for d in direction))
        if dir_len == 0:
            dir_len = 1e-5  # avoid division by zero

        ax, ay, az = 0, 0, 1
        dx, dy, dz = [d / dir_len for d in direction]

        rx = ay * dz - az * dy
        ry = az * dx - ax * dz
        rz = ax * dy - ay * dx
        angle_rad = math.acos(dz)
        angle_deg = math.degrees(angle_rad)

        if rx != 0 or ry != 0 or rz != 0:
            GL.glRotatef(angle_deg, rx, ry, rz)

        GL.glColor3f(*color)
        quadric = GLU.gluNewQuadric()
        GLU.gluCylinder(quadric, radius, 0.0, length, 10, 1)
        GLU.gluDeleteQuadric(quadric)

        GL.glPopMatrix()

    def draw_saturn(self):
        """Draw textured Saturn with rings"""
        if self.saturn_texture is None:
            return

        GL.glPushMatrix()

        # Gambar bola Saturnus dengan tekstur
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.saturn_texture)

        radius = 0.91
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
            y = math.sin(theta) * 0.9

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
            y = math.sin(theta) * 0.9

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
            y = math.sin(theta) * 0.9

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
            y = math.sin(theta) * 0.9

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
                GL.glNormal3f(x, y, z) # Normal untuk pencahayaan
                GL.glTexCoord2f(s, t1)
                GL.glVertex3f(x * radius, y * radius, z * radius)
                
                # Vertex kedua
                x = math.cos(lng) * math.cos(lat1)
                y = math.sin(lng) * math.cos(lat1)
                z = math.sin(lat1)
                GL.glNormal3f(x, y, z) # Normal untuk pencahayaan
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
          # Tambahkan Tab Control untuk transformasi yang lebih jelas
        self.transform_tabs = QtWidgets.QTabWidget()
        self.transform_tabs.setStyleSheet("background-color: rgb(255, 255, 255);")
        
        # === Tab Rotasi ===
        self.rotation_tab = QtWidgets.QWidget()
        self.rotation_layout = QtWidgets.QVBoxLayout(self.rotation_tab)
        
        # Rotasi X
        self.rotasi_x_groupbox = QtWidgets.QGroupBox("Rotasi X")
        self.rotasi_x_layout = QtWidgets.QHBoxLayout(self.rotasi_x_groupbox)
        
        self.rotasi_x = QtWidgets.QDoubleSpinBox()
        self.rotasi_x.setRange(0, 360)
        self.rotasi_x.setSingleStep(1)
        self.rotasi_x.setValue(0)
        self.view_rotasi_x = QtWidgets.QPushButton("Apply")
        
        self.rotasi_x_layout.addWidget(self.rotasi_x)
        self.rotasi_x_layout.addWidget(self.view_rotasi_x)
        self.rotation_layout.addWidget(self.rotasi_x_groupbox)
        
        # Rotasi Y
        self.rotasi_y_groupbox = QtWidgets.QGroupBox("Rotasi Y")
        self.rotasi_y_layout = QtWidgets.QHBoxLayout(self.rotasi_y_groupbox)
        
        self.rotasi_y = QtWidgets.QDoubleSpinBox()
        self.rotasi_y.setRange(0, 360)
        self.rotasi_y.setSingleStep(1)
        self.rotasi_y.setValue(0)
        self.view_rotasi_y = QtWidgets.QPushButton("Apply")
        
        self.rotasi_y_layout.addWidget(self.rotasi_y)
        self.rotasi_y_layout.addWidget(self.view_rotasi_y)
        self.rotation_layout.addWidget(self.rotasi_y_groupbox)
        
        # Rotasi Z
        self.rotasi_z_groupbox = QtWidgets.QGroupBox("Rotasi Z")
        self.rotasi_z_layout = QtWidgets.QHBoxLayout(self.rotasi_z_groupbox)
        
        self.rotasi_z = QtWidgets.QDoubleSpinBox()
        self.rotasi_z.setRange(0, 360)
        self.rotasi_z.setSingleStep(1)
        self.rotasi_z.setValue(0)
        self.view_rotasi_z = QtWidgets.QPushButton("Apply")
        
        self.rotasi_z_layout.addWidget(self.rotasi_z)
        self.rotasi_z_layout.addWidget(self.view_rotasi_z)
        self.rotation_layout.addWidget(self.rotasi_z_groupbox)
        
        # Tombol-tombol cepat untuk rotasi
        self.rotation_buttons = QtWidgets.QGridLayout()
        self.rot_x_plus = QtWidgets.QPushButton("X+")
        self.rot_x_minus = QtWidgets.QPushButton("X-")
        self.rot_y_plus = QtWidgets.QPushButton("Y+")
        self.rot_y_minus = QtWidgets.QPushButton("Y-")
        self.rot_z_plus = QtWidgets.QPushButton("Z+")
        self.rot_z_minus = QtWidgets.QPushButton("Z-")
        
        self.rotation_buttons.addWidget(self.rot_x_plus, 0, 0)
        self.rotation_buttons.addWidget(self.rot_x_minus, 0, 1)
        self.rotation_buttons.addWidget(self.rot_y_plus, 1, 0)
        self.rotation_buttons.addWidget(self.rot_y_minus, 1, 1)
        self.rotation_buttons.addWidget(self.rot_z_plus, 2, 0)
        self.rotation_buttons.addWidget(self.rot_z_minus, 2, 1)
        
        self.rotation_layout.addLayout(self.rotation_buttons)
        self.transform_tabs.addTab(self.rotation_tab, "Rotasi")
        
        # === Tab Translasi ===
        self.translation_tab = QtWidgets.QWidget()
        self.translation_layout = QtWidgets.QVBoxLayout(self.translation_tab)
        
        # Translasi X
        self.translasi_x_groupbox = QtWidgets.QGroupBox("Translasi X")
        self.translasi_x_layout = QtWidgets.QHBoxLayout(self.translasi_x_groupbox)
        self.translasi_x = QtWidgets.QDoubleSpinBox()
        self.translasi_x.setRange(-5.0, 5.0)
        self.translasi_x.setSingleStep(0.1)
        self.translasi_x.setValue(0.0)
        self.translasi_x_layout.addWidget(self.translasi_x)
        self.translation_layout.addWidget(self.translasi_x_groupbox)

        # Translasi Y
        self.translasi_y_groupbox = QtWidgets.QGroupBox("Translasi Y")
        self.translasi_y_layout = QtWidgets.QHBoxLayout(self.translasi_y_groupbox)
        self.translasi_y = QtWidgets.QDoubleSpinBox()
        self.translasi_y.setRange(-5.0, 5.0)
        self.translasi_y.setSingleStep(0.1)
        self.translasi_y.setValue(0.0)
        self.translasi_y_layout.addWidget(self.translasi_y)
        self.translation_layout.addWidget(self.translasi_y_groupbox)

        # Translasi Z (tambahan untuk maju/mundur)
        self.translasi_z_groupbox = QtWidgets.QGroupBox("Translasi Z")
        self.translasi_z_layout = QtWidgets.QHBoxLayout(self.translasi_z_groupbox)
        self.translasi_z = QtWidgets.QDoubleSpinBox()
        self.translasi_z.setRange(-90.0, 90.0) # Sesuaikan rentang ini dengan gluPerspective
        self.translasi_z.setSingleStep(0.5) # Sesuaikan step
        self.translasi_z.setValue(0.0)
        self.translasi_z_layout.addWidget(self.translasi_z)
        self.translation_layout.addWidget(self.translasi_z_groupbox)

        # Tombol arah translasi
        self.trans_groupbox = QtWidgets.QGroupBox("Arah Translasi Cepat")
        self.trans_layout = QtWidgets.QGridLayout(self.trans_groupbox)
        
        self.kiri = QtWidgets.QPushButton("Kiri (X-)")
        self.kanan = QtWidgets.QPushButton("Kanan (X+)")
        self.atas = QtWidgets.QPushButton("Atas (Y+)")
        self.bawah = QtWidgets.QPushButton("Bawah (Y-)")
        self.maju = QtWidgets.QPushButton("Maju (Z+)")       # Tambah tombol Z+
        self.mundur = QtWidgets.QPushButton("Mundur (Z-)")   # Tambah tombol Z-
        
        self.trans_layout.addWidget(self.atas, 0, 1)
        self.trans_layout.addWidget(self.kiri, 1, 0)
        self.trans_layout.addWidget(self.kanan, 1, 2)
        self.trans_layout.addWidget(self.bawah, 2, 1)
        self.trans_layout.addWidget(self.maju, 0, 2)    # Letak tombol Maju
        self.trans_layout.addWidget(self.mundur, 2, 2)  # Letak tombol Mundur
        
        self.translation_layout.addWidget(self.trans_groupbox)
        self.transform_tabs.addTab(self.translation_tab, "Translasi")
        
        # === Tab Skala ===
        self.scale_tab = QtWidgets.QWidget()
        self.scale_layout = QtWidgets.QVBoxLayout(self.scale_tab)
        
        # Skala Uniform
        self.skala_groupbox = QtWidgets.QGroupBox("Skala Uniform")
        self.skala_uni_layout = QtWidgets.QHBoxLayout(self.skala_groupbox)

        self.skala = QtWidgets.QDoubleSpinBox()
        self.skala.setRange(0.1, 2.0)
        self.skala.setSingleStep(0.1)
        self.skala.setValue(1.0)
        self.view_skala = QtWidgets.QPushButton("Apply")

        self.skala_uni_layout.addWidget(self.skala)
        self.skala_uni_layout.addWidget(self.view_skala)
        self.scale_layout.addWidget(self.skala_groupbox)
        
        # Skala 3D Per Sumbu (baru)
        self.skala_3d_groupbox = QtWidgets.QGroupBox("Skala Per Sumbu (3D)")
        self.skala_3d_layout = QtWidgets.QGridLayout(self.skala_3d_groupbox)

        self.label_sx = QtWidgets.QLabel("Skala X:")
        self.skala_x = QtWidgets.QDoubleSpinBox()
        self.skala_x.setRange(0.1, 5.0)
        self.skala_x.setSingleStep(0.1)
        self.skala_x.setValue(1.0)
        self.skala_x_apply = QtWidgets.QPushButton("Apply")

        self.label_sy = QtWidgets.QLabel("Skala Y:")
        self.skala_y = QtWidgets.QDoubleSpinBox()
        self.skala_y.setRange(0.1, 5.0)
        self.skala_y.setSingleStep(0.1)
        self.skala_y.setValue(1.0)
        self.skala_y_apply = QtWidgets.QPushButton("Apply")

        self.label_sz = QtWidgets.QLabel("Skala Z:")
        self.skala_z = QtWidgets.QDoubleSpinBox()
        self.skala_z.setRange(0.1, 5.0)
        self.skala_z.setSingleStep(0.1)
        self.skala_z.setValue(1.0)
        self.skala_z_apply = QtWidgets.QPushButton("Apply")

        self.skala_3d_layout.addWidget(self.label_sx, 0, 0)
        self.skala_3d_layout.addWidget(self.skala_x, 0, 1)
        self.skala_3d_layout.addWidget(self.skala_x_apply, 0, 2)
        self.skala_3d_layout.addWidget(self.label_sy, 1, 0)
        self.skala_3d_layout.addWidget(self.skala_y, 1, 1)
        self.skala_3d_layout.addWidget(self.skala_y_apply, 1, 2)
        self.skala_3d_layout.addWidget(self.label_sz, 2, 0)
        self.skala_3d_layout.addWidget(self.skala_z, 2, 1)
        self.skala_3d_layout.addWidget(self.skala_z_apply, 2, 2)

        self.scale_layout.addWidget(self.skala_3d_groupbox)

        # Tombol cepat untuk skala
        self.scale_buttons = QtWidgets.QHBoxLayout()
        self.scale_up = QtWidgets.QPushButton("Perbesar")
        self.scale_down = QtWidgets.QPushButton("Perkecil")
        self.scale_reset = QtWidgets.QPushButton("Reset (1.0)")
        
        self.scale_buttons.addWidget(self.scale_up)
        self.scale_buttons.addWidget(self.scale_down)
        self.scale_buttons.addWidget(self.scale_reset)
        
        self.scale_layout.addLayout(self.scale_buttons)
        self.transform_tabs.addTab(self.scale_tab, "Skala")
        
        # Tambahkan tab transformasi ke tata letak utama
        self.left_panel.addWidget(self.transform_tabs)
        
        # Tambahkan keyboard shortcut help
        self.shortcut_groupbox = QtWidgets.QGroupBox("Keyboard Shortcuts")
        self.shortcut_groupbox.setMaximumHeight(150)
        self.shortcut_groupbox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.shortcut_layout = QtWidgets.QVBoxLayout(self.shortcut_groupbox)
        
        self.shortcut_info = QtWidgets.QTextEdit()
        self.shortcut_info.setReadOnly(True)
        self.shortcut_info.setHtml("""
        <p><b>Rotasi:</b> Arrow Keys (X/Y), Q/E (Z axis)</p>
        <p><b>Translasi:</b> W, A, S, D (X/Y), + / - (Z axis)</p>
        <p><b>Skala:</b> Shift + = (Perbesar), Shift + - (Perkecil)</p>
        <p><b>Skala Sumbu:</b> Shift + X/Y/Z (Perbesar), Ctrl + X/Y/Z (Perkecil)</p>
        <p><b>Reset:</b> R key</p>
        """)
        
        self.shortcut_layout.addWidget(self.shortcut_info)
        self.left_panel.addWidget(self.shortcut_groupbox)
        
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
        
        # Pastikan GLWidget mendapatkan fokus saat aplikasi dimulai
        QtCore.QTimer.singleShot(100, self.glWidget.setFocus)

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
        
        # Translation controls (Buttons)
        self.kiri.clicked.connect(lambda: self.glWidget.set_translation_x(self.glWidget.translation_x - 0.1))
        self.kanan.clicked.connect(lambda: self.glWidget.set_translation_x(self.glWidget.translation_x + 0.1))
        self.atas.clicked.connect(lambda: self.glWidget.set_translation_y(self.glWidget.translation_y + 0.1))
        self.bawah.clicked.connect(lambda: self.glWidget.set_translation_y(self.glWidget.translation_y - 0.1))
        self.maju.clicked.connect(lambda: self.glWidget.set_translation_z(self.glWidget.translation_z + 0.5))    # Z+
        self.mundur.clicked.connect(lambda: self.glWidget.set_translation_z(self.glWidget.translation_z - 0.5))  # Z-
        
        # Translation controls (SpinBoxes)
        self.translasi_x.valueChanged.connect(self.glWidget.set_translation_x)
        self.translasi_y.valueChanged.connect(self.glWidget.set_translation_y)
        self.translasi_z.valueChanged.connect(self.glWidget.set_translation_z)

        # Rotation controls (SpinBoxes)
        self.view_rotasi_x.clicked.connect(lambda: self.glWidget.set_rotation_x(self.rotasi_x.value()))
        self.view_rotasi_y.clicked.connect(lambda: self.glWidget.set_rotation_y(self.rotasi_y.value()))
        self.view_rotasi_z.clicked.connect(lambda: self.glWidget.set_rotation_z(self.rotasi_z.value()))
        
        # Quick rotation buttons
        self.rot_x_plus.clicked.connect(lambda: self.glWidget.set_rotation_x(self.glWidget.rotation_x + 5))
        self.rot_x_minus.clicked.connect(lambda: self.glWidget.set_rotation_x(self.glWidget.rotation_x - 5))
        self.rot_y_plus.clicked.connect(lambda: self.glWidget.set_rotation_y(self.glWidget.rotation_y + 5))
        self.rot_y_minus.clicked.connect(lambda: self.glWidget.set_rotation_y(self.glWidget.rotation_y - 5))
        self.rot_z_plus.clicked.connect(lambda: self.glWidget.set_rotation_z(self.glWidget.rotation_z + 5))
        self.rot_z_minus.clicked.connect(lambda: self.glWidget.set_rotation_z(self.glWidget.rotation_z - 5))
        
        # Scale control (Uniform)
        self.view_skala.clicked.connect(lambda: self.glWidget.set_scale(self.skala.value()))
        self.scale_up.clicked.connect(lambda: self.glWidget.set_scale(min(2.0, self.glWidget.scale + 0.1)))
        self.scale_down.clicked.connect(lambda: self.glWidget.set_scale(max(0.1, self.glWidget.scale - 0.1)))
        self.scale_reset.clicked.connect(lambda: self.glWidget.set_scale(1.0))
        
        # Scale 3D controls (Per-axis)
        self.skala_x_apply.clicked.connect(lambda: self.glWidget.set_scale_x(self.skala_x.value()))
        self.skala_y_apply.clicked.connect(lambda: self.glWidget.set_scale_y(self.skala_y.value()))
        self.skala_z_apply.clicked.connect(lambda: self.glWidget.set_scale_z(self.skala_z.value()))
        
        # Reset transformations
        self.reset_button.clicked.connect(self.reset_all_transformations)
        
        # Color picker
        self.color_button.clicked.connect(self.pick_color)
        
        # Connect signals from GLWidget to update UI
        self.glWidget.rotationChanged.connect(self.update_rotation_ui)
        self.glWidget.translationChanged.connect(self.update_translation_ui)
        self.glWidget.scaleChanged.connect(self.update_scale_ui)
        self.glWidget.scale3DChanged.connect(self.update_scale3d_ui) # Connect 3D scale signal
        self.glWidget.colorChanged.connect(self.update_color_demo)
        
        # Pastikan widget OpenGL memiliki fokus untuk input keyboard
        # Set focus policy and focus
        self.glWidget.setFocusPolicy(Qt.StrongFocus)
        self.glWidget.setFocus()
        
        # Connect to widget's focusInEvent untuk debugging
        self.glWidget.focusInEvent = lambda event: print("OpenGL widget has gained focus")

    def update_translation_ui(self, x, y, z):
        """Update translation UI widgets with current values"""
        self.translasi_x.setValue(x)
        self.translasi_y.setValue(y)
        self.translasi_z.setValue(z) # Update Z translation spin box
        
        # Debugging
        print(f"Translation updated: x={x}, y={y}, z={z}")

    def reset_all_transformations(self):
        """Reset all transformations and update UI"""
        self.glWidget.reset_transformations()
        
        # Reset UI controls
        self.rotasi_x.setValue(0)
        self.rotasi_y.setValue(0)
        self.rotasi_z.setValue(0)
        self.translasi_x.setValue(0)
        self.translasi_y.setValue(0)
        self.translasi_z.setValue(0) # Reset Z spin box
        self.skala.setValue(1.0)
        self.skala_x.setValue(1.0) # Reset 3D scale
        self.skala_y.setValue(1.0) # Reset 3D scale
        self.skala_z.setValue(1.0) # Reset 3D scale

        
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

    def update_scale_ui(self, scale):
        self.skala.setValue(scale)

    def update_scale3d_ui(self, sx, sy, sz):
        self.skala_x.setValue(sx)
        self.skala_y.setValue(sy)
        self.skala_z.setValue(sz)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        
        # Title
        self.JUDUL.setHtml(_translate("MainWindow", 
            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:7.875pt; font-weight:400; font-style:normal;\">\n"
            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600; color:#ffffff;\">ATAP LANGIT</span></p></body></html>"))
        
        MainWindow.setWindowTitle(_translate("MainWindow", "OpenGL Viewer"))
        self.groupBox_objek2d.setTitle(_translate("MainWindow", "Objek 2D"))
        self.petir.setText(_translate("MainWindow", "Petir"))
        self.awan.setText(_translate("MainWindow", "Awan"))
        self.pelangi.setText(_translate("MainWindow", "Pelangi"))
        self.roket.setText(_translate("MainWindow", "Roket"))
        self.groupBox_objek3d.setTitle(_translate("MainWindow", "Objek 3D"))
        self.star.setText(_translate("MainWindow", "Bintang"))
        self.saturn.setText(_translate("MainWindow", "Saturnus"))
        self.earth.setText(_translate("MainWindow", "Bumi"))
        self.moon.setText(_translate("MainWindow", "Bulan"))
        self.transform_tabs.setTabText(self.transform_tabs.indexOf(self.rotation_tab), _translate("MainWindow", "Rotasi"))
        self.rotasi_x_groupbox.setTitle(_translate("MainWindow", "Rotasi X"))
        self.view_rotasi_x.setText(_translate("MainWindow", "Apply"))
        self.rotasi_y_groupbox.setTitle(_translate("MainWindow", "Rotasi Y"))
        self.view_rotasi_y.setText(_translate("MainWindow", "Apply"))
        self.rotasi_z_groupbox.setTitle(_translate("MainWindow", "Rotasi Z"))
        self.view_rotasi_z.setText(_translate("MainWindow", "Apply"))
        self.rot_x_plus.setText(_translate("MainWindow", "X+"))
        self.rot_x_minus.setText(_translate("MainWindow", "X-"))
        self.rot_y_plus.setText(_translate("MainWindow", "Y+"))
        self.rot_y_minus.setText(_translate("MainWindow", "Y-"))
        self.rot_z_plus.setText(_translate("MainWindow", "Z+"))
        self.rot_z_minus.setText(_translate("MainWindow", "Z-"))

        self.transform_tabs.setTabText(self.transform_tabs.indexOf(self.translation_tab), _translate("MainWindow", "Translasi"))
        self.translasi_x_groupbox.setTitle(_translate("MainWindow", "Translasi X"))
        self.translasi_y_groupbox.setTitle(_translate("MainWindow", "Translasi Y"))
        self.translasi_z_groupbox.setTitle(_translate("MainWindow", "Translasi Z"))
        self.trans_groupbox.setTitle(_translate("MainWindow", "Arah Translasi Cepat"))
        self.kiri.setText(_translate("MainWindow", "Kiri (X-)"))
        self.kanan.setText(_translate("MainWindow", "Kanan (X+)"))
        self.atas.setText(_translate("MainWindow", "Atas (Y+)"))
        self.bawah.setText(_translate("MainWindow", "Bawah (Y-)"))
        self.maju.setText(_translate("MainWindow", "Maju (Z+)"))
        self.mundur.setText(_translate("MainWindow", "Mundur (Z-)"))

        self.transform_tabs.setTabText(self.transform_tabs.indexOf(self.scale_tab), _translate("MainWindow", "Skala"))
        self.skala_groupbox.setTitle(_translate("MainWindow", "Skala Uniform"))
        self.view_skala.setText(_translate("MainWindow", "Apply"))
        self.skala_3d_groupbox.setTitle(_translate("MainWindow", "Skala Per Sumbu (3D)"))
        self.skala_x_apply.setText(_translate("MainWindow", "Apply"))
        self.skala_y_apply.setText(_translate("MainWindow", "Apply"))
        self.skala_z_apply.setText(_translate("MainWindow", "Apply"))
        self.scale_up.setText(_translate("MainWindow", "Perbesar"))
        self.scale_down.setText(_translate("MainWindow", "Perkecil"))
        self.scale_reset.setText(_translate("MainWindow", "Reset (1.0)"))
        self.color_groupbox.setTitle(_translate("MainWindow", "Warna Objek 2D"))
        self.color_button.setText(_translate("MainWindow", "Pilih Warna"))
        self.reset_button.setText(_translate("MainWindow", "Reset Transformasi"))


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