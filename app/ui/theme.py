from __future__ import annotations

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication


def apply_light_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f5f5f5"))
    palette.setColor(QPalette.WindowText, QColor("#1f1f1f"))
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#f0f0f0"))
    palette.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipText, QColor("#1f1f1f"))
    palette.setColor(QPalette.Text, QColor("#1f1f1f"))
    palette.setColor(QPalette.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ButtonText, QColor("#1f1f1f"))
    palette.setColor(QPalette.Highlight, QColor("#5b8ef5"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)


def apply_dark_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#121212"))
    palette.setColor(QPalette.WindowText, QColor("#f2f2f2"))
    palette.setColor(QPalette.Base, QColor("#1e1e1e"))
    palette.setColor(QPalette.AlternateBase, QColor("#2b2b2b"))
    palette.setColor(QPalette.ToolTipBase, QColor("#f2f2f2"))
    palette.setColor(QPalette.ToolTipText, QColor("#f2f2f2"))
    palette.setColor(QPalette.Text, QColor("#f2f2f2"))
    palette.setColor(QPalette.Button, QColor("#2a2a2a"))
    palette.setColor(QPalette.ButtonText, QColor("#f2f2f2"))
    palette.setColor(QPalette.Highlight, QColor("#7aa2ff"))
    palette.setColor(QPalette.HighlightedText, QColor("#121212"))
    app.setPalette(palette)
