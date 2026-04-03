import json
import os
import re
from PySide6.QtCore import (
    QEvent,
    QPropertyAnimation,
    QEasingCurve,
    QSize,
    Qt,
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMenu,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextBrowser,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QComboBox,
)
from functools import partial
from quest.app.home_page.ui.ui_home_page import Ui_home_page
from quest.app.home_page.front_end import form_apps
from quest.app.home_page.home_back_end import app_manager
import sys
# home_dir = os.path.dirname(__file__)
# base_dir = os.path.join(home_dir, "..", "..")

from quest.paths import get_path
base_dir = get_path()

class gui_connector():
    """
    Connects the front-end GUI with the back-end logic for managing application installation and removal.

    This class handles the interactions between the GUI elements and the back-end processes,
    updating the GUI based on the state of the application installation or removal.
    """
    def __init__(self, front_end, back_end, state):
        """
        Initialize the GUI connector with the front-end, back-end, and state information.

        :param front_end: The front-end GUI elements.
        :type front_end: QWidget
        :param back_end: The back-end logic for managing installation and removal.
        :type back_end: app_manager
        :param state: The environment directory to check for installation status.
        :type state: str
        """
        self.front = front_end
        self.back = back_end
        self.state = state
        self.front.install_button.clicked.connect(self.install_display)
        self.front.progress_bar.setValue(0)
        self.log_dialog = None
        self.log_browser = None
        self._post_uninstall_callback = None
        self.menu = QMenu()
        self.menu.addAction("Uninstall", self.app_removal)
        self.front.setting_button.setMenu(self.menu)
        if self.back.is_app_installed():
            self.front.install_button.setText("Launch")

    def ensure_log_dialog(self):
        """Create the install log dialog the first time it is needed."""
        if self.log_dialog is not None:
            return

        self.log_dialog = QDialog(self.front)
        self.log_dialog.setWindowTitle("App Log")
        self.log_dialog.resize(760, 420)

        layout = QVBoxLayout(self.log_dialog)
        self.log_browser = QTextBrowser(self.log_dialog)
        self.log_browser.setOpenExternalLinks(True)
        layout.addWidget(self.log_browser)

    def append_install_log(self, text):
        """Append process output to the visible install log."""
        self.ensure_log_dialog()
        if text:
            self.log_browser.append(text)

    def show_install_output(self):
        """Ensure the install log window is visible to the user."""
        self.ensure_log_dialog()
        self.log_dialog.show()
        self.log_dialog.raise_()
        self.log_dialog.activateWindow()

    def install_display(self):
        """
        Display the installation progress and update the GUI accordingly.

        This method sets the progress bar to indeterminate, disables the install button,
        and starts the installation process. It updates the button text based on the
        installation status and connects the back-end's finished signal to reset the GUI.
        """
        self.front.progress_bar.setRange(0,0)
        self.front.install_button.setEnabled(False)
        self.back.install()
        self.show_install_output()
        self.log_browser.clear()
        self.append_install_log(f"Starting process: {' '.join(self.back.runner.command)}")
        self.back.runner.signals.output_line.connect(self.append_install_log)
        self.back.runner.signals.result.connect(self.handle_install_result)
        if self.back.is_app_installed():
            self.front.install_button.setText("Running")
        else:
            self.front.install_button.setText("Installing")
        self.back.runner.signals.finished.connect(self.reset_gui)

    def handle_install_result(self, output):
        """Add a final status line once the process completes."""
        if not output.strip():
            self.append_install_log("Process finished with no output.")
        elif not output.endswith("\n"):
            self.append_install_log("")

    def reset_gui(self):
        """
        Reset the GUI elements to their default state after installation or removal.

        This method sets the progress bar to determinate, enables the install button,
        and updates the button text based on the installation status.
        """
        self.front.progress_bar.setRange(0,100)
        self.front.install_button.setEnabled(True)
        self.front.install_button.setChecked(False)
        if self.back.is_app_installed():
            self.front.install_button.setText("Launch")
            self.append_install_log("Installation finished. The app appears to be installed.")
        else:
            self.front.install_button.setText("Install")
            self.append_install_log("Installation finished, but the app is still not detected as installed.")

    def app_removal(self):
        """
        Display the removal progress and update the GUI accordingly.

        This method sets the progress bar to indeterminate, disables the install button,
        and starts the removal process. It updates the button text to 'Uninstalling'
        and connects the back-end's finished signal to reset the GUI.
        """
        self.front.progress_bar.setRange(0,0)
        self.front.install_button.setChecked(True)
        self.front.install_button.setEnabled(False)
        self.front.install_button.setText('Uninstalling')
        self.back.remove_app()
        self.show_install_output()
        self.log_browser.clear()
        self.append_install_log(f"Starting process: {' '.join(self.back.runner.command)}")
        self.back.runner.signals.output_line.connect(self.append_install_log)
        self.back.runner.signals.result.connect(self.handle_uninstall_result)
        self.back.runner.signals.finished.connect(self.reset_gui)

    def handle_uninstall_result(self, output):
        """Add a final status line once the uninstall process completes."""
        if not output.strip():
            self.append_install_log("Process finished with no output.")
        elif not output.endswith("\n"):
            self.append_install_log("")

    def remove_and_deactivate(self, callback):
        """Run uninstall, then invoke callback when the app is no longer detected."""
        self._post_uninstall_callback = callback
        try:
            self.back.runner.signals.finished.disconnect(self._finalize_post_uninstall)
        except Exception:
            pass
        self.back.runner.signals.finished.connect(self._finalize_post_uninstall)
        self.app_removal()

    def _finalize_post_uninstall(self, *_args):
        callback = self._post_uninstall_callback
        self._post_uninstall_callback = None
        try:
            self.back.runner.signals.finished.disconnect(self._finalize_post_uninstall)
        except Exception:
            pass
        if callback is None:
            return
        if self.back.is_app_installed():
            self.append_install_log("Removal finished, but the app still appears to be installed.")
            return
        try:
            callback()
        except Exception:
            pass

