"""Password generator dialog for SecureVault Pro."""

import math

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.services.password_service import PasswordService


class PasswordGeneratorDialog(QDialog):
    """Dialog for generating strong passwords with configurable options."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Password Generator")
        self.setMinimumWidth(520)
        self.setModal(True)
        self._generated = ""
        self._mode = "random"  # "random" or "passphrase"
        self._build_ui()
        self._generate()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Generate Secure Password")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #64B4FF;")
        layout.addWidget(title)

        pw_row = QHBoxLayout()
        self._pw_display = QLineEdit()
        self._pw_display.setReadOnly(True)
        self._pw_display.setFont(QFont("Consolas", 14))
        self._pw_display.setStyleSheet(
            "QLineEdit { background: #16162a; border: 1px solid #2a2a4a; border-radius: 6px; "
            "padding: 10px 12px; color: #e0e0e0; }"
        )
        pw_row.addWidget(self._pw_display)

        copy_btn = QPushButton("Copy")
        copy_btn.setFixedWidth(60)
        copy_btn.setStyleSheet(
            "QPushButton { background: #3B82F6; color: white; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: #2563EB; }"
        )
        copy_btn.clicked.connect(self._copy_password)
        pw_row.addWidget(copy_btn)
        layout.addLayout(pw_row)

        self._strength_bar = QLabel("Strength: ---")
        self._strength_bar.setStyleSheet("color: #aaa; font-size: 12px; padding: 2px 0;")
        layout.addWidget(self._strength_bar)

        mode_row = QHBoxLayout()
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("color: #ccc;")
        mode_row.addWidget(mode_label)

        self._mode_random = QRadioButton("Random Characters")
        self._mode_random.setChecked(True)
        self._mode_random.setStyleSheet("QRadioButton { color: #ccc; spacing: 6px; }")
        self._mode_passphrase = QRadioButton("Passphrase")
        self._mode_passphrase.setStyleSheet("QRadioButton { color: #ccc; spacing: 6px; }")

        mode_group = QButtonGroup(self)
        mode_group.addButton(self._mode_random, 0)
        mode_group.addButton(self._mode_passphrase, 1)
        mode_group.idClicked.connect(self._on_mode_changed)
        mode_row.addWidget(self._mode_random)
        mode_row.addWidget(self._mode_passphrase)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        self._random_options = QWidget()
        self._build_random_options(self._random_options)
        layout.addWidget(self._random_options)

        self._passphrase_options = QWidget()
        self._build_passphrase_options(self._passphrase_options)
        self._passphrase_options.setVisible(False)
        layout.addWidget(self._passphrase_options)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        gen_btn = QPushButton("Generate")
        gen_btn.setStyleSheet(
            "QPushButton { background: #10B981; color: white; border: none; border-radius: 6px; padding: 8px 20px; font-weight: bold; }"
            "QPushButton:hover { background: #059669; }"
        )
        gen_btn.clicked.connect(self._generate)
        btn_row.addWidget(gen_btn)

        use_btn = QPushButton("Use This Password")
        use_btn.setStyleSheet(
            "QPushButton { background: #64B4FF; color: #1a1a2e; border: none; border-radius: 6px; padding: 8px 20px; font-weight: bold; }"
            "QPushButton:hover { background: #4A9AE6; }"
        )
        use_btn.clicked.connect(self.accept)
        btn_row.addWidget(use_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            "QPushButton { background: #333; color: #ccc; border: none; border-radius: 6px; padding: 8px 16px; }"
            "QPushButton:hover { background: #444; }"
        )
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        layout.addLayout(btn_row)

    def _build_random_options(self, parent: QWidget) -> None:
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        len_row = QHBoxLayout()
        len_label = QLabel("Length:")
        len_label.setStyleSheet("color: #ccc;")
        len_row.addWidget(len_label)

        self._length_slider = QSlider(Qt.Orientation.Horizontal)
        self._length_slider.setRange(8, 128)
        self._length_slider.setValue(20)
        self._length_slider.setStyleSheet(
            "QSlider::groove:horizontal { background: #2a2a4a; height: 6px; border-radius: 3px; }"
            "QSlider::handle:horizontal { background: #64B4FF; width: 16px; margin: -5px 0; border-radius: 8px; }"
        )
        self._length_slider.valueChanged.connect(self._on_length_changed)
        len_row.addWidget(self._length_slider, 1)

        self._length_display = QLabel("20")
        self._length_display.setFixedWidth(30)
        self._length_display.setStyleSheet("color: #e0e0e0;")
        len_row.addWidget(self._length_display)
        layout.addLayout(len_row)

        options_label = QLabel("Character Sets:")
        options_label.setStyleSheet("color: #ccc; margin-top: 8px;")
        layout.addWidget(options_label)

        opts_layout = QHBoxLayout()
        self._upper_cb = QCheckBox("Uppercase (A-Z)")
        self._upper_cb.setChecked(True)
        self._lower_cb = QCheckBox("Lowercase (a-z)")
        self._lower_cb.setChecked(True)
        self._digits_cb = QCheckBox("Digits (0-9)")
        self._digits_cb.setChecked(True)
        self._symbols_cb = QCheckBox("Symbols (!@#$)")
        self._symbols_cb.setChecked(True)

        for cb in (self._upper_cb, self._lower_cb, self._digits_cb, self._symbols_cb):
            cb.setStyleSheet("QCheckBox { color: #ccc; spacing: 6px; }")
            opts_layout.addWidget(cb)
        layout.addLayout(opts_layout)

    def _build_passphrase_options(self, parent: QWidget) -> None:
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        word_row = QHBoxLayout()
        word_label = QLabel("Word count:")
        word_label.setStyleSheet("color: #ccc;")
        word_row.addWidget(word_label)

        self._word_slider = QSlider(Qt.Orientation.Horizontal)
        self._word_slider.setRange(3, 8)
        self._word_slider.setValue(4)
        self._word_slider.setStyleSheet(
            "QSlider::groove:horizontal { background: #2a2a4a; height: 6px; border-radius: 3px; }"
            "QSlider::handle:horizontal { background: #64B4FF; width: 16px; margin: -5px 0; border-radius: 8px; }"
        )
        self._word_slider.valueChanged.connect(self._on_word_count_changed)
        word_row.addWidget(self._word_slider, 1)

        self._word_display = QLabel("4")
        self._word_display.setFixedWidth(20)
        self._word_display.setStyleSheet("color: #e0e0e0;")
        word_row.addWidget(self._word_display)
        layout.addLayout(word_row)

        sep_row = QHBoxLayout()
        sep_label = QLabel("Separator:")
        sep_label.setStyleSheet("color: #ccc;")
        sep_row.addWidget(sep_label)

        self._separator_combo = QComboBox()
        self._separator_combo.addItems(["Hyphen (-)", "Space ( )", "Dot (.)"])
        self._separator_combo.setFixedWidth(130)
        self._separator_combo.setStyleSheet(
            "QComboBox { background: #16162a; border: 1px solid #2a2a4a; border-radius: 4px; color: #e0e0e0; padding: 4px 8px; }"
        )
        sep_row.addWidget(self._separator_combo)
        sep_row.addStretch()
        layout.addLayout(sep_row)

        self._capitalize_cb = QCheckBox("Capitalize words")
        self._capitalize_cb.setChecked(True)
        self._capitalize_cb.setStyleSheet("QCheckBox { color: #ccc; spacing: 6px; }")
        layout.addWidget(self._capitalize_cb)

    def _on_mode_changed(self, mode_id: int) -> None:
        self._mode = "passphrase" if mode_id == 1 else "random"
        self._random_options.setVisible(self._mode == "random")
        self._passphrase_options.setVisible(self._mode == "passphrase")
        self._generate()

    def _on_length_changed(self, val: int) -> None:
        self._length_display.setText(str(val))

    def _on_word_count_changed(self, val: int) -> None:
        self._word_display.setText(str(val))

    def _generate(self) -> None:
        if self._mode == "passphrase":
            sep_map = {"Hyphen (-)": "-", "Space ( )": " ", "Dot (.)": "."}
            sep_text = self._separator_combo.currentText()
            separator = sep_map.get(sep_text, "-")
            self._generated = PasswordService.generate_passphrase(
                num_words=self._word_slider.value(),
                separator=separator,
                capitalize=self._capitalize_cb.isChecked(),
            )
        else:
            self._generated = PasswordService.generate_password(
                length=self._length_slider.value(),
                use_uppercase=self._upper_cb.isChecked(),
                use_lowercase=self._lower_cb.isChecked(),
                use_digits=self._digits_cb.isChecked(),
                use_symbols=self._symbols_cb.isChecked(),
            )
        self._pw_display.setText(self._generated)
        self._update_strength()

    def _update_strength(self) -> None:
        if self._mode == "passphrase":
            word_count = self._word_slider.value()
            entropy = round(word_count * math.log2(2048), 1)
            if entropy < 60:
                label, color = "Weak", "#EF4444"
            elif entropy < 80:
                label, color = "Fair", "#F59E0B"
            elif entropy < 100:
                label, color = "Good", "#3B82F6"
            else:
                label, color = "Strong", "#10B981"
            self._strength_bar.setText(f"Strength: {label}  |  Entropy: {entropy} bits")
            self._strength_bar.setStyleSheet(f"color: {color}; font-size: 12px; padding: 2px 0;")
        else:
            strength = PasswordService.calculate_strength(self._generated)
            label = strength["label"]
            color_map = {"Weak": "#EF4444", "Fair": "#F59E0B", "Good": "#3B82F6", "Strong": "#10B981"}
            color = color_map.get(label, "#aaa")
            self._strength_bar.setText(f"Strength: {label}  |  Entropy: {strength['entropy']} bits")
            self._strength_bar.setStyleSheet(f"color: {color}; font-size: 12px; padding: 2px 0;")

    def _copy_password(self) -> None:
        from app.security.clipboard_manager import ClipboardManager

        ClipboardManager().copy_secret(self._generated)

    def get_password(self) -> str:
        return self._generated
