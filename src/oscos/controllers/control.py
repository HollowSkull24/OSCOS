from pyqtgraph import PlotWidget, mkPen
from core import buffer, SpeedProcessor, AccelerationProcessor, SpeedCorrectedProcessor, SpeedPeakDetection, serial_mgr
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QVBoxLayout, QFileDialog, QMessageBox
import os
import csv
import time

class ControlController:
    def __init__(self, ui):
        self.ui = ui
        serial_mgr.control_rx.connect(self.refresh_rpm_buffer)
        serial_mgr.telemetry_rx.connect(self.refresh_t_buffer)

        # Create a layout inside the widget
        self.layout = QVBoxLayout()
        self.ui.RealTimeGraphWidget.setLayout(self.layout)


        # Dictionary to track active graphs
        self.graphs = {}

        # Connect checkbox signals
        self.ui.SpeedCheckBox.stateChanged.connect(self.update_graph_selection)
        self.ui.RpmCheckBox.stateChanged.connect(self.update_graph_selection)
        self.ui.AccelerationCheckBox.stateChanged.connect(self.update_graph_selection)
        self.ui.AutoScrollGraphCheckBox.stateChanged.connect(self.toggle_graph_range)
        self.ui.CustomExportFilenameCheckBox.stateChanged.connect(self.toggle_export_custom_name)

        # Connect button signals
        self.ui.RPMSendButton.clicked.connect(self.change_rpm)
        self.ui.RPMStopButton.clicked.connect(self.stop_rpm)
        self.ui.ExportButton.clicked.connect(self.export_buffers)
        self.ui.ClearBuffersButton.clicked.connect(self.clear_buffers)
        self.ui.SelectPathButton.clicked.connect(self.select_export_path)
        self.ui.KpSendButton.clicked.connect(self.send_kp)
        self.ui.KpDefaultButton.clicked.connect(self.set_kp_default)
        
        # Create a timer for the graph refresh rate
        self.timer = QTimer()
        self.timer.setInterval(1000 // 60)
        self.timer.timeout.connect(self.refresh_graph)
        self.timer.start()

        # Create data processors:
        self.speed_processor = SpeedProcessor(
            self.ui.toothLengthSpinBox.value(),
            buffer.speed
        )

        self.accel_processor = AccelerationProcessor(buffer.acceleration)

        self.speed_corrected_processor = SpeedCorrectedProcessor(buffer.speed_corrected)
        self.accel_corrected_processor = AccelerationProcessor(buffer.acceleration_corrected)
        # Initialize peak detector using values from the UI spinboxes
        peak_window = float(self.ui.PeakWindowSpinBox.value())
        peak_threshold = float(self.ui.PeakThresholdSpinBox.value())
        self.speed_peak_processor = SpeedPeakDetection(
            buffer.speed_peaks,
            window_seconds=peak_window,
            threshold=peak_threshold,
        )

        # Connect button to update peak detector parameters at runtime
        self.ui.PeakChangeButton.clicked.connect(self.update_peak_params)

        buffer.speed.subscribe(self.accel_processor)
        buffer.speed.subscribe(self.speed_corrected_processor)
        buffer.speed_corrected.subscribe(self.accel_corrected_processor)
        buffer.speed.subscribe(self.speed_peak_processor)

        # Hardcoded info about each graph
        self.signal_registry = {
            "speed": {
                "lcd": self.ui.lcdSpeed,
                "scrollable": True,
            },
            "acceleration": {
                "lcd": self.ui.lcdAcceleration,
                "scrollable": True,
            },
            "rpm": {
                "lcd": self.ui.lcdRPM,
                "scrollable": False,
            },
            "peak": {
                "lcd": self.ui.lcdPeak,
                "scrollable": None,
            },
        }

        # Checkbox map
        self.checkbox_map={
            "speed": self.ui.SpeedCheckBox,
            "acceleration": self.ui.AccelerationCheckBox,
            "rpm": self.ui.RpmCheckBox,
            "peak": self.ui.PeakCheckBox,
        }

        # Steps of the graph scrollbar
        self.scroll_step = 0.1

        # Enable autoscroll on start
        self.ui.AutoScrollGraphCheckBox.setChecked(True)


    def _resolve_buffer(self, name):
        sign_corrected = self.ui.SignCorrectionCheckBox.isChecked()

        if name == "speed":
            return buffer.speed_corrected if sign_corrected else buffer.speed

        if name == "acceleration":
            return (
                buffer.acceleration_corrected
                if sign_corrected
                else buffer.acceleration
            )

        if name == "rpm":
            return buffer.rpm
        if name == "peak":
            return buffer.speed_peaks

    #----------------------------------------
    # Send Kp value
    #----------------------------------------
    def send_kp(self):
        serial_mgr.send_control("k;" + str(self.ui.KpSpinBox.value()))

    def set_kp_default(self):
        self.ui.KpSpinBox.setValue(0.5)
        serial_mgr.send_control("k;" + str(0.5))
    #----------------------------------------
    # Change rpm or stop
    #----------------------------------------
    def change_rpm(self):
        serial_mgr.send_control("r;" + str(self.ui.RPMSpinBox.value()))

    def stop_rpm(self):
        serial_mgr.send_control("r;" + str(0))

    def update_peak_params(self):
        """Update the peak detector parameters from the UI spinboxes."""
        try:
            window = float(self.ui.PeakWindowSpinBox.value())
            threshold = float(self.ui.PeakThresholdSpinBox.value())
        except Exception:
            return

        # Update processor parameters in-place and reset state
        self.speed_peak_processor.window_seconds = window
        self.speed_peak_processor.threshold = threshold
        self.speed_peak_processor.reset()

    #----------------------------------------
    # Refresh graphs based on checkboxes
    #----------------------------------------
    def update_graph_selection(self):
        for name, checkbox in self.checkbox_map.items():
            # The 'peak' checkbox only toggles the overlay on the speed graph;
            # do not create a separate graph for peaks.
            if name == "peak":
                # Ensure speed graph exists if peaks are requested
                if checkbox.isChecked() and "speed" not in self.graphs:
                    cfg = self.signal_registry["speed"]
                    self._add_graph("speed", lcd=cfg["lcd"], scrollable=cfg["scrollable"]) 
                continue

            if checkbox.isChecked() and name not in self.graphs:
                cfg = self.signal_registry[name]
                self._add_graph(
                    name,
                    lcd=cfg["lcd"],
                    scrollable=cfg["scrollable"],
                )

            elif not checkbox.isChecked() and name in self.graphs:
                self._remove_graph(name)

    #--------------------------------------------
    # Add and remove graphs
    #--------------------------------------------
    def _add_graph(self, name, lcd=None, scrollable=True):
        pw = PlotWidget(background="#ffffff")
        pw.plotItem.showGrid(x=True, y=True)
        pw.plotItem.setLabel("bottom", "Time (s)")
        pw.plotItem.setLabel("left", name)
        pw.getAxis("left").setPen("#000000")
        pw.getAxis("bottom").setPen("#000000")
        pw.enableAutoRange(x=False, y=True)

        # Store the curve reference so updating is fast
        curve = pw.plot([], [], pen=mkPen(color=(0, 0, 255), width=2))

        # For speed graph, also create a scatter plot item for peaks (hidden by default)
        peaks_item = None
        if name == "speed":
            peaks_item = pw.plot([], [], pen=None, symbol='o', symbolBrush=(255, 0, 0), symbolSize=8)

        self.graphs[name] = {
            "name": name,
            "widget": pw,
            "curve": curve,
            "peaks_item": peaks_item,
            "lcd": lcd,
            "scrollable": scrollable,
        }

        self.layout.addWidget(pw)

    def _remove_graph(self, name):
        info = self.graphs.pop(name)
        widget = info["widget"]

        self.layout.removeWidget(widget)
        widget.deleteLater()
    
    

    def _get_windowed_data(self, buf, window_size, position=None, autoscroll=False):
        timestamps, values = buf.get_all()
        if len(timestamps) < 2:
            return [], [], None, None

        t_min = timestamps[0]
        t_max = timestamps[-1]
        duration = t_max - t_min

        if window_size <= 0 or window_size >= duration:
            t_start = t_min
        else:
            if autoscroll or position is None:
                t_start = t_max - window_size
            else:
                t_start = t_min + position * self.scroll_step

        t_end = t_start + window_size

        t_out = []
        v_out = []

        prev_t = prev_v = None
        next_t = next_v = None

        for t, v in zip(timestamps, values):
            if t < t_start:
                prev_t, prev_v = t, v
                continue

            if t > t_end:
                next_t, next_v = t, v
                break

            t_out.append(t)
            v_out.append(v)

        # Extend left boundary using real previous value
        if prev_t is not None and t_out and t_out[0] > t_start:
            t_out.insert(0, t_start)
            v_out.insert(0, prev_v)

        # Extend right boundary using real next value
        if next_t is not None and t_out and t_out[-1] < t_end:
            t_out.append(t_end)
            v_out.append(v_out[-1])

        return t_out, v_out, t_start, t_end


    def _update_scrollbar(self, buf, window_size):
        timestamps, _ = buf.get_all()
        if len(timestamps) < 2:
            self.ui.GraphPositionScrollBar.setMaximum(0)
            return

        t_min = timestamps[0]
        t_max = timestamps[-1]
        duration = t_max - t_min

        if window_size <= 0 or window_size >= duration:
            max_pos = 0
        else:
            max_pos = int((duration - window_size) / self.scroll_step)

        self.ui.GraphPositionScrollBar.setMaximum(max_pos)


        
    #--------------------------------------------------
    # Refresh the graph every time the timer emits a signal
    #--------------------------------------------------
   
    def refresh_graph(self):
        window_size = self.ui.GraphRangeSpinBox.value()
        autoscroll = self.ui.AutoScrollGraphCheckBox.isChecked()
        position = self.ui.GraphPositionScrollBar.value()

        # Update scrollbar based on speed buffer (reference timeline)
        self._update_scrollbar(buffer.speed, window_size)

        if autoscroll:
            self.ui.GraphPositionScrollBar.setValue(
                self.ui.GraphPositionScrollBar.maximum()
            )
            position = self.ui.GraphPositionScrollBar.value()

        for info in self.graphs.values():
            buf = self._resolve_buffer(info["name"])
            curve = info["curve"]
            lcd = info["lcd"]
            scrollable = info["scrollable"]

            if scrollable:
                t, v, t_start, t_end = self._get_windowed_data(
                    buf,
                    window_size,
                    position=position,
                    autoscroll=autoscroll
                )
            else:
                # RPM: always show full buffer (normalized)
                info["widget"].enableAutoRange(x=True, y=True)
                timestamps, values = buf.get_latest(2000)
                if len(timestamps) < 2:
                    continue
                t0 = timestamps[0]
                t = [ts - t0 for ts in timestamps]
                v = values

            if not t or not v:
                continue

            curve.setData(t, v)

            if scrollable and t_start is not None and t_end is not None:
                info["widget"].setXRange(t_start, t_end, padding=0)

            # If this is the speed graph and PeakCheckBox is enabled, overlay peaks as scatter
            if info["name"] == "speed":
                peaks_item = info.get("peaks_item")
                if self.ui.PeakCheckBox.isChecked() and peaks_item is not None:
                    # Use the same windowing parameters to fetch peaks
                    t_p, v_p, _, _ = self._get_windowed_data(
                        buffer.speed_peaks,
                        window_size,
                        position=position,
                        autoscroll=autoscroll,
                    )
                    if t_p and v_p:
                        # Align peaks timestamps to the speed buffer timeline.
                        speed_base = getattr(buffer.speed, "_t0", None)
                        peaks_base = getattr(buffer.speed_peaks, "_t0", None)
                        if speed_base is not None and peaks_base is not None:
                            delta = peaks_base - speed_base
                            t_p = [tp + delta for tp in t_p]
                        peaks_item.setData(t_p, v_p)
                    else:
                        peaks_item.setData([], [])
                elif peaks_item is not None:
                    # Clear if checkbox not checked
                    peaks_item.setData([], [])

            if lcd is not None:
                lcd.display(v[-1])

    def toggle_graph_range(self):
        if self.ui.AutoScrollGraphCheckBox.isChecked():
            self.ui.GraphPositionScrollBar.setEnabled(False)
        else:
            self.ui.GraphPositionScrollBar.setEnabled(True)


    #---------------------------------------------------
    # Refresh data buffers on serial read
    #---------------------------------------------------
    def refresh_t_buffer(self, data):
        t_us = float(data)
        t_s = t_us * 1e-6

        buffer.raw_timestamps.add(t_s)
        self.speed_processor.push(t_s)

    def refresh_rpm_buffer(self, data):
        buffer.rpm.add(float(data))

    #--------------------------------------------------
    # Export data as CSV
    #--------------------------------------------------
    def select_export_path(self):
        directory = QFileDialog.getExistingDirectory(
            None,
            "Select export directory"
        )

        if directory:
            self.ui.ExportPathField.setText(directory)

        if not directory:
            return

    def toggle_export_custom_name(self):
        if self.ui.CustomExportFilenameCheckBox.isChecked():
            self.ui.ExportFilenameField.setText("")
            self.ui.ExportFilenameField.setEnabled(True)
        else:
            self.ui.ExportFilenameField.setText("telemetry_Ymd_HMS")
            self.ui.ExportFilenameField.setEnabled(False)

    def export_buffers(self):
        # Select directory
        directory = self.ui.ExportPathField.text()

        if not directory:
            QMessageBox.warning(None, "Warning", "No directory selected.")
            return

        # Create filename from export time
        if self.ui.CustomExportFilenameCheckBox.isChecked():
            filepath = os.path.join(directory, self.ui.ExportFilenameField.text()+".csv")
        else:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(directory, f"telemetry_{timestamp}.csv")


        # Buffers to export based on the checkboxes
        data_info = {
            "raw_timestamp": (self.ui.ExportTimestampsCheckBox, buffer.raw_timestamps),
            "speed": (self.ui.ExportSpeedCheckBox, buffer.speed),
            "acceleration": (self.ui.ExportAccelerationCheckBox, buffer.acceleration),
            "rpm": (self.ui.ExportRPMCheckBox, buffer.rpm),
            "speed_corrected": (self.ui.ExportCorrectedSpeedCheckBox, buffer.speed_corrected),
            "acceleration_corrected": (self.ui.ExportCorrectedAccelerationCheckBox, buffer.acceleration_corrected),
            "speed_peaks": (self.ui.ExportPeaksCheckBox, buffer.speed_peaks),
        }

        # Write CSV
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["signal", "timestamp", "value"])

            for name, info in data_info.items():
                if info[0].isChecked():
                    timestamps, values = info[1].get_all()

                    for t, v in zip(timestamps, values):
                        writer.writerow([name, t, v])

    #-----------------------------------------------
    # Clear data buffers
    #-----------------------------------------------
    def clear_buffers(self):
        # Stop graph refresh briefly (optional but safer)
        self.timer.stop()

        # --- Clear all buffers ---
        buffer.raw_timestamps.clear()
        buffer.speed.clear()
        buffer.acceleration.clear()
        buffer.rpm.clear()
        buffer.speed_corrected.clear()
        buffer.acceleration_corrected.clear()
        buffer.speed_peaks.clear()

        # --- Reset processors (VERY IMPORTANT) ---
        self.speed_processor.reset()
        self.accel_processor.reset()
        self.speed_corrected_processor.reset()
        self.accel_corrected_processor.reset()

        # --- Clear graphs ---
        for info in self.graphs.values():
            info["curve"].clear()
            info["widget"].enableAutoRange(x=True, y=True)

        # --- Reset UI ---
        self.ui.GraphPositionScrollBar.setValue(0)

        # Restart graph refresh
        self.timer.start()

