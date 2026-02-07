
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
import serial

class SerialWorker(QObject):
    data_received = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()
    connected = pyqtSignal(str, int)
    sent_data = pyqtSignal(str)

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.timer = None
        self.rx_buffer = bytearray()
        
    @pyqtSlot()
    def start(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0)
            self.connected.emit(self.port, self.baudrate)
            self.timer = QTimer()
            self.timer.timeout.connect(self.read_serial)
            self.timer.start(10)  # 100 Hz read loop
        except Exception as e:
            self.error.emit(str(e))

    @pyqtSlot()
    def stop(self):
        if self.timer:
            self.timer.stop()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.finished.emit()

    @pyqtSlot()
    def read_serial(self):
        try:
            if self.ser.in_waiting:
                data = self.ser.read(self.ser.in_waiting)
                self.rx_buffer.extend(data)

                while b"\n" in self.rx_buffer:
                    line, _, self.rx_buffer = self.rx_buffer.partition(b"\n")
                    text = line.decode(errors="ignore").strip()
                    self.data_received.emit(text)
        except Exception as e:
            self.error.emit(str(e))

    @pyqtSlot(str)
    def send_text(self, text):
        if self.ser and self.ser.is_open:
            self.ser.write(text.encode("utf-8"))
            self.sent_data.emit(text)