class InfoPage(QWidget):
    """
    A page that displays information with a title, contact, and additional info.

    This class sets up a QTextBrowser to display formatted HTML content.
    """
    def __init__(self, title, contact, info):
        """
        Initialize the InfoPage with the given title, contact, and info.

        :param title: The title of the information page.
        :type title: str
        :param contact: The contact information to display.
        :type contact: str
        :param info: The additional information to display.
        :type info: str
        """
        super().__init__()
        self.layout = QVBoxLayout()

        self.text_browser = QTextBrowser()
        # Formatting the info content
        html_content = f"""
        <html>
            <body>
                <h1 style="font-size:26px; font-weight:bold;">{title}</h1>
                <p style="font-size:14px;">{info}</p>
                <p style="font-size:14px; font-weight:bold;">Contact</p>
                <p style="font-size:14px;">{contact}</p>
            </body>
        </html>
        """
        self.text_browser.setHtml(html_content)

        self.layout.addWidget(self.text_browser)
        self.setLayout(self.layout)



class info_drop():
    """
    Manage the dynamic drop-down GUI updates.

    This class handles the creation and management of information pages within a stacked widget,
    and provides methods to connect buttons to these pages.
    """
    def __init__(self, about_info, stacked):
        """
        Initialize the info_drop manager with the given about_info widget and stacked widget.

        :param about_info: The widget containing the about information.
        :type about_info: QWidget
        :param stacked: The stacked widget to manage the information pages.
        :type stacked: QStackedWidget
        """
        self.about_info = about_info
        self.stack = stacked
        self.pages = []

    def add_page(self, title, contact, info):
        """
        Add a new information page to the stacked widget.

        :param title: The title of the information page.
        :type title: str
        :param contact: The contact information to display.
        :type contact: str
        :param info: The additional information to display.
        :type info: str
        :return: The index of the newly added page in the stacked widget.
        :rtype: int
        """
        page = InfoPage(title, contact, info)
        self.pages.append(page)

        index = self.stack.addWidget(page)
        return index



    def connect_about(self, button, page_index):
        """
        Connect a button to navigate to a specific information page.

        :param button: The button to connect.
        :type button: QPushButton
        :param page_index: The index of the page to navigate to.
        :type page_index: int
        """
        button.clicked.connect(partial(self.about_page_drop, page_index))

    def clear_pages(self):
        """Remove dynamically-added info pages so the grid can be rebuilt safely."""
        for page in self.pages:
            try:
                self.stack.removeWidget(page)
            except Exception:
                pass
            page.deleteLater()
        self.pages = []

    def about_page_drop(self, page_index):
        """
        Navigate to the information page and animate the drop-down effect.

        :param page_index: The index of the page to navigate to.
        :type page_index: int
        """

        height = self.about_info.height()
        if height == 0:
                newheight = 450
        else:
                newheight = 450
        self.stack.setCurrentIndex(page_index)
        self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
        self.animation.setDuration(250)
        self.animation.setStartValue(height)
        self.animation.setEndValue(newheight)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()


