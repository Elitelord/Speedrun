# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun: a window hosting the honest MCAT readiness dashboard.

The dashboard shows three separate scores — Memory, Performance and Readiness —
each with a range and a give-up rule. It's the Svelte page at
ts/routes/memory-dashboard; this is just a thin Qt shell that loads it.
"""

from __future__ import annotations

import aqt
from aqt.qt import QDialog, Qt, QVBoxLayout
from aqt.utils import disable_help_button, restoreGeom, saveGeom
from aqt.webview import AnkiWebView, AnkiWebViewKind


class MemoryDashboardDialog(QDialog):
    TITLE = "memoryDashboard"

    def __init__(self, mw: aqt.main.AnkiQt) -> None:
        QDialog.__init__(self, mw, Qt.WindowType.Window)
        self.mw = mw
        mw.garbage_collect_on_dialog_finish(self)
        self.setWindowTitle("MCAT Readiness")
        self.setMinimumSize(480, 480)
        disable_help_button(self)
        restoreGeom(self, self.TITLE, default_size=(600, 720))

        self.web = AnkiWebView(kind=AnkiWebViewKind.MEMORY_DASHBOARD)
        self.web.load_sveltekit_page("memory-dashboard")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.web)
        self.setLayout(layout)
        self.show()

    def reject(self) -> None:
        self.web.cleanup()
        self.web = None  # type: ignore[assignment]
        saveGeom(self, self.TITLE)
        QDialog.reject(self)
