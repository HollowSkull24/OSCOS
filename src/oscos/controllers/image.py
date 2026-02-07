from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QFileSystemModel,
)
from PyQt5.QtGui import QPixmap, QIcon, QStandardItemModel, QStandardItem, QDesktopServices
from PyQt5.QtCore import QDir, QSize, Qt, QUrl, QTimer
import os
import shutil
import numpy as np
import cv2
from PIL import Image
from core import take_photo
from PyQt5.QtCore import QSettings
import re
import time
from pathlib import Path
import csv
from core import buffer


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff"}

TAG_DEFINITIONS = {
    # Acquisition
    "amp": "Amplitude (AmplitudeComboBox text)",
    "rpm": "RPM value (RPMPhotoSpinBox)",
    "exposure": "Exposure time in microseconds",
    "exposure_s": "Exposure time in seconds",
    "gain": "Camera gain",

    # Indexing
    "n": "Photo index in current set (1-based)",
    "n0": "Zero-padded photo index (001, 002, ...)",

    # Time
    "year": "Year (YYYY)",
    "month": "Month (MM)",
    "day": "Day (DD)",
    "hour": "Hour (HH)",
    "minute": "Minute (mm)",
    "second": "Second (ss)",
    "timestamp": "YYYYMMDD_HHMMSS",

    # Context
    "set": "Current photo set folder name",
}