class AddAppDialog(QDialog):
    """Dialog for creating a new app card entry in app_cards.json."""

    def __init__(self, existing_apps, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New App")
        self.resize(720, 560)
        self._existing_apps = existing_apps
        self._created_app = None
        self._inactive_apps = [app for app in self._existing_apps if not bool(app.get("active", True))]

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.restore_combo = QComboBox()
        self.restore_combo.addItem("Select inactive app...", "")
        for app in self._inactive_apps:
            app_id = str(app.get("id", "")).strip()
            title = str(app.get("title", app_id)).strip() or app_id
            self.restore_combo.addItem(title, app_id)
        self.restore_button = QPushButton("Restore Selected")
        self.restore_button.setEnabled(len(self._inactive_apps) > 0)

        self.app_id_input = QLineEdit()
        self.title_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.info_input = QPlainTextEdit()
        self.info_input.setMinimumHeight(100)
        self.image_input = QLineEdit()
        self.env_input = QLineEdit()
        self.script_input = QLineEdit()
        self.env_delete_input = QLineEdit()
        self.solve_input = QLineEdit()
        self.launch_type_input = QComboBox()
        self.launch_type_input.addItems(["module", "path", "exe"])
        self.launch_value_input = QLineEdit()
        self.image_browse_button = QPushButton("Browse")
        self.script_browse_button = QPushButton("Browse")

        self.image_input.setPlaceholderText("images/logo/my_app_logo.png")
        self.env_input.setPlaceholderText("app_envs/env_my_app")
        self.script_input.setPlaceholderText("app/tools/script_files/my_app.bat")
        self.env_delete_input.setPlaceholderText("app_envs/env_my_app")
        self.solve_input.setPlaceholderText("Optional")
        self.launch_value_input.setPlaceholderText("module name or relative path")
        self.env_input.setReadOnly(True)
        self.env_delete_input.setReadOnly(True)

        image_row = QWidget()
        image_layout = QHBoxLayout(image_row)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.addWidget(self.image_input)
        image_layout.addWidget(self.image_browse_button)

        script_row = QWidget()
        script_layout = QHBoxLayout(script_row)
        script_layout.setContentsMargins(0, 0, 0, 0)
        script_layout.addWidget(self.script_input)
        script_layout.addWidget(self.script_browse_button)

        restore_row = QWidget()
        restore_layout = QHBoxLayout(restore_row)
        restore_layout.setContentsMargins(0, 0, 0, 0)
        restore_layout.addWidget(self.restore_combo)
        restore_layout.addWidget(self.restore_button)

        form.addRow("Restore App", restore_row)
        form.addRow("App ID", self.app_id_input)
        form.addRow("Title", self.title_input)
        form.addRow("Contact", self.contact_input)
        form.addRow("Info", self.info_input)
        form.addRow("Image Path", image_row)
        form.addRow("Env Path", self.env_input)
        form.addRow("Install Script", script_row)
        form.addRow("Env Delete Path", self.env_delete_input)
        form.addRow("Solver Path", self.solve_input)
        form.addRow("Launch Type", self.launch_type_input)
        form.addRow("Launch Value", self.launch_value_input)

        layout.addLayout(form)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.app_id_input.textChanged.connect(self._sync_generated_paths)
        self.image_browse_button.clicked.connect(self._browse_image)
        self.script_browse_button.clicked.connect(self._browse_script)
        self.restore_button.clicked.connect(self._restore_selected_inactive_app)
        self._result_action = "create"
        self._target_existing_id = None

    def created_app(self):
        return self._created_app

    def result_action(self):
        return self._result_action

    def target_existing_id(self):
        return self._target_existing_id

    def _restore_selected_inactive_app(self):
        selected_id = str(self.restore_combo.currentData() or "").strip()
        if not selected_id:
            QMessageBox.information(self, "Restore App", "Select an inactive app card to restore.")
            return
        self._result_action = "reactivate"
        self._target_existing_id = selected_id
        self._created_app = None
        super().accept()

    def _sanitize_identifier(self, raw_value):
        sanitized = []
        for ch in (raw_value or "").strip().lower():
            if ch.isalnum():
                sanitized.append(ch)
            else:
                sanitized.append("_")
        value = "".join(sanitized).strip("_")
        while "__" in value:
            value = value.replace("__", "_")
        return value

    def _environment_component(self):
        app_id = self._sanitize_identifier(self.app_id_input.text())
        if not app_id:
            return ""
        return f"env_{app_id}"

    def _sync_generated_paths(self):
        env_component = self._environment_component()
        env_relpath = f"app_envs/{env_component}" if env_component else ""
        self.env_input.setText(env_relpath)
        self.env_delete_input.setText(env_relpath)

    def _browse_relative_file(self, start_rel_dir, file_filter):
        start_dir = os.path.join(base_dir, start_rel_dir)
        selected_path, _ = QFileDialog.getOpenFileName(self, "Select File", start_dir, file_filter)
        if not selected_path:
            return ""
        return os.path.relpath(selected_path, base_dir).replace("\\", "/")

    def _browse_image(self):
        relpath = self._browse_relative_file("images/logo", "Images (*.png *.jpg *.jpeg *.svg *.bmp *.gif);;All Files (*)")
        if relpath:
            self.image_input.setText(relpath)

    def _browse_script(self):
        relpath = self._browse_relative_file("app/tools/script_files", "Batch Files (*.bat *.cmd);;All Files (*)")
        if relpath:
            self.script_input.setText(relpath)

    def _validate_script_environment(self, script_relpath, env_relpath):
        if not script_relpath or not env_relpath:
            return []
        script_abs = os.path.join(base_dir, script_relpath)
        try:
            with open(script_abs, "r", encoding="utf-8", errors="ignore") as script_file:
                script_text = script_file.read()
        except Exception:
            return []

        env_names = set(re.findall(r"env_[A-Za-z0-9_]+", script_text))
        if not env_names:
            return []

        expected_env_name = os.path.basename(env_relpath.replace("\\", "/"))
        if expected_env_name in env_names:
            return []

        if len(env_names) == 1:
            hardcoded_env = sorted(env_names)[0]
            return [
                f"Install Script appears to be hardcoded for '{hardcoded_env}', but this app card expects '{expected_env_name}'."
            ]

        return [
            f"Install Script references multiple environment names ({', '.join(sorted(env_names))}). Please use a script dedicated to this app."
        ]

    def _validate_existing_constraints(self, app_id, title="", image_relpath="", env_relpath="", script_relpath="", launch_type="", launch_value=""):
        connector_attr = f"{app_id}_obj"
        search_key = app_id
        existing_ids = {str(app.get("id", "")).strip(): app for app in self._existing_apps if str(app.get("id", "")).strip()}
        existing_connectors = {str(app.get("connector_attr", "")).strip(): app for app in self._existing_apps if str(app.get("connector_attr", "")).strip()}
        existing_search_keys = {str(app.get("search_key", "")).strip(): app for app in self._existing_apps if str(app.get("search_key", "")).strip()}
        existing_titles = {str(app.get("title", "")).strip().lower(): app for app in self._existing_apps if str(app.get("title", "")).strip()}
        existing_images = {str(app.get("image_relpath", "")).strip(): app for app in self._existing_apps if str(app.get("image_relpath", "")).strip()}
        existing_envs = {
            str(app.get("env_relpath", "")).strip(): app
            for app in self._existing_apps
            if str(app.get("env_relpath", "")).strip()
        }
        existing_scripts = {
            str(app.get("script_relpath", "")).strip(): app
            for app in self._existing_apps
            if str(app.get("script_relpath", "")).strip()
        }

        existing_launch_targets = {}
        for app in self._existing_apps:
            launch = app.get("launch", {})
            if not isinstance(launch, dict):
                continue
            if "type" in launch:
                launch_configs = [launch]
            else:
                launch_configs = [cfg for cfg in launch.values() if isinstance(cfg, dict)]
            for launch_cfg in launch_configs:
                launch_key = (
                    str(launch_cfg.get("type", "")).strip(),
                    str(launch_cfg.get("value", launch_cfg.get("value_relpath", ""))).strip(),
                )
                if launch_key[0] and launch_key[1]:
                    existing_launch_targets[launch_key] = app

        errors = []
        inactive_duplicates = []

        def register_duplicate(app, message):
            if bool(app.get("active", True)):
                errors.append(message)
            else:
                inactive_duplicates.append(app)

        if app_id in existing_ids:
            register_duplicate(existing_ids[app_id], f"An app with id '{app_id}' already exists.")
        if connector_attr in existing_connectors:
            register_duplicate(existing_connectors[connector_attr], f"The generated connector '{connector_attr}' already exists.")
        if search_key in existing_search_keys:
            register_duplicate(existing_search_keys[search_key], f"The generated search key '{search_key}' already exists.")
        lowered_title = title.strip().lower()
        if lowered_title and lowered_title in existing_titles:
            register_duplicate(existing_titles[lowered_title], f"An app with title '{title.strip()}' already exists.")
        if image_relpath and image_relpath in existing_images:
            register_duplicate(existing_images[image_relpath], f"The image path '{image_relpath}' is already used by another app card.")
        if env_relpath and env_relpath in existing_envs:
            register_duplicate(existing_envs[env_relpath], f"The environment path '{env_relpath}' is already used by another app card.")
        if script_relpath and script_relpath in existing_scripts:
            register_duplicate(existing_scripts[script_relpath], f"The install script '{script_relpath}' is already used by another app card.")
        launch_key = (launch_type.strip(), launch_value.strip())
        if launch_key[0] and launch_key[1] and launch_key in existing_launch_targets:
            register_duplicate(existing_launch_targets[launch_key], f"The launch target '{launch_value.strip()}' ({launch_type.strip()}) is already used by another app card.")

        deduped_inactive = []
        seen_ids = set()
        for app in inactive_duplicates:
            app_key = str(app.get("id", "")).strip()
            if app_key and app_key not in seen_ids:
                deduped_inactive.append(app)
                seen_ids.add(app_key)
        return connector_attr, search_key, errors, deduped_inactive

    def _show_errors(self, errors):
        QMessageBox.warning(self, "Invalid App Card", "\n".join(errors))

    def _resolve_inactive_duplicate(self, duplicate_app):
        title = str(duplicate_app.get("title", duplicate_app.get("id", "this app"))).strip() or "this app"
        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Question)
        message_box.setWindowTitle("Inactive App Exists")
        message_box.setText(f"An inactive app card matching '{title}' already exists.")
        message_box.setInformativeText("Do you want to overwrite it with the new details, or just turn the old card back to active?")
        overwrite_button = message_box.addButton("Overwrite", QMessageBox.AcceptRole)
        reactivate_button = message_box.addButton("Reactivate Old", QMessageBox.YesRole)
        cancel_button = message_box.addButton(QMessageBox.Cancel)
        message_box.exec()
        clicked_button = message_box.clickedButton()
        if clicked_button == overwrite_button:
            return "overwrite"
        if clicked_button == reactivate_button:
            return "reactivate"
        return "cancel"

    def accept(self):
        app_id = self._sanitize_identifier(self.app_id_input.text())
        if app_id:
            self.app_id_input.setText(app_id)

        errors = []
        if not app_id:
            errors.append("App ID is required and must contain letters or numbers.")

        title = self.title_input.text().strip()
        contact = self.contact_input.text().strip()
        info = self.info_input.toPlainText().strip()
        image_relpath = self.image_input.text().strip()
        env_relpath = self.env_input.text().strip()
        script_relpath = self.script_input.text().strip()
        env_delete_relpath = self.env_delete_input.text().strip()
        solve_relpath = self.solve_input.text().strip()
        launch_type = self.launch_type_input.currentText().strip()
        launch_value = self.launch_value_input.text().strip()

        if not title:
            errors.append("Title is required.")
        if not contact:
            errors.append("Contact is required.")
        if not info:
            errors.append("Info is required.")
        if not image_relpath:
            errors.append("Image Path is required.")
        if not env_relpath:
            errors.append("Env Path is required.")
        if not script_relpath:
            errors.append("Install Script is required.")
        if not env_delete_relpath:
            errors.append("Env Delete Path is required.")
        if not launch_value:
            errors.append("Launch Value is required.")

        connector_attr, search_key, uniqueness_errors, inactive_duplicates = self._validate_existing_constraints(
            app_id,
            title=title,
            image_relpath=image_relpath,
            env_relpath=env_relpath,
            script_relpath=script_relpath,
            launch_type=launch_type,
            launch_value=launch_value,
        )
        errors.extend(uniqueness_errors)

        if env_relpath and not os.path.basename(env_relpath).startswith("env_"):
            errors.append("Env Path must begin with 'env_' in the final folder name.")

        image_abs = os.path.join(base_dir, image_relpath) if image_relpath else ""
        script_abs = os.path.join(base_dir, script_relpath) if script_relpath else ""
        if image_relpath and not os.path.exists(image_abs):
            errors.append(f"Image Path does not exist: {image_relpath}")
        if script_relpath and not os.path.exists(script_abs):
            errors.append(f"Install Script does not exist: {script_relpath}")
        errors.extend(self._validate_script_environment(script_relpath, env_relpath))

        if errors:
            self._show_errors(errors)
            return

        if inactive_duplicates:
            if len(inactive_duplicates) > 1:
                self._show_errors(["More than one inactive app card matches this new app. Please remove the duplicates manually before adding this app."])
                return
            duplicate_app = inactive_duplicates[0]
            resolution = self._resolve_inactive_duplicate(duplicate_app)
            if resolution == "cancel":
                return
            self._target_existing_id = str(duplicate_app.get("id", "")).strip()
            if resolution == "reactivate":
                self._result_action = "reactivate"
                self._created_app = None
                super().accept()
                return
            self._result_action = "overwrite"
        else:
            self._result_action = "create"
            self._target_existing_id = None

        if launch_type == "module":
            launch = {
                "type": "module",
                "value": launch_value,
            }
        elif launch_type == "exe":
            launch = {
                "type": "exe",
                "value_relpath": launch_value,
            }
        else:
            launch = {
                "type": "path",
                "value_relpath": launch_value,
            }

        self._created_app = {
            "id": app_id,
            "connector_attr": connector_attr,
            "search_key": search_key,
            "title": title,
            "contact": contact,
            "info": info,
            "image_relpath": image_relpath,
            "env_relpath": env_relpath,
            "script_relpath": script_relpath,
            "env_delete_relpath": env_delete_relpath,
            "launch": launch,
            "grid_position": [0, 0],
            "active": True,
        }
        if solve_relpath:
            self._created_app["solve_relpath"] = solve_relpath

        super().accept()


