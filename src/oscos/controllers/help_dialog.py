#!/usr/bin/env python3
"""
Help Dialog Module for the Oscillation Control System GUI
Provides an interactive bilingual manual with navigation.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QTextBrowser
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import os


class HelpDialog(QDialog):
    """
    Dialog that displays the help manual for the application.
    Supports English and Spanish with interactive navigation.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help - Manual")
        self.setSize(1000, 700)
        self.current_language = "es"  # Default to Spanish
        self.setup_ui()
        self.load_manual()
        
    def setSize(self, width, height):
        """Set the dialog size"""
        self.resize(QSize(width, height))
        
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Top control panel
        control_layout = QHBoxLayout()
        
        # Language selector
        lang_label = QLabel("Language / Idioma:")
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Español", "es")
        self.language_combo.setCurrentIndex(1)  # Default Spanish
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
        control_layout.addWidget(lang_label)
        control_layout.addWidget(self.language_combo)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # Text browser for content
        self.text_browser = QTextBrowser()
        layout.addWidget(self.text_browser)
        
        # Navigation buttons
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def on_language_changed(self):
        """Handle language change"""
        self.current_language = self.language_combo.currentData()
        self.load_manual()
        
    def load_manual(self):
        """Load the appropriate manual based on current language"""
        if self.current_language == "es":
            html_content = self.get_spanish_manual()
        else:
            html_content = self.get_english_manual()
            
        self.text_browser.setHtml(html_content)
        
    def get_spanish_manual(self):
        """Return the Spanish version of the manual"""
        return """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
                h1 { color: #1f5fa1; border-bottom: 3px solid #1f5fa1; padding-bottom: 10px; }
                h2 { color: #2196F3; margin-top: 30px; }
                h3 { color: #424242; margin-top: 15px; }
                .section { margin-bottom: 30px; }
                .button-desc { background-color: #f5f5f5; padding: 10px; margin: 10px 0; border-left: 4px solid #2196F3; }
                table { border-collapse: collapse; width: 100%; margin: 15px 0; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #2196F3; color: white; }
                .toc { background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .toc ul { list-style-type: none; padding-left: 0; }
                .toc a { color: #1f5fa1; text-decoration: none; font-weight: bold; }
                .toc a:hover { text-decoration: underline; }
                .warning { background-color: #fff3e0; padding: 10px; margin: 10px 0; border-left: 4px solid #ff9800; }
                .tip { background-color: #e8f5e9; padding: 10px; margin: 10px 0; border-left: 4px solid #4caf50; }
            </style>
        </head>
        <body>
        
        <h1>📘 Manual de Usuario - Sistema de Control de Oscilaciones</h1>
        
        <div class="toc">
            <h3>📑 Índice de Contenidos</h3>
            <ul>
                <li><a href="#intro">1. Introducción</a></li>
                <li><a href="#connection">2. Pestaña de Conexión</a></li>
                <li><a href="#control">3. Pestaña de Control</a></li>
                <li><a href="#imaging">4. Pestaña de Adquisición de Imágenes</a></li>
                <li><a href="#tips">5. Consejos y Solución de Problemas</a></li>
            </ul>
        </div>
        
        <div class="section" id="intro">
            <h2>1. Introducción 🚀</h2>
            <p>Bienvenido al Sistema de Control de Oscilaciones. Esta aplicación le permite:</p>
            <ul>
                <li>Conectarse a dispositivos de control y telemetría por Bluetooth o Serial</li>
                <li>Configurar y monitorear parámetros de oscilación (RPM, velocidad, aceleración)</li>
                <li>Adquirir y gestionar imágenes sincronizadas con los parámetros de oscilación</li>
                <li>Exportar datos para análisis posterior</li>
            </ul>
            <p>La interfaz está dividida en tres pestañas principales que se describen en detalle a continuación.</p>
        </div>
        
        <div class="section" id="connection">
            <h2>2. Pestaña de Conexión 🔌</h2>
            <p>Esta es la primera pestaña donde configura las conexiones con los dispositivos necesarios.</p>
            
            <h3>Sección de Control (Lado Izquierdo)</h3>
            
            <div class="button-desc">
                <strong>Bluetooth / Serial (Radio Buttons)</strong><br>
                Seleccione el tipo de conexión para el dispositivo de control:
                <ul>
                    <li><strong>Bluetooth:</strong> Conexión inalámbrica (actualmente deshabilitada en la versión actual)</li>
                    <li><strong>Serial (Por defecto):</strong> Conexión por puerto COM/Serial</li>
                </ul>
            </div>
            
            <div class="button-desc">
                <strong>Puerto Serial (Dropdown + Botón de Actualizar 🔄)</strong><br>
                Seleccione el puerto COM donde está conectado su dispositivo de control.
                El botón de actualizar (icono de recarga) busca nuevos puertos disponibles.
                <div class="tip">💡 <strong>Consejo:</strong> Si no aparece su puerto, haga clic en el botón de actualizar.</div>
            </div>
            
            <div class="button-desc">
                <strong>Velocidad en Baudios (Baud Rate)</strong><br>
                Seleccione la velocidad de comunicación. Valores comunes: 9600, 115200, etc.
                <div class="warning">⚠️ <strong>Importante:</strong> Asegúrese de que coincida con la configuración de su dispositivo.</div>
            </div>
            
            <div class="button-desc">
                <strong>Botón Conectar 🟢</strong><br>
                Establece la conexión con el dispositivo de control usando los parámetros seleccionados.
                Se habilitará después de seleccionar un puerto.
            </div>
            
            <div class="button-desc">
                <strong>Botón Desconectar 🔴</strong><br>
                Cierra la conexión con el dispositivo de control.
                Solo está disponible cuando una conexión está activa.
            </div>
            
            <h3>Sección de Telemetría</h3>
            <p>De manera similar a la sección de Control, aquí configura la conexión con el dispositivo de telemetría que envía datos de sensores.</p>
            
            <h3>Consolas de Comunicación</h3>
            <p>Dos pestañas secundarias muestran la comunicación en tiempo real:</p>
            <div class="button-desc">
                <strong>Control / Telemetry Console</strong><br>
                Muestra mensajes enviados y recibidos de cada dispositivo.
                <ul>
                    <li><strong>Auto-Scroll:</strong> Desplaza automáticamente hacia el último mensaje</li>
                    <li><strong>Clear:</strong> Limpia todos los mensajes del console</li>
                    <li><strong>Send:</strong> Envía un comando manual al dispositivo (para debug)</li>
                </ul>
            </div>
        </div>
        
        <div class="section" id="control">
            <h2>3. Pestaña de Control ⚙️</h2>
            <p>Aquí gestiona el comportamiento del sistema de oscilación y monitorea los parámetros en tiempo real.</p>
            
            <h3>Parámetros de Control</h3>
            
            <div class="button-desc">
                <strong>RPM (Revoluciones por Minuto)</strong><br>
                Controla la velocidad de rotación del sistema.
                <ul>
                    <li>Ingrese el valor deseado de RPM</li>
                    <li><strong>Enviar:</strong> Aplica el cambio al dispositivo</li>
                    <li><strong>Detener:</strong> Para el movimiento del sistema</li>
                </ul>
            </div>
            
            <div class="button-desc">
                <strong>Kp (Ganancia Proporcional)</strong><br>
                Parámetro del controlador PID que afecta la respuesta del sistema.
                <ul>
                    <li><strong>Enviar:</strong> Aplica el nuevo valor de Kp</li>
                    <li><strong>Por Defecto:</strong> Restaura el valor predeterminado</li>
                </ul>
            </div>
            
            <h3>Mediciones Actuales</h3>
            <p>Muestra en tiempo real los valores de:</p>
            <table>
                <tr>
                    <th>Parámetro</th>
                    <th>Unidad</th>
                    <th>Descripción</th>
                </tr>
                <tr>
                    <td>RPM</td>
                    <td>rpm</td>
                    <td>Velocidad actual de rotación</td>
                </tr>
                <tr>
                    <td>Speed</td>
                    <td>m/s</td>
                    <td>Velocidad lineal del punto de oscilación</td>
                </tr>
                <tr>
                    <td>Acceleration</td>
                    <td>m/s²</td>
                    <td>Aceleración actual</td>
                </tr>
                <tr>
                    <td>Peak Speed</td>
                    <td>m/s</td>
                    <td>Velocidad máxima detectada en la ventana de tiempo</td>
                </tr>
            </table>
            
            <div class="button-desc">
                <strong>Parámetros de Detección de Picos</strong><br>
                Configura cómo el sistema detecta los valores máximos:
                <ul>
                    <li><strong>Peak window:</strong> Ventana de tiempo (segundos) para buscar el máximo</li>
                    <li><strong>Threshold:</strong> Velocidad mínima para considerar un pico válido (m/s)</li>
                    <li><strong>Change:</strong> Aplica los nuevos parámetros de detección</li>
                </ul>
            </div>
            
            <h3>Parámetros del Gráfico</h3>
            
            <div class="button-desc">
                <strong>Rango del Gráfico</strong><br>
                Define el rango de valores a mostrar en los gráficos de velocidad y aceleración.
                Ingrese un valor numérico.
            </div>
            
            <div class="button-desc">
                <strong>Corrección de Signo</strong><br>
                Si está marcado, invierte el signo de los datos para corrección.
            </div>
            
            <div class="button-desc">
                <strong>Mostrar Picos</strong><br>
                Si está marcado, muestra los puntos de máximo en los gráficos.
            </div>
            
            <div class="button-desc">
                <strong>Auto-scroll</strong><br>
                Si está marcado, el gráfico se desplaza automáticamente mostrando los datos más recientes.
            </div>
            
            <div class="button-desc">
                <strong>Clear buffers 🗑️</strong><br>
                Limpia todos los datos acumulados en memoria. Útil para comenzar una nueva sesión.
            </div>
            
            <h3>Exportar Datos</h3>
            
            <div class="button-desc">
                <strong>Seleccione qué datos exportar:</strong><br>
                <ul>
                    <li>✓ RPM - Velocidad angular</li>
                    <li>✓ Speed - Velocidad lineal</li>
                    <li>✓ Corrected Speed - Velocidad corregida</li>
                    <li>✓ Acceleration - Aceleración bruta</li>
                    <li>✓ Corrected Acceleration - Aceleración procesada</li>
                    <li>✓ Raw timestamps - Marcas de tiempo originales</li>
                    <li>✓ Peaks - Valores de picos detectados</li>
                </ul>
            </div>
            
            <div class="button-desc">
                <strong>Carpeta de Guardado</strong><br>
                Seleccione dónde guardar los archivos CSV. El botón "..." abre un selector de carpeta.
            </div>
            
            <div class="button-desc">
                <strong>Nombre personalizado</strong><br>
                Si está marcado, puede especificar un nombre personalizado para el archivo (sin extensión).
                El sistema agregará automáticamente ".csv".
            </div>
            
            <div class="button-desc">
                <strong>Exportar datos 📊</strong><br>
                Guarda los datos seleccionados en un archivo CSV en la carpeta indicada.
            </div>
        </div>
        
        <div class="section" id="imaging">
            <h2>4. Pestaña de Adquisición de Imágenes 📸</h2>
            <p>Permite capturar y gestionar imágenes sincronizadas con los parámetros de oscilación.</p>
            
            <h3>Configuración de Carpeta</h3>
            
            <div class="button-desc">
                <strong>Ruta de Guardado</strong><br>
                Especifica la carpeta donde se guardarán las imágenes.
                El botón "..." abre un selector de carpeta.
            </div>
            
            <div class="button-desc">
                <strong>Agregar Set 📁</strong><br>
                Crea una nueva carpeta de conjunto para organizar imágenes por experimento.
                Se creará una subcarpeta con nombre automático.
            </div>
            
            <div class="button-desc">
                <strong>Eliminar Set Seleccionado 🗑️</strong><br>
                Elimina el conjunto de imágenes seleccionado en la lista.
                <div class="warning">⚠️ <strong>Importante:</strong> Esta acción es irreversible.</div>
            </div>
            
            <h3>Parámetros de Cámara</h3>
            
            <div class="button-desc">
                <strong>Exposure Time (Tiempo de Exposición)</strong><br>
                Duración en segundos que el sensor captura luz.
                Valores típicos: 0.001 - 0.1 segundos.
                <ul>
                    <li>Valores bajos = menos luz, menos movimiento</li>
                    <li>Valores altos = más luz, mayor desenfoque de movimiento</li>
                </ul>
            </div>
            
            <div class="button-desc">
                <strong>Gain (Ganancia)</strong><br>
                Amplificación del sensor en decibelios (dB).
                Rango típico: 0 - 20 dB.
                <ul>
                    <li>Valores altos = más ruidosas pero más claras</li>
                    <li>Valores bajos = menos ruidosas pero más oscuras</li>
                </ul>
            </div>
            
            <h3>Parámetros de Fotografía</h3>
            
            <div class="button-desc">
                <strong>Amplitud</strong><br>
                Seleccione la amplitud de oscilación (11, 13, o 15 mm).
                Determina el rango de movimiento del sistema.
            </div>
            
            <div class="button-desc">
                <strong>RPM</strong><br>
                Velocidad de rotación a la cual tomar las fotos.
                Debe coincidir con el valor configurado en la pestaña de Control.
            </div>
            
            <div class="button-desc">
                <strong>Número de Fotografías</strong><br>
                Cantidad total de imágenes a capturar en esta sesión.
            </div>
            
            <div class="button-desc">
                <strong>Tiempo entre Fotografías</strong><br>
                Intervalo en segundos entre capturas sucesivas.
                Ejemplo: 0.5 segundos = 2 fotos por segundo.
            </div>
            
            <div class="button-desc">
                <strong>Etiqueta de Fotografía ℹ️</strong><br>
                Identificador o descripción para este conjunto de fotos.
                Útil para identificar experimentos o condiciones especiales.
                El botón "?" muestra información sobre el conjunto seleccionado.
            </div>
            
            <h3>Control de Captura</h3>
            
            <div class="button-desc">
                <strong>Comenzar Captura de Fotografías ▶️</strong><br>
                Inicia la adquisición de imágenes con los parámetros especificados.
                <div class="tip">💡 <strong>Consejo:</strong> Asegúrese de que el sistema esté ejecutándose a los RPM deseados antes de iniciar.</div>
            </div>
            
            <div class="button-desc">
                <strong>Detener Captura de Fotografías ⏹️</strong><br>
                Finaliza la captura de imágenes inmediatamente.
            </div>
            
            <h3>Información de Imágenes</h3>
            <p>La sección inferior muestra:</p>
            <ul>
                <li>Lista de conjuntos de imágenes disponibles</li>
                <li>Vista previa de imágenes en el conjunto seleccionado</li>
                <li>Botón para eliminar una imagen específica</li>
            </ul>
        </div>
        
        <div class="section" id="tips">
            <h2>5. Consejos y Solución de Problemas 🔧</h2>
            
            <h3>Problemas de Conexión</h3>
            
            <div class="warning">
                <strong>❌ Puerto COM no aparece:</strong>
                <ol>
                    <li>Verifique que el dispositivo esté conectado correctamente</li>
                    <li>Haga clic en el botón de actualizar (🔄) en la pestaña Connection</li>
                    <li>Intente desconectar y reconectar el dispositivo USB</li>
                    <li>En Windows, verifique en Administrador de dispositivos que el puerto sea reconocido</li>
                </ol>
            </div>
            
            <div class="warning">
                <strong>❌ Conexión falla después de seleccionar puerto:</strong>
                <ol>
                    <li>Verifique la velocidad en baudios (baud rate)</li>
                    <li>Intente otros valores estándar: 9600, 19200, 115200</li>
                    <li>Cierre otros programas que usen el puerto (ej: monitores seriales)</li>
                    <li>Reinicie la aplicación</li>
                </ol>
            </div>
            
            <h3>Problemas con Datos y Gráficos</h3>
            
            <div class="warning">
                <strong>❌ El gráfico está vacío o muestra datos erráticos:</strong>
                <ol>
                    <li>Haga clic en "Clear buffers" para limpiar datos anteriores</li>
                    <li>Verifique que el sistema esté enviando datos en la consola</li>
                    <li>Ajuste el rango del gráfico a un valor apropiado</li>
                    <li>Desactive y reactive la corrección de signo si es necesario</li>
                </ol>
            </div>
            
            <h3>Problemas con Imágenes</h3>
            
            <div class="warning">
                <strong>❌ Las imágenes no se capturan:</strong>
                <ol>
                    <li>Verifique que la cámara está conectada y encendida</li>
                    <li>Compruebe los permisos de carpeta (permisos de escritura)</li>
                    <li>Intente con una carpeta diferente</li>
                    <li>Revise la consola de Control para mensajes de error</li>
                </ol>
            </div>
            
            <div class="warning">
                <strong>❌ Las imágenes están oscuras o desenfocadas:</strong>
                <ol>
                    <li>Aumente el tiempo de exposición (Exposure Time)</li>
                    <li>Aumente la ganancia (Gain) en pequeños incrementos</li>
                    <li>Aumente la iluminación del ambiente</li>
                    <li>Para desenfoque de movimiento, reduzca el tiempo de exposición</li>
                </ol>
            </div>
            
            <h3>Mejores Prácticas</h3>
            
            <div class="tip">
                <strong>✓ Flujo de trabajo recomendado:</strong>
                <ol>
                    <li>Inicie la aplicación</li>
                    <li>Vaya a la pestaña Connection y conecte ambos dispositivos</li>
                    <li>Configure los parámetros de control en la pestaña Control</li>
                    <li>Inicie el sistema (RPM Send)</li>
                    <li>En la pestaña Image Acquisition, configure parámetros de cámara</li>
                    <li>Inicie la captura de imágenes</li>
                    <li>Una vez completado, exporte los datos</li>
                    <li>Desconecte los dispositivos antes de cerrar</li>
                </ol>
            </div>
            
            <div class="tip">
                <strong>✓ Consejos para mejores resultados:</strong>
                <ul>
                    <li>Deje estabilizar el sistema durante unos segundos antes de capturar imágenes</li>
                    <li>Use valores de Kp consistentes para reproducibilidad</li>
                    <li>Mantenga registros de los parámetros de cada experimento</li>
                    <li>Use etiquetas descriptivas para los conjuntos de imágenes</li>
                    <li>Exporte datos regularmente para evitar pérdida de información</li>
                </ul>
            </div>
        </div>
        
        <hr>
        <p style="text-align: center; color: #666;">
            <strong>Manual del Sistema de Control de Oscilaciones</strong><br>
            Última actualización: Febrero 2026
        </p>
        
        </body>
        </html>
        """
        
    def get_english_manual(self):
        """Return the English version of the manual"""
        return """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
                h1 { color: #1f5fa1; border-bottom: 3px solid #1f5fa1; padding-bottom: 10px; }
                h2 { color: #2196F3; margin-top: 30px; }
                h3 { color: #424242; margin-top: 15px; }
                .section { margin-bottom: 30px; }
                .button-desc { background-color: #f5f5f5; padding: 10px; margin: 10px 0; border-left: 4px solid #2196F3; }
                table { border-collapse: collapse; width: 100%; margin: 15px 0; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #2196F3; color: white; }
                .toc { background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .toc ul { list-style-type: none; padding-left: 0; }
                .toc a { color: #1f5fa1; text-decoration: none; font-weight: bold; }
                .toc a:hover { text-decoration: underline; }
                .warning { background-color: #fff3e0; padding: 10px; margin: 10px 0; border-left: 4px solid #ff9800; }
                .tip { background-color: #e8f5e9; padding: 10px; margin: 10px 0; border-left: 4px solid #4caf50; }
            </style>
        </head>
        <body>
        
        <h1>📘 User Manual - Oscillation Control System</h1>
        
        <div class="toc">
            <h3>📑 Table of Contents</h3>
            <ul>
                <li><a href="#intro">1. Introduction</a></li>
                <li><a href="#connection">2. Connection Tab</a></li>
                <li><a href="#control">3. Control Tab</a></li>
                <li><a href="#imaging">4. Image Acquisition Tab</a></li>
                <li><a href="#tips">5. Tips and Troubleshooting</a></li>
            </ul>
        </div>
        
        <div class="section" id="intro">
            <h2>1. Introduction 🚀</h2>
            <p>Welcome to the Oscillation Control System. This application allows you to:</p>
            <ul>
                <li>Connect to control and telemetry devices via Bluetooth or Serial</li>
                <li>Configure and monitor oscillation parameters (RPM, speed, acceleration)</li>
                <li>Acquire and manage images synchronized with oscillation parameters</li>
                <li>Export data for further analysis</li>
            </ul>
            <p>The interface is divided into three main tabs that are described in detail below.</p>
        </div>
        
        <div class="section" id="connection">
            <h2>2. Connection Tab 🔌</h2>
            <p>This is the first tab where you configure connections with the required devices.</p>
            
            <h3>Control Section (Left Side)</h3>
            
            <div class="button-desc">
                <strong>Bluetooth / Serial (Radio Buttons)</strong><br>
                Select the connection type for the control device:
                <ul>
                    <li><strong>Bluetooth:</strong> Wireless connection (currently disabled in current version)</li>
                    <li><strong>Serial (Default):</strong> Connection via COM/Serial port</li>
                </ul>
            </div>
            
            <div class="button-desc">
                <strong>Serial Port (Dropdown + Refresh Button 🔄)</strong><br>
                Select the COM port where your control device is connected.
                The refresh button (reload icon) searches for new available ports.
                <div class="tip">💡 <strong>Tip:</strong> If your port doesn't appear, click the refresh button.</div>
            </div>
            
            <div class="button-desc">
                <strong>Baud Rate</strong><br>
                Select the communication speed. Common values: 9600, 115200, etc.
                <div class="warning">⚠️ <strong>Important:</strong> Make sure it matches your device's configuration.</div>
            </div>
            
            <div class="button-desc">
                <strong>Connect Button 🟢</strong><br>
                Establishes connection with the control device using selected parameters.
                Enabled after selecting a port.
            </div>
            
            <div class="button-desc">
                <strong>Disconnect Button 🔴</strong><br>
                Closes the connection with the control device.
                Only available when a connection is active.
            </div>
            
            <h3>Telemetry Section</h3>
            <p>Similarly to the Control section, here you configure the connection with the telemetry device that sends sensor data.</p>
            
            <h3>Communication Consoles</h3>
            <p>Two secondary tabs show real-time communication:</p>
            <div class="button-desc">
                <strong>Control / Telemetry Console</strong><br>
                Shows messages sent and received from each device.
                <ul>
                    <li><strong>Auto-Scroll:</strong> Automatically scrolls to the latest message</li>
                    <li><strong>Clear:</strong> Clears all console messages</li>
                    <li><strong>Send:</strong> Sends a manual command to the device (for debugging)</li>
                </ul>
            </div>
        </div>
        
        <div class="section" id="control">
            <h2>3. Control Tab ⚙️</h2>
            <p>Here you manage the oscillation system behavior and monitor parameters in real-time.</p>
            
            <h3>Control Parameters</h3>
            
            <div class="button-desc">
                <strong>RPM (Revolutions Per Minute)</strong><br>
                Controls the rotation speed of the system.
                <ul>
                    <li>Enter the desired RPM value</li>
                    <li><strong>Send:</strong> Applies the change to the device</li>
                    <li><strong>Stop:</strong> Stops the system movement</li>
                </ul>
            </div>
            
            <div class="button-desc">
                <strong>Kp (Proportional Gain)</strong><br>
                PID controller parameter that affects system response.
                <ul>
                    <li><strong>Send:</strong> Applies the new Kp value</li>
                    <li><strong>Default:</strong> Restores the default value</li>
                </ul>
            </div>
            
            <h3>Current Measurements</h3>
            <p>Shows real-time values of:</p>
            <table>
                <tr>
                    <th>Parameter</th>
                    <th>Unit</th>
                    <th>Description</th>
                </tr>
                <tr>
                    <td>RPM</td>
                    <td>rpm</td>
                    <td>Current rotation speed</td>
                </tr>
                <tr>
                    <td>Speed</td>
                    <td>m/s</td>
                    <td>Linear velocity of the oscillation point</td>
                </tr>
                <tr>
                    <td>Acceleration</td>
                    <td>m/s²</td>
                    <td>Current acceleration</td>
                </tr>
                <tr>
                    <td>Peak Speed</td>
                    <td>m/s</td>
                    <td>Maximum velocity detected in the time window</td>
                </tr>
            </table>
            
            <div class="button-desc">
                <strong>Peak Detection Parameters</strong><br>
                Configures how the system detects maximum values:
                <ul>
                    <li><strong>Peak window:</strong> Time window (seconds) to search for maximum</li>
                    <li><strong>Threshold:</strong> Minimum speed to consider a valid peak (m/s)</li>
                    <li><strong>Change:</strong> Applies the new detection parameters</li>
                </ul>
            </div>
            
            <h3>Graph Parameters</h3>
            
            <div class="button-desc">
                <strong>Graph Range</strong><br>
                Defines the value range to display in velocity and acceleration graphs.
                Enter a numeric value.
            </div>
            
            <div class="button-desc">
                <strong>Sign Correction</strong><br>
                If checked, inverts the sign of the data for correction.
            </div>
            
            <div class="button-desc">
                <strong>Show Peaks</strong><br>
                If checked, displays maximum points in the graphs.
            </div>
            
            <div class="button-desc">
                <strong>Auto-scroll</strong><br>
                If checked, the graph automatically scrolls showing the most recent data.
            </div>
            
            <div class="button-desc">
                <strong>Clear buffers 🗑️</strong><br>
                Clears all accumulated data in memory. Useful for starting a new session.
            </div>
            
            <h3>Export Data</h3>
            
            <div class="button-desc">
                <strong>Select what data to export:</strong><br>
                <ul>
                    <li>✓ RPM - Angular velocity</li>
                    <li>✓ Speed - Linear velocity</li>
                    <li>✓ Corrected Speed - Corrected velocity</li>
                    <li>✓ Acceleration - Raw acceleration</li>
                    <li>✓ Corrected Acceleration - Processed acceleration</li>
                    <li>✓ Raw timestamps - Original time marks</li>
                    <li>✓ Peaks - Detected peak values</li>
                </ul>
            </div>
            
            <div class="button-desc">
                <strong>Save Path</strong><br>
                Select where to save CSV files. The "..." button opens a folder selector.
            </div>
            
            <div class="button-desc">
                <strong>Custom Filename</strong><br>
                If checked, you can specify a custom filename (without extension).
                The system will automatically add ".csv".
            </div>
            
            <div class="button-desc">
                <strong>Export Data 📊</strong><br>
                Saves selected data to a CSV file in the indicated folder.
            </div>
        </div>
        
        <div class="section" id="imaging">
            <h2>4. Image Acquisition Tab 📸</h2>
            <p>Allows capturing and managing images synchronized with oscillation parameters.</p>
            
            <h3>Folder Configuration</h3>
            
            <div class="button-desc">
                <strong>Save Path</strong><br>
                Specifies the folder where images will be saved.
                The "..." button opens a folder selector.
            </div>
            
            <div class="button-desc">
                <strong>Add Set 📁</strong><br>
                Creates a new set folder to organize images by experiment.
                A subfolder with automatic name will be created.
            </div>
            
            <div class="button-desc">
                <strong>Delete Selected Set 🗑️</strong><br>
                Deletes the selected image set from the list.
                <div class="warning">⚠️ <strong>Important:</strong> This action is irreversible.</div>
            </div>
            
            <h3>Camera Parameters</h3>
            
            <div class="button-desc">
                <strong>Exposure Time</strong><br>
                Duration in seconds that the sensor captures light.
                Typical values: 0.001 - 0.1 seconds.
                <ul>
                    <li>Low values = less light, less motion blur</li>
                    <li>High values = more light, greater motion blur</li>
                </ul>
            </div>
            
            <div class="button-desc">
                <strong>Gain</strong><br>
                Sensor amplification in decibels (dB).
                Typical range: 0 - 20 dB.
                <ul>
                    <li>High values = noisier but brighter</li>
                    <li>Low values = cleaner but darker</li>
                </ul>
            </div>
            
            <h3>Photo Parameters</h3>
            
            <div class="button-desc">
                <strong>Amplitude</strong><br>
                Select oscillation amplitude (11, 13, or 15 mm).
                Determines the range of system movement.
            </div>
            
            <div class="button-desc">
                <strong>RPM</strong><br>
                Rotation speed at which to take photos.
                Should match the value configured in the Control tab.
            </div>
            
            <div class="button-desc">
                <strong>Number of Photos</strong><br>
                Total number of images to capture in this session.
            </div>
            
            <div class="button-desc">
                <strong>Time Between Photos</strong><br>
                Interval in seconds between successive captures.
                Example: 0.5 seconds = 2 photos per second.
            </div>
            
            <div class="button-desc">
                <strong>Photo Label ℹ️</strong><br>
                Identifier or description for this set of photos.
                Useful for identifying experiments or special conditions.
                The "?" button shows information about the selected set.
            </div>
            
            <h3>Capture Control</h3>
            
            <div class="button-desc">
                <strong>Start Taking Photos ▶️</strong><br>
                Starts image acquisition with the specified parameters.
                <div class="tip">💡 <strong>Tip:</strong> Make sure the system is running at the desired RPM before starting.</div>
            </div>
            
            <div class="button-desc">
                <strong>Stop Taking Photos ⏹️</strong><br>
                Stops image capture immediately.
            </div>
            
            <h3>Image Information</h3>
            <p>The bottom section displays:</p>
            <ul>
                <li>List of available image sets</li>
                <li>Preview of images in the selected set</li>
                <li>Button to delete a specific image</li>
            </ul>
        </div>
        
        <div class="section" id="tips">
            <h2>5. Tips and Troubleshooting 🔧</h2>
            
            <h3>Connection Issues</h3>
            
            <div class="warning">
                <strong>❌ COM port does not appear:</strong>
                <ol>
                    <li>Verify that the device is connected correctly</li>
                    <li>Click the refresh button (🔄) in the Connection tab</li>
                    <li>Try disconnecting and reconnecting the USB device</li>
                    <li>On Windows, check Device Manager that the port is recognized</li>
                </ol>
            </div>
            
            <div class="warning">
                <strong>❌ Connection fails after selecting port:</strong>
                <ol>
                    <li>Verify the baud rate</li>
                    <li>Try other standard values: 9600, 19200, 115200</li>
                    <li>Close other programs using the port (e.g., serial monitors)</li>
                    <li>Restart the application</li>
                </ol>
            </div>
            
            <h3>Data and Graph Issues</h3>
            
            <div class="warning">
                <strong>❌ Graph is empty or shows erratic data:</strong>
                <ol>
                    <li>Click "Clear buffers" to clean previous data</li>
                    <li>Verify that the system is sending data in the console</li>
                    <li>Adjust the graph range to an appropriate value</li>
                    <li>Disable and re-enable sign correction if necessary</li>
                </ol>
            </div>
            
            <h3>Image Issues</h3>
            
            <div class="warning">
                <strong>❌ Images are not being captured:</strong>
                <ol>
                    <li>Verify that the camera is connected and powered on</li>
                    <li>Check folder permissions (write permissions)</li>
                    <li>Try with a different folder</li>
                    <li>Review the Control console for error messages</li>
                </ol>
            </div>
            
            <div class="warning">
                <strong>❌ Images are dark or blurry:</strong>
                <ol>
                    <li>Increase the exposure time</li>
                    <li>Increase gain in small increments</li>
                    <li>Increase ambient lighting</li>
                    <li>For motion blur, reduce the exposure time</li>
                </ol>
            </div>
            
            <h3>Best Practices</h3>
            
            <div class="tip">
                <strong>✓ Recommended workflow:</strong>
                <ol>
                    <li>Start the application</li>
                    <li>Go to Connection tab and connect both devices</li>
                    <li>Configure control parameters in Control tab</li>
                    <li>Start the system (RPM Send)</li>
                    <li>In Image Acquisition tab, configure camera parameters</li>
                    <li>Start image capture</li>
                    <li>Once complete, export the data</li>
                    <li>Disconnect devices before closing</li>
                </ol>
            </div>
            
            <div class="tip">
                <strong>✓ Tips for better results:</strong>
                <ul>
                    <li>Allow the system to stabilize for a few seconds before capturing images</li>
                    <li>Use consistent Kp values for reproducibility</li>
                    <li>Keep records of parameters for each experiment</li>
                    <li>Use descriptive labels for image sets</li>
                    <li>Export data regularly to avoid information loss</li>
                </ul>
            </div>
        </div>
        
        <hr>
        <p style="text-align: center; color: #666;">
            <strong>Oscillation Control System Manual</strong><br>
            Last updated: February 2026
        </p>
        
        </body>
        </html>
        """