class ImageController:
    def __init__(self, ui):
        self.ui = ui
        self.root_dir = None
        self.dir_model = None

        # List model for images
        self.list_model = QStandardItemModel()
        self.ui.PhotoListView.setModel(self.list_model)
        self.ui.PhotoListView.setViewMode(self.ui.PhotoListView.IconMode)
        self.ui.PhotoListView.setIconSize(QSize(128, 128))
        self.ui.PhotoListView.setGridSize(QSize(150, 150))

        self.ui.SelectPhotoPathButton.clicked.connect(self.select_photo_path)
        self.ui.AddSetButton.clicked.connect(self.add_set)
        self.ui.DeleteSetButton.clicked.connect(self.delete_set)
        self.ui.PhotoListView.doubleClicked.connect(self.open_image)
        self.ui.DeletePhotoButton.clicked.connect(self.delete_photo)
        self.ui.StartPhotosButton.clicked.connect(self.start_photos)
        self.ui.PhotolabelInfoButton.clicked.connect(self.show_photo_label_info)
        self.ui.StopPhotosButton.clicked.connect(self.stop_photos)

        self.ui.PhotoLabelField.textChanged.connect(
            lambda text: self.settings.setValue("photo_label_template", text.strip())
        )


        self.ui.PhotoListView.selectionModel().currentChanged.connect(
            self.on_photo_selection_changed
        )

        self._photo_timer = QTimer()
        self._photo_timer.setInterval(5000)
        self._photo_timer.timeout.connect(self._on_photo_timer)
        self._photos_remaining = 0
        self._photo_target_folder = None
        self.settings = QSettings("UTP", "OSCOS")

        last_template = self.settings.value("photo_label_template", "", type=str)
        self.ui.PhotoLabelField.setText(last_template)



        last_path = self.settings.value("image_root_path", "", type=str)
        if last_path and os.path.isdir(last_path):
            self.root_dir = last_path
            self.ui.PhotoPathField.setText(last_path)
            self._load_root_directory(last_path)



    
    def select_photo_path(self):
        start_dir = self.settings.value("image_root_path", "", type=str)

        directory = QFileDialog.getExistingDirectory(
            None,
            "Select photo root directory",
            start_dir if os.path.isdir(start_dir) else ""
        )
        if not directory:
            return

        self.root_dir = directory
        self.ui.PhotoPathField.setText(directory)

        # Save it
        self.settings.setValue("image_root_path", directory)

        self._load_root_directory(directory)

    def on_tree_selection_changed(self, current, previous):
        if not self.dir_model:
            return

        path = self.dir_model.filePath(current)
        if not path:
            return

        self.load_images(path)

    def load_images(self, folder_path):
        """Populate the `PhotoListView` with thumbnails of images inside `folder_path`.
        Non-image files are ignored.
        """
        self.list_model.clear()
        try:
            entries = os.listdir(folder_path)
        except Exception:
            return

        for entry in sorted(entries):
            fp = os.path.join(folder_path, entry)
            if not os.path.isfile(fp):
                continue

            ext = os.path.splitext(entry)[1].lower()
            if ext not in IMAGE_EXTS:
                continue

            pix = QPixmap(fp)
            if pix.isNull():
                continue

            icon = QIcon(pix.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            item = QStandardItem(icon, entry)
            item.setData(fp, Qt.UserRole + 1)
            item.setEditable(False)
            self.list_model.appendRow(item)

        # ensure view parameters
        self.ui.PhotoListView.setViewMode(self.ui.PhotoListView.IconMode)
        self.ui.PhotoListView.setIconSize(QSize(128, 128))
        self.ui.PhotoListView.setGridSize(QSize(150, 150))

    def add_set(self):
        """Create a new subfolder inside the currently selected folder (or root).
        Name is taken from `AddSetField`.
        """
        name = self.ui.AddSetField.text().strip()
        if not name:
            QMessageBox.warning(None, "Warning", "Enter a set name in the AddSet field.")
            return

        sel = self.ui.PhotoSetTreeView.currentIndex()
        target = None
        if sel and sel.isValid():
            target = self.dir_model.filePath(sel)

        if not target:
            target = self.root_dir

        if not target:
            QMessageBox.warning(None, "Warning", "No photo root selected.")
            return

        new_dir = os.path.join(target, name)
        try:
            os.makedirs(new_dir, exist_ok=False)
        except FileExistsError:
            QMessageBox.warning(None, "Warning", "Folder already exists.")
            return
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not create folder: {e}")
            return

        # Refresh QFileSystemModel so the new folder appears
        try:
            self.dir_model.setRootPath(self.root_dir)
            idx = self.dir_model.index(new_dir)
            if idx.isValid():
                self.ui.PhotoSetTreeView.setCurrentIndex(idx)
        except Exception:
            pass


    def delete_photo(self):
        view = self.ui.PhotoListView
        model = self.list_model

        idx = view.currentIndex()
        if not idx.isValid():
            return

        row = idx.row()
        fp = idx.data(Qt.UserRole + 1)
        if not fp:
            return

        
        try:
            os.remove(fp)
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not delete photo: {e}")
            return

        # Remove metadata row
        folder = os.path.dirname(fp)
        filename = os.path.basename(fp)
        self._remove_csv_row(folder, filename)

        # Reload images
        sel = self.ui.PhotoSetTreeView.currentIndex()
        folder = self.dir_model.filePath(sel) if sel and sel.isValid() else self.root_dir
        if not folder:
            return

        self.load_images(folder)

        # Decide which row to select next
        new_count = model.rowCount()
        if new_count == 0:
            return

        # Prefer same row, otherwise previous
        new_row = min(row, new_count - 1)
        new_index = model.index(new_row, 0)

        view.setCurrentIndex(new_index)
        view.scrollTo(new_index)

    def start_photos(self):
        print("Starting photo sequence...")
        # Determine target folder
        sel = self.ui.PhotoSetTreeView.currentIndex()
        target = None
        if sel and sel.isValid():
            target = self.dir_model.filePath(sel)

        if not target:
            target = self.root_dir

        if not target:
            QMessageBox.warning(None, "Warning", "No photo set selected.")
            return

        try:
            n = int(self.ui.NPhotosSpinBox.value())
        except Exception:
            QMessageBox.warning(None, "Warning", "Invalid number of photos.")
            return

        if n <= 0:
            QMessageBox.warning(None, "Warning", "NPhotos must be > 0.")
            return

        self._photos_remaining = n
        self._photo_target_folder = target

        # take first photo immediately
        self._take_and_save_photo()

        # determine interval (spinbox value in seconds) and start timer
        try:
            t_sec = float(self.ui.timeBetweenPhotosSpinBox.value())
            interval_ms = max(10, int(t_sec * 1000))
        except Exception:
            interval_ms = 5000

        self._photo_timer.setInterval(interval_ms)
        if self._photos_remaining > 0:
            self._photo_timer.start()

    def stop_photos(self):
        self._photo_timer.stop()
        self._photos_remaining = 0
        self._photo_target_folder = None

    def _on_photo_timer(self):
        if self._photos_remaining <= 0:
            self._photo_timer.stop()
            return

        # Before taking the photo, allow runtime changes to the interval
        try:
            t_sec = float(self.ui.timeBetweenPhotosSpinBox.value())
            interval_ms = max(10, int(t_sec * 1000))
            # update timer interval for next shot
            if self._photo_timer.interval() != interval_ms:
                self._photo_timer.setInterval(interval_ms)
        except Exception:
            pass

        self._take_and_save_photo()

    
    def _take_and_save_photo(self):
        if not self._photo_target_folder:
            return

        # -------------------------
        # Read acquisition parameters
        # -------------------------
        exposure_s = float(self.ui.ExposureTimeSpinBox.value())
        exposure = int(exposure_s * 1_000_000)  # µs
        gain = float(self.ui.GainSpinBox.value())

        # Photo index (1-based, per set)
        index = (self.ui.NPhotosSpinBox.value() - self._photos_remaining) + 1

        # -------------------------
        # Build filename from template
        # -------------------------
        template = self.ui.PhotoLabelField.text().strip()
        if not template:
            template = "{set}_{n0}_{timestamp}"

        tags = self._build_tag_map(index, self._photo_target_folder)
        base_name = self._expand_filename_template(template, tags)

        out_path = self._safe_output_path(
            self._photo_target_folder,
            base_name,
            ".png"
        )

        # -------------------------
        # Take photo
        # -------------------------
        try:
            print(f"Taking photo {index}, saving to {out_path}...")
            img = take_photo(exposure_us=exposure, gain_db=gain)
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Failed taking photo: {e}")
            self._photo_timer.stop()
            self._photos_remaining = 0
            return

        # -------------------------
        # Validate and save image
        # -------------------------
        try:
            if img is None:
                QMessageBox.warning(None, "Error", "take_photo returned None")
                return

            try:
                info = (
                    f"img dtype={getattr(img, 'dtype', None)} "
                    f"shape={getattr(img, 'shape', None)} "
                    f"min={np.min(img)} max={np.max(img)}"
                )
            except Exception:
                info = f"img type={type(img)}"

            print("[DEBUG]", info)

            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            # Convert to uint8 if needed
            if isinstance(img, np.ndarray):
                if img.dtype != np.uint8:
                    if np.issubdtype(img.dtype, np.floating):
                        m = np.nanmax(img)
                        if m <= 1.0:
                            img2 = (img * 255.0).astype(np.uint8)
                        else:
                            img2 = np.clip(img, 0, 255).astype(np.uint8)
                    else:
                        img2 = np.clip(img, 0, 255).astype(np.uint8)
                else:
                    img2 = img
            else:
                QMessageBox.warning(None, "Error", "Returned image is not an ndarray")
                return

            print(f"Saving photo to {out_path}...")
            # OpenCV uses BGR ordering; Pillow expects RGB. Convert before saving.
            if isinstance(img2, np.ndarray) and img2.ndim == 3 and img2.shape[2] == 3:
                img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img2)
            pil_img.save(out_path)

            # -------------------------
            # Save metadata to CSV
            # -------------------------
            csv_path = self._csv_path_for_set(self._photo_target_folder)
            self._ensure_csv_header(csv_path)

            metadata = self._collect_photo_metadata(
                filename=os.path.basename(out_path),
                index=index,
            )

            self._append_csv_row(csv_path, metadata)
            print("Saved photo using Pillow")

        except Exception as e:
            QMessageBox.warning(None, "Error", f"Failed saving photo: {e}")
            return

        # -------------------------
        # Update UI and counters
        # -------------------------
        self.load_images(self._photo_target_folder)

        self._photos_remaining -= 1
        if self._photos_remaining <= 0:
            self._photo_timer.stop()

    def delete_set(self):
        sel = self.ui.PhotoSetTreeView.currentIndex()
        if not sel or not sel.isValid():
            QMessageBox.warning(None, "Warning", "No set selected to delete.")
            return

        path = self.dir_model.filePath(sel)
        name = os.path.basename(path)

        reply = QMessageBox.question(
            None,
            "Delete set",
            f"Delete set '{name}' and all its contents?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        try:
            shutil.rmtree(path)
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not delete folder: {e}")
            return

        # Refresh model and clear list view
        self.dir_model.setRootPath(self.root_dir)
        parent = sel.parent()
        if parent and parent.isValid():
            self.ui.PhotoSetTreeView.setCurrentIndex(parent)
        else:
            self.ui.PhotoSetTreeView.setRootIndex(self.dir_model.index(self.root_dir))

        self.list_model.clear()

    def open_image(self, index):
        fp = index.data(Qt.UserRole + 1)
        if not fp:
            return

        try:
            os.startfile(fp)
        except AttributeError:
            QDesktopServices.openUrl(QUrl.fromLocalFile(fp))


    def _load_root_directory(self, directory):
        self.dir_model = QFileSystemModel()
        self.dir_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.dir_model.setRootPath(directory)

        self.ui.PhotoSetTreeView.setModel(self.dir_model)
        self.ui.PhotoSetTreeView.setRootIndex(self.dir_model.index(directory))

        for col in range(1, self.dir_model.columnCount()):
            self.ui.PhotoSetTreeView.hideColumn(col)

        self.ui.PhotoSetTreeView.selectionModel().currentChanged.connect(
            self.on_tree_selection_changed
        )

    def _build_tag_map(self, index: int, folder: str) -> dict:
        now = time.localtime()

        exposure_s = float(self.ui.ExposureTimeSpinBox.value())
        exposure_us = int(exposure_s * 1_000_000)

        return {
            # Acquisition
            "amp": self.ui.AmplitudeComboBox.currentText(),
            "rpm": str(self.ui.RPMPhotoSpinBox.value()),
            "exposure": str(exposure_us),
            "exposure_s": f"{exposure_s:.6f}",
            "gain": str(self.ui.GainSpinBox.value()),

            # Indexing
            "n": str(index),
            "n0": f"{index:03d}",

            # Time
            "year": f"{now.tm_year}",
            "month": f"{now.tm_mon:02d}",
            "day": f"{now.tm_mday:02d}",
            "hour": f"{now.tm_hour:02d}",
            "minute": f"{now.tm_min:02d}",
            "second": f"{now.tm_sec:02d}",
            "timestamp": time.strftime("%Y%m%d_%H%M%S", now),

            # Context
            "set": os.path.basename(folder),
        }


    def show_photo_label_info(self):
        lines = []
        lines.append("<b>Photo Labeling System</b><br><br>")
        lines.append("Use tags inside <code>{ }</code> to build photo names.<br>")
        lines.append("Example: <code>{amp}-{rpm}-{n}</code><br><br>")

        lines.append("<b>Available Tags:</b><br>")

        for tag, desc in sorted(TAG_DEFINITIONS.items()):
            lines.append(f"&nbsp;&nbsp;<code>{{{tag}}}</code> — {desc}<br>")

        lines.append("<br><b>Notes:</b><br>")
        lines.append("• If the generated name is not unique, a number is automatically appended.<br>")
        lines.append("• Invalid filename characters are replaced with underscores.<br>")
        lines.append("• Leaving the field empty uses a safe default name.<br>")

        QMessageBox.information(
            None,
            "Photo Labeling Help",
            "".join(lines),
        )

    def _expand_filename_template(self, template: str, tags: dict) -> str:
        def repl(match):
            key = match.group(1)
            return tags.get(key, match.group(0))

        name = re.sub(r"{(\w+)}", repl, template)

        # Sanitize for filesystem
        name = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", name)
        name = name.strip()

        return name if name else "image"


    def _safe_output_path(self, folder: str, base_name: str, ext: str) -> str:
        path = Path(folder) / f"{base_name}{ext}"

        if not path.exists():
            return str(path)

        # Auto-append counter
        i = 1
        while True:
            new_path = Path(folder) / f"{base_name}_{i:03d}{ext}"
            if not new_path.exists():
                return str(new_path)
            i += 1

    def _csv_path_for_set(self, folder: str) -> str:
        return os.path.join(folder, "metadata.csv")

    
    def _ensure_csv_header(self, csv_path: str):
        if os.path.exists(csv_path):
            return

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "filename",
                "timestamp",
                "photo_index",
                "amp",
                "rpm_cmd",
                "rpm_measured",
                "speed_last",
                "accel_last",
                "speed_max",
                "accel_max",
                "kp",
                "tooth_length",
                "exposure_us",
                "gain",
                "set_name",
            ])

    def _collect_photo_metadata(self, filename: str, index: int) -> dict: # Latest values (safe even if empty)
        def last_or_none(buf):
            _, v = buf.get_latest(1)
            return v[0] if v else None

        def max_or_none(buf, window_seconds: float = 1.5):
            # Return the maximum value from the last `window_seconds` seconds
            ts, vals = buf.get_all()
            if not ts or not vals:
                return None

            last_t = ts[-1]
            cutoff = last_t - float(window_seconds)

            recent = [v for t, v in zip(ts, vals) if t >= cutoff]
            if recent:
                return max(recent)
            # fallback to global max if no recent samples
            return max(vals) if vals else None

        return {
            "filename": filename,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "photo_index": index,
            "amp": self.ui.AmplitudeComboBox.currentText(),
            "rpm_cmd": self.ui.RPMPhotoSpinBox.value(),
            "rpm_measured": last_or_none(buffer.rpm),
            "speed_last": last_or_none(buffer.speed),
            "accel_last": last_or_none(buffer.acceleration),
            "speed_max": last_or_none(buffer.speed_peaks),
            "accel_max": max_or_none(buffer.acceleration, 1.5),
            "kp": self.ui.KpSpinBox.value(),
            "tooth_length": self.ui.toothLengthSpinBox.value(),
            "exposure_us": int(self.ui.ExposureTimeSpinBox.value() * 1_000_000),
            "gain": self.ui.GainSpinBox.value(),
            "set_name": os.path.basename(self._photo_target_folder),
        }


    
    def _append_csv_row(self, csv_path: str, data: dict):
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writerow(data)


    def on_photo_selection_changed(self, current, previous):
        if not current or not current.isValid():
            self.ui.PhotoInfoTextBrowser.clear()
            return

        photo_path = current.data(Qt.UserRole + 1)
        if not photo_path:
            self.ui.PhotoInfoTextBrowser.clear()
            return

        folder = os.path.dirname(photo_path)
        filename = os.path.basename(photo_path)

        metadata = self._read_photo_metadata(folder, filename)

        if not metadata:
            self.ui.PhotoInfoTextBrowser.setText(
                f"<b>filename:</b> {filename}<br><br>"
                "<i>No metadata found.</i>"
            )
            return

        self._display_metadata(metadata)


    def _read_photo_metadata(self, folder: str, filename: str) -> dict | None:
        csv_path = os.path.join(folder, "metadata.csv")
        if not os.path.isfile(csv_path):
            return None

        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("filename") == filename:
                        return row
        except Exception as e:
            print(f"[ERROR] Reading metadata CSV: {e}")

        return None


    def _display_metadata(self, metadata: dict):
        lines = []

        for key, value in metadata.items():
            if value is None or value == "":
                continue

            lines.append(
                f"<b>{key}:</b> {value}<br>"
            )

        self.ui.PhotoInfoTextBrowser.setHtml("".join(lines))


    def _remove_csv_row(self, folder: str, filename: str):
        csv_path = os.path.join(folder, "metadata.csv")
        if not os.path.isfile(csv_path):
            return  # No metadata file, nothing to do

        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                fieldnames = reader.fieldnames

            if not fieldnames:
                return

            # Filter out the row matching this filename
            new_rows = [row for row in rows if row.get("filename") != filename]

            # If nothing changed, avoid rewriting
            if len(new_rows) == len(rows):
                return

            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(new_rows)

        except Exception as e:
            print(f"[ERROR] Failed to update metadata CSV: {e}")
