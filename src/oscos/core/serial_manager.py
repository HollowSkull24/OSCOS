from PyQt5.QtCore import QObject, QThread, pyqtSignal
from workers import SerialWorker

class SerialManager(QObject):
    # Outgoing signals
    control_rx = pyqtSignal(str)
    telemetry_rx = pyqtSignal(str)

    control_sent = pyqtSignal(str)
    telemetry_sent = pyqtSignal(str)

    control_connected = pyqtSignal(str, int)
    control_disconnected = pyqtSignal()

    telemetry_connected = pyqtSignal(str, int)
    telemetry_disconnected = pyqtSignal()

    control_error = pyqtSignal(str)
    telemetry_error = pyqtSignal(str)

    send_control_signal = pyqtSignal(str)
    send_telemetry_signal = pyqtSignal(str)

    shutdown_control = pyqtSignal()
    shutdown_telemetry = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.control_worker = None
        self.control_thread = None
        self.telemetry_worker = None
        self.telemetry_thread = None

    #-------------------------
    # CONTROL
    #-------------------------
    def connect_control(self,port,baud):
        # Create worker and move it to its own thread
        self.control_thread = QThread()
        self.control_worker = SerialWorker(port, baud)
        self.control_worker.moveToThread(self.control_thread)

        self.send_control_signal.connect(self.control_worker.send_text)

        # Connect signals to worker slots
        self.control_thread.started.connect(self.control_worker.start)

        # Succesfully connected/disconnected signals
        self.control_worker.connected.connect(self.control_connected)
        self.control_worker.finished.connect(self.control_thread.quit)

        # Data sent/received succesfully
        self.control_worker.data_received.connect(self.control_rx)
        self.control_worker.sent_data.connect(self.control_sent)

        # Errors
        self.control_worker.error.connect(self.control_error)

        self.shutdown_control.connect(self.control_worker.stop)

        # Start the thread
        self.control_thread.start()


    def disconnect_control(self):
        # Stop the worker
        if self.control_worker is not None:
            self.shutdown_telemetry.emit()

        # Quit the worker's thread
        if self.control_worker is not None:
            self.control_thread.quit()
            self.control_thread.wait()

        self.control_worker = None
        self.control_thread = None
        self.control_disconnected.emit()

    def send_control(self, text):
        self.send_control_signal.emit(text)

    #-------------------------
    # TELEMETRY
    #-------------------------
    def connect_telemetry(self,port,baud):
        # Create worker and move it to its own thread
        self.telemetry_thread = QThread()
        self.telemetry_worker = SerialWorker(port, baud)
        self.telemetry_worker.moveToThread(self.telemetry_thread)

        self.send_telemetry_signal.connect(self.telemetry_worker.send_text)

        # Connect signals to worker slots
        self.telemetry_thread.started.connect(self.telemetry_worker.start)

        # Succesfully connected/disconnected signals
        self.telemetry_worker.connected.connect(self.telemetry_connected)
        self.telemetry_worker.finished.connect(self.telemetry_thread.quit)

        # Data sent/received succesfully
        self.telemetry_worker.data_received.connect(self.telemetry_rx)
        self.telemetry_worker.sent_data.connect(self.telemetry_sent)

        # Errors
        self.telemetry_worker.error.connect(self.telemetry_error)

        self.shutdown_telemetry.connect(self.telemetry_worker.stop)

        # Start the thread
        self.telemetry_thread.start()

    def disconnect_telemetry(self):
        # Stop the worker
        if self.telemetry_worker is not None:
            self.shutdown_telemetry.emit()

        # Quit the worker's thread
        if self.telemetry_worker is not None:
            self.telemetry_thread.quit()
            self.telemetry_thread.wait()

        self.telemetry_worker = None
        self.telemetry_thread = None
        self.telemetry_disconnected.emit()

    def send_telemetry(self, text):
        self.send_telemetry_signal.emit(text)

serial_mgr = SerialManager()
