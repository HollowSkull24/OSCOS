from serial.tools import list_ports
from PyQt5.QtGui import QTextCursor
from datetime import datetime
from core import serial_mgr

class ConnectionController:
    def __init__(self, ui):
        self.ui = ui

        # Threads and workers
        self.control_thread = None
        self.control_worker = None

        self.telemetry_thread = None
        self.telemetry_worker = None

        # Init GUI elements
        self.populate_ports()
        self.populate_baudrates()

        # Buttons
        self.ui.CSeRefreshButton.clicked.connect(self.populate_ports)
        self.ui.TSeRefreshButton.clicked.connect(self.populate_ports)
        self.ui.CSeConnectButton.clicked.connect(self.control_COM_connect)
        self.ui.TSeConnectButton.clicked.connect(self.telemetry_COM_connect)
        self.ui.CSeDisconnectButton.clicked.connect(self.control_COM_disconnect)
        self.ui.TSeDisconnectButton.clicked.connect(self.telemetry_COM_disconnect)
        self.ui.CConsoleClear.clicked.connect(self.clear_control_console)
        self.ui.TConsoleClear.clicked.connect(self.clear_telemetry_console)
        self.ui.CCBSend.clicked.connect(self.send_control_console)
        self.ui.TCBSend.clicked.connect(self.send_telemetry_console)
        self.ui.CConsoleMessage.returnPressed.connect(self.send_control_console)
        self.ui.TConsoleMessage.returnPressed.connect(self.send_telemetry_console)

        # Serial manager signals
        serial_mgr.control_rx.connect(self.update_control_console)
        serial_mgr.telemetry_rx.connect(self.update_telemetry_console)
        serial_mgr.control_sent.connect(self.update_control_console_sent)
        serial_mgr.telemetry_sent.connect(self.update_telemetry_console_sent)
        serial_mgr.control_connected.connect(self.control_connected)
        serial_mgr.telemetry_connected.connect(self.telemetry_connected)
        serial_mgr.control_disconnected.connect(self.control_disconnected)
        serial_mgr.telemetry_disconnected.connect(self.telemetry_disconnected)
        serial_mgr.control_error.connect(self.control_error)
        serial_mgr.telemetry_error.connect(self.telemetry_error)

    #----------------------
    # GUI INITIALIZATION
    #----------------------
    def populate_ports(self):
        self.ui.CSeComboBox.clear()
        self.ui.TSeComboBox.clear()
        ports = list_ports.comports()
        for port in ports:
            self.ui.CSeComboBox.addItem(port.device)
            self.ui.TSeComboBox.addItem(port.device)

    def populate_baudrates(self):
        baudrates_list = ["300", "1200", "2400", "4800", "9600", "19200",
                          "38400", "57600", "115200", "230400"]
        self.ui.CSeComboBoxBaudRate.addItems(baudrates_list)
        self.ui.TSeComboBoxBaudRate.addItems(baudrates_list)
        self.ui.CSeComboBoxBaudRate.setCurrentIndex(8)
        self.ui.TSeComboBoxBaudRate.setCurrentIndex(8)
    
    #-----------------------------
    # Control connect/disconnect
    #-----------------------------

    def control_COM_connect(self):
        port = self.ui.CSeComboBox.currentText()
        baud = int(self.ui.CSeComboBoxBaudRate.currentText())
        serial_mgr.connect_control(port, baud)

    def control_COM_disconnect(self):
        serial_mgr.disconnect_control()

    def control_connected(self, port, baud):
        self.ui.CConsoleTextBrowser.append(f"<span style='color:#00ff00;'>[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Connected to {port} @ {baud} Bd/s</span>")
        if self.ui.CCBAutoScroll.checkState():
            self.ui.CConsoleTextBrowser.moveCursor(QTextCursor.End)
            self.ui.CConsoleTextBrowser.ensureCursorVisible()

        self.ui.CSeConnectButton.setEnabled(False)
        self.ui.CSeDisconnectButton.setEnabled(True)
        index = self.ui.TSeComboBox.findText(port)
        self.ui.TSeComboBox.removeItem(index)

    def control_disconnected(self):
        self.ui.CConsoleTextBrowser.append(f"<span style='color:#ff0000;'>[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Disconnected control COM port.</span>")
        if self.ui.CCBAutoScroll.checkState():
            self.ui.CConsoleTextBrowser.moveCursor(QTextCursor.End)
            self.ui.CConsoleTextBrowser.ensureCursorVisible()

        self.ui.CSeConnectButton.setEnabled(True)
        self.ui.CSeDisconnectButton.setEnabled(False)

    #-----------------------------
    # Telemetry connect/disconnect
    #-----------------------------

    def telemetry_COM_connect(self):
        port = self.ui.TSeComboBox.currentText()
        baud = int(self.ui.TSeComboBoxBaudRate.currentText())
        serial_mgr.connect_telemetry(port, baud)

    def telemetry_COM_disconnect(self):
        serial_mgr.disconnect_telemetry()

    def telemetry_connected(self, port, baud):
        self.ui.TConsoleTextBrowser.append(f"<span style='color:#00ff00;'>[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Connected to {port} @ {baud} Bd/s</span>")
        if self.ui.TCBAutoScroll.checkState():
            self.ui.TConsoleTextBrowser.moveCursor(QTextCursor.End)
            self.ui.TConsoleTextBrowser.ensureCursorVisible()

        self.ui.TSeConnectButton.setEnabled(False)
        self.ui.TSeDisconnectButton.setEnabled(True)
        index = self.ui.CSeComboBox.findText(port)
        self.ui.CSeComboBox.removeItem(index)


    def telemetry_disconnected(self):
        self.ui.TConsoleTextBrowser.append(f"<span style='color:#ff0000;'>[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Disconnected telemetry COM port.</span>")
        if self.ui.TCBAutoScroll.checkState():
            self.ui.TConsoleTextBrowser.moveCursor(QTextCursor.End)
            self.ui.TConsoleTextBrowser.ensureCursorVisible()

        self.ui.TSeConnectButton.setEnabled(True)
        self.ui.TSeDisconnectButton.setEnabled(False)

    #------------------------------------
    # Update consoles
    #------------------------------------

    def update_control_console(self, text):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.ui.CConsoleTextBrowser.append(f"<span style='color:#ffffff;'>[{timestamp}] {text}</span>")
        if self.ui.CCBAutoScroll.checkState():
            self.ui.CConsoleTextBrowser.moveCursor(QTextCursor.End)
            self.ui.CConsoleTextBrowser.ensureCursorVisible()

    def update_control_console_sent(self, text):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.ui.CConsoleTextBrowser.append(f"<span style='color:#ffff00;'>[{timestamp}][SENT] {text}</span>")
        if self.ui.CCBAutoScroll.checkState():
            self.ui.CConsoleTextBrowser.moveCursor(QTextCursor.End)
            self.ui.CConsoleTextBrowser.ensureCursorVisible()

    def control_error(self, msg):
        self.ui.CConsoleTextBrowser.append(f"<span style='color:#ff0000;'>[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}][ERROR] {msg}</span>")
        self.control_COM_disconnect()

    def clear_control_console(self):
        self.ui.CConsoleTextBrowser.clear()

    def update_telemetry_console(self, text):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.ui.TConsoleTextBrowser.append(f"<span style='color:#ffffff;'>[{timestamp}] {text}</span>")
        if self.ui.TCBAutoScroll.checkState():
            self.ui.TConsoleTextBrowser.moveCursor(QTextCursor.End)
            self.ui.TConsoleTextBrowser.ensureCursorVisible()

    def update_telemetry_console_sent(self, text):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.ui.TConsoleTextBrowser.append(f"<span style='color:#ffff00;'>[{timestamp}][SENT] {text}</span>")
        if self.ui.TCBAutoScroll.checkState():
            self.ui.TConsoleTextBrowser.moveCursor(QTextCursor.End)
            self.ui.TConsoleTextBrowser.ensureCursorVisible()


    def telemetry_error(self, msg):
        self.ui.TConsoleTextBrowser.append(f"<span style='color:#ff0000;'>[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}][ERROR] {msg}</span>")
        self.telemetry_COM_disconnect()

    def clear_telemetry_console(self):
        self.ui.TConsoleTextBrowser.clear()

    #-----------------------------------
    # Send serial messages
    #-----------------------------------
    def send_control_console(self):
        serial_mgr.send_control(self.ui.CConsoleMessage.text())
        self.ui.CConsoleMessage.clear()

    def send_telemetry_console(self):
        serial_mgr.send_telemetry(self.ui.TConsoleMessage.text())
        self.ui.TConsoleMessage.clear()


