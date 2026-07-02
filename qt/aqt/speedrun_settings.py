# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun: a window hosting the consolidated MCAT settings page.

The page groups the Speedrun toggles that were previously scattered across the
Tools menu — interleaving, weakness weighting, topic tags, free-text grading,
and AI status — into one place. It's the Svelte route at ts/routes/settings;
this is just a thin Qt shell that loads it.
"""

from __future__ import annotations

import aqt
from aqt.qt import QDialog, Qt, QVBoxLayout
from aqt.utils import disable_help_button, restoreGeom, saveGeom
from aqt.webview import AnkiWebView, AnkiWebViewKind


class SpeedrunSettingsDialog(QDialog):
    TITLE = "speedrunSettings"

    def __init__(self, mw: aqt.main.AnkiQt) -> None:
        QDialog.__init__(self, mw, Qt.WindowType.Window)
        self.mw = mw
        mw.garbage_collect_on_dialog_finish(self)
        self.setWindowTitle("MCAT Settings")
        self.setMinimumSize(480, 480)
        disable_help_button(self)
        restoreGeom(self, self.TITLE, default_size=(600, 680))

        self.web = AnkiWebView(kind=AnkiWebViewKind.SETTINGS)
        self.web.load_sveltekit_page("settings")
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