class home_page(QWidget, Ui_home_page):
    """
    The landing screen.

    Initialize the install manager class.
    Initialize the app removal class.
    Initialize the info drop downs.
    Update state based on files at launch
    """

    def _app_cards_file_path(self):
        return os.path.join(os.path.dirname(__file__), "app_cards.json")

    def _sanitize_identifier(self, raw_value):
        sanitized = []
        for ch in (raw_value or "").strip().lower():
            if ch.isalnum():
                sanitized.append(ch)
            else:
                sanitized.append("_")
        value = "".join(sanitized).strip("_")
        while "__" in value:
            value = value.replace("__", "_")
        return value

    def _load_app_card_data(self):
        with open(self._app_cards_file_path(), "r", encoding="utf-8") as app_cards_file:
            return json.load(app_cards_file)

    def _save_app_card_data(self, data):
        with open(self._app_cards_file_path(), "w", encoding="utf-8") as app_cards_file:
            json.dump(data, app_cards_file, indent=2)
            app_cards_file.write("\n")

    def _normalize_grid_positions(self, app_data):
        active_apps = [app for app in app_data.get("apps", []) if bool(app.get("active", True))]
        active_apps.sort(key=lambda app: tuple(app.get("grid_position", [9999, 9999])))
        columns = 4
        for index, app in enumerate(active_apps):
            app["grid_position"] = [index // columns, index % columns]
        return app_data

    def _resolve_card_path(self, relpath):
        if not relpath:
            return None
        if os.path.isabs(relpath):
            return relpath
        return os.path.join(base_dir, relpath)

    def _resolve_launch(self, app_definition, default_mod):
        launch = app_definition.get("launch", {})
        if not isinstance(launch, dict):
            raise ValueError(f"Invalid launch configuration for app '{app_definition.get('id', '')}'.")

        if "type" in launch:
            launch_config = launch
        elif sys.platform.startswith("win") and isinstance(launch.get("windows"), dict):
            launch_config = launch["windows"]
        else:
            launch_config = launch.get("default", {})

        launch_type = launch_config.get("type")
        launch_mod = launch_config.get("mod", default_mod if launch_type == "module" else None)

        if launch_type == "module":
            return launch_config.get("value", ""), launch_mod
        if launch_type in {"path", "exe"}:
            launch_value = self._resolve_card_path(launch_config.get("value_relpath") or launch_config.get("value"))
            if launch_type == "exe" and launch_mod is None:
                launch_mod = "exe"
            return launch_value, launch_mod

        raise ValueError(f"Unsupported launch type '{launch_type}' for app '{app_definition.get('id', '')}'.")

    def _load_app_card_configs(self, del_path, mod):
        data = self._load_app_card_data()
        configs = []
        for app_definition in data.get("apps", []):
            if not app_definition.get("active", True):
                continue

            env_cmd, resolved_mod = self._resolve_launch(app_definition, mod)
            config = {
                "app_id": app_definition["id"],
                "connector_attr": app_definition["connector_attr"],
                "search_key": app_definition["search_key"],
                "title": app_definition["title"],
                "contact": app_definition["contact"],
                "info": app_definition["info"],
                "image": self._resolve_card_path(app_definition.get("image_relpath") or app_definition.get("image")),
                "env_path": self._resolve_card_path(app_definition.get("env_relpath") or app_definition.get("env_path")),
                "env_cmd": env_cmd,
                "script_path": self._resolve_card_path(app_definition.get("script_relpath") or app_definition.get("script_path")),
                "env_delete": self._resolve_card_path(app_definition.get("env_delete_relpath") or app_definition.get("env_delete")),
                "solve_path": self._resolve_card_path(app_definition.get("solve_relpath") or app_definition.get("solve_path")),
                "mod": resolved_mod,
                "grid_position": tuple(app_definition["grid_position"]),
            }
            configs.append(config)
        return configs

    def _set_app_active(self, app_id, active):
        app_data = self._load_app_card_data()
        found = False
        for app in app_data.get("apps", []):
            if str(app.get("id", "")).strip() == str(app_id).strip():
                app["active"] = bool(active)
                found = True
                break
        if not found:
            raise ValueError(f"Unable to find app id '{app_id}' in app_cards.json.")
        app_data = self._normalize_grid_positions(app_data)
        self._save_app_card_data(app_data)

    def _replace_existing_app_card(self, app_id, new_app):
        app_data = self._load_app_card_data()
        found = False
        for index, app in enumerate(app_data.get("apps", [])):
            if str(app.get("id", "")).strip() == str(app_id).strip():
                replacement = dict(new_app)
                replacement["grid_position"] = app.get("grid_position", new_app.get("grid_position", [0, 0]))
                app_data["apps"][index] = replacement
                found = True
                break
        if not found:
            raise ValueError(f"Unable to find inactive app id '{app_id}' to overwrite.")
        app_data = self._normalize_grid_positions(app_data)
        self._save_app_card_data(app_data)

    def _remove_app_card(self, app_id, connector, title):
        answer = QMessageBox.question(
            self,
            "Remove App",
            f"Are you sure you want to remove '{title}' from the app hub?\n\nThis will uninstall the app and hide its card.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        def finalize_removal():
            try:
                self._set_app_active(app_id, False)
                self._refresh_home_cards()
                QMessageBox.information(self, "App Removed", f"'{title}' was removed from the app hub.")
            except Exception as exc:
                QMessageBox.critical(self, "Remove App Error", f"The app hub could not be updated.\n\nDetails: {exc}")

        if connector.back.is_app_installed():
            connector.remove_and_deactivate(finalize_removal)
        else:
            finalize_removal()

    def _next_grid_position(self, app_definitions):
        used_positions = {
            tuple(app.get("grid_position", []))
            for app in app_definitions
            if bool(app.get("active", True))
            and isinstance(app.get("grid_position", None), list)
            and len(app.get("grid_position", [])) == 2
        }
        columns = 4
        index = 0
        while True:
            candidate = (index // columns, index % columns)
            if candidate not in used_positions:
                return list(candidate)
            index += 1

    def _clear_grid_layout(self):
        while self.gridLayout.count():
            item = self.gridLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _build_add_app_card(self):
        front = form_apps()
        front.install_button.setText("Add App")
        front.progress_bar.hide()
        front.about_button.hide()
        front.setting_button.hide()
        front.app_image.setStyleSheet("background-color: #f8fafc; border: 2px dashed #94a3b8; border-radius: 10px;")

        front.install_button.clicked.connect(self._open_add_app_dialog)
        self._add_app_click_targets.update({front.app_search, front.app_image})
        for widget in self._add_app_click_targets:
            try:
                widget.installEventFilter(self)
            except Exception:
                pass
        return front

    def _refresh_home_cards(self):
        self._clear_grid_layout()
        self.search_widgets = {}
        self._add_app_click_targets = set()
        self.add_info_page.clear_pages()

        del_path = os.path.join(base_dir, "app", "tools", "env_delete", "delete_env.py")
        mod = '-m'
        for app_config in self._load_app_card_configs(del_path, mod):
            self.search_widgets[app_config["search_key"]] = self._build_app_card(app_config, del_path)

        add_app_front = self._build_add_app_card()
        next_row, next_column = self._next_grid_position(self._load_app_card_data().get("apps", []))
        self.gridLayout.addWidget(add_app_front, next_row, next_column)

    def _open_add_app_dialog(self):
        try:
            app_data = self._load_app_card_data()
        except Exception as exc:
            QMessageBox.critical(self, "App Cards Error", f"Unable to read app_cards.json.\n\nDetails: {exc}")
            return

        dialog = AddAppDialog(app_data.get("apps", []), self)
        if dialog.exec() != QDialog.Accepted:
            return

        result_action = dialog.result_action()
        target_existing_id = dialog.target_existing_id()
        new_app = dialog.created_app()
        if result_action == "reactivate":
            if not target_existing_id:
                QMessageBox.critical(self, "App Cards Error", "Unable to determine which inactive app should be reactivated.")
                return
            try:
                self._set_app_active(target_existing_id, True)
                self._refresh_home_cards()
                QMessageBox.information(self, "App Reactivated", f"'{target_existing_id}' was turned back to active.")
            except Exception as exc:
                QMessageBox.critical(self, "App Cards Error", f"Unable to reactivate the existing app card.\n\nDetails: {exc}")
            return

        if not new_app:
            return

        try:
            if result_action == "overwrite":
                if not target_existing_id:
                    raise ValueError("No inactive app id was selected for overwrite.")
                self._replace_existing_app_card(target_existing_id, new_app)
            else:
                app_data.setdefault("apps", [])
                new_app["grid_position"] = self._next_grid_position(app_data["apps"])
                app_data["apps"].append(new_app)
                app_data = self._normalize_grid_positions(app_data)
                self._save_app_card_data(app_data)
        except Exception as exc:
            QMessageBox.critical(self, "App Cards Error", f"Unable to save app_cards.json.\n\nDetails: {exc}")
            return

        try:
            self._refresh_home_cards()
        except Exception as exc:
            QMessageBox.critical(self, "Home Refresh Error", f"The app was saved, but the home page could not refresh.\n\nDetails: {exc}")
            return

        QMessageBox.information(self, "App Added", f"'{new_app['title']}' was added successfully.")

    def _build_app_card(self, config, del_path):
        """Create, connect, and place a single app card."""
        front = form_apps()
        image_path = config["image"].replace("\\", "/")
        front.app_image.setStyleSheet(f"image: url({image_path});")
        remove_button = QPushButton(front.app_search)
        remove_button.setFixedSize(24, 24)
        remove_icon = QIcon()
        remove_icon.addFile(u":/icon/images/icons/close_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        remove_button.setIcon(remove_icon)
        remove_button.setIconSize(QSize(20, 20))
        remove_button.setFlat(True)
        remove_button.setStyleSheet(
            "QPushButton {"
            "background: transparent;"
            "border: none;"
            "padding: 0px;"
            "}"
            "QPushButton:hover {"
            "background-color: #c42b1c;"
            "}"
        )
        remove_button.move(max(front.app_search.width() - 30, 0), 6)
        remove_button.raise_()
        remove_button.show()

        env_path = config["env_path"]
        env_act = os.path.join(env_path, "Scripts", "python.exe")
        back = app_manager(
            env_path,
            env_act,
            config["env_cmd"],
            config["script_path"],
            del_path,
            config["env_delete"],
            config.get("solve_path"),
            config.get("mod"),
        )
        connector = gui_connector(front, back, env_path)
        setattr(self, config["connector_attr"], connector)
        remove_button.clicked.connect(
            lambda _checked=False, app_id=config["app_id"], app_connector=connector, title=config["title"]:
            self._remove_app_card(app_id, app_connector, title)
        )

        page_index = self.add_info_page.add_page(
            config["title"],
            config["contact"],
            config["info"],
        )
        self.add_info_page.connect_about(front.about_button, page_index)
        row, column = config["grid_position"]
        self.gridLayout.addWidget(front, row, column)
        return front.app_search

    def __init__(self):
        """Initialize the home page."""
        super().__init__()
#           Set up the ui
        self.setupUi(self)
#           gui objects for the about page class
        about = self.about_info
        stacked = self.stackedWidget_2
#       path to deletion tool
        del_path = os.path.join(base_dir, "app", "tools", "env_delete", "delete_env.py")
#       package entry point identifier
        mod = '-m'

#       declare info page

        self.add_info_page = info_drop(about, stacked)
        self.search_widgets = {}
        self._add_app_click_targets = set()
        self._refresh_home_cards()
##      place holder formats
        # #Planning app place holder
        # self.plan_front = form_apps()
        # self.plan_front.progress_bar.setValue(0)
        # self.plan_front.setting_button.setEnabled(False)
        # self.plan_front.install_button.setEnabled(False)
        # self.plan_front.install_button.setText("Upcoming")
        # plan_image = os.path.join(base_dir, "images", "logo", "Quest_Planning_Logo_RGB.png")
        # plan_image = plan_image.replace("\\", "/")
        # self.plan_front.app_image.setStyleSheet(f"image: url({plan_image});")

        # plan_about_button = self.plan_front.about_button
        # plan_page = self.add_info_page.add_page("QuESt Planning", "", "This app is still in development and will be released to the QuESt platform soon.")
        # self.add_info_page.connect_about(plan_about_button, plan_page)

        # self.gridLayout.addWidget(self.plan_front, 2, 0)



#           connecting the search bar funtion

        self.lineEdit.setPlaceholderText("Search apps")
        self.lineEdit.textChanged.connect(self.update_display)

#       hide the about window
        self.about_hide.clicked.connect(self.about_hide_window_btn)

    def about_hide_window_btn(self):
         """Button to minimize the about drop down page on the homescreen."""
         height = self.about_info.height()

         if height == 0:
            newheight = 450

         else:
           newheight = 0

         self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
         self.animation.setDuration(250)
         self.animation.setStartValue(height)
         self.animation.setEndValue(newheight)
         self.animation.setEasingCurve(QEasingCurve.InOutQuart)
         self.animation.start()

    def update_display(self, text,):
        """Dynamic update of visible apps."""
        search_text = text.lower()
        for widget_name, widget in self.search_widgets.items():
            widget.setVisible(search_text in widget_name.lower())

    def eventFilter(self, obj, event):
        try:
            if obj in getattr(self, "_add_app_click_targets", set()) and event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                self._open_add_app_dialog()
                return True
        except Exception:
            pass
        return super().eventFilter(obj, event)

if __name__ == '__main__':
    home_page()
