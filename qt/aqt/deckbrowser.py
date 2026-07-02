# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from __future__ import annotations

import html
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import aqt
import aqt.operations
from anki.collection import Collection, OpChanges
from anki.decks import DeckCollapseScope, DeckId, DeckTreeNode
from aqt import AnkiQt, gui_hooks
from aqt.deckoptions import display_options_for_deck_id
from aqt.operations import QueryOp
from aqt.operations.deck import (
    add_deck_dialog,
    remove_decks,
    rename_deck,
    reparent_decks,
    set_current_deck,
    set_deck_collapsed,
)
from aqt.qt import *
from aqt.sound import av_player
from aqt.toolbar import BottomBar
from aqt.utils import getOnlyText, openLink, shortcut, showInfo, tooltip, tr


class DeckBrowserBottomBar:
    def __init__(self, deck_browser: DeckBrowser) -> None:
        self.deck_browser = deck_browser


# Speedrun: fallback MCAT topic tags when none are configured.
_DEFAULT_MCAT_TAGS = ["mcat::biobiochem", "mcat::chemphys", "mcat::psychsoc"]


@dataclass
class RenderData:
    """Data from collection that is required to show the page."""

    tree: DeckTreeNode
    current_deck_id: DeckId
    studied_today: str
    sched_upgrade_required: bool
    # Speedrun: the three honest scores + recently-studied decks for the landing.
    memory: Any
    performance: Any
    readiness: Any
    recent: list[tuple[int, str]]
    settings: dict[str, Any]


@dataclass
class DeckBrowserContent:
    """Stores sections of HTML content that the deck browser will be
    populated with.

    Attributes:
        tree {str} -- HTML of the deck tree section
        stats {str} -- HTML of the stats section
        scores {str} -- HTML of the Speedrun scores + recent-decks strip
    """

    tree: str
    stats: str
    scores: str


@dataclass
class RenderDeckNodeContext:
    current_deck_id: DeckId


class DeckBrowser:
    _render_data: RenderData

    def __init__(self, mw: AnkiQt) -> None:
        self.mw = mw
        self.web = mw.web
        self.bottom = BottomBar(mw, mw.bottomWeb)
        self.scrollPos = QPoint(0, 0)
        self._refresh_needed = False
        # Speedrun: which page the (single) main webview is showing.
        # One of: home | library | readiness | settings.
        self._view = "home"

    def set_view(self, view: str) -> None:
        """Switch the main-window view and re-render. Called by the nav rail."""
        self._view = view
        self.mw._highlight_nav(view if view != "library" else "home")
        if self.mw.state == "deckBrowser":
            self.refresh()

    def show(self) -> None:
        av_player.stop_and_clear_queue()
        self.web.set_bridge_command(self._linkHandler, self)
        # redraw top bar for theme change
        self.mw.toolbar.redraw()
        self.refresh()

    def refresh(self) -> None:
        self._renderPage()
        self._refresh_needed = False

    def refresh_if_needed(self) -> None:
        if self._refresh_needed:
            self.refresh()

    def op_executed(
        self, changes: OpChanges, handler: object | None, focused: bool
    ) -> bool:
        if changes.study_queues and handler is not self:
            self._refresh_needed = True

        if focused:
            self.refresh_if_needed()

        return self._refresh_needed

    # Event handlers
    ##########################################################################

    def _linkHandler(self, url: str) -> Any:
        if ":" in url:
            (cmd, arg) = url.split(":", 1)
        else:
            cmd = url
            arg = ""
        if cmd == "open":
            self.set_current_deck(DeckId(int(arg)))
        elif cmd == "study":
            self.set_current_deck(DeckId(int(arg)))
        elif cmd == "view":
            self.set_view(arg)
        elif cmd == "savesettings":
            self._save_settings(arg)
        elif cmd == "advanced":
            self._run_advanced(arg)
        elif cmd == "readiness":
            self.set_view("readiness")
        elif cmd == "opts":
            self._showOptions(arg)
        elif cmd == "shared":
            self._onShared()
        elif cmd == "import":
            self.mw.onImport()
        elif cmd == "create":
            self._on_create()
        elif cmd == "drag":
            source, target = arg.split(",")
            self._handle_drag_and_drop(DeckId(int(source)), DeckId(int(target or 0)))
        elif cmd == "collapse":
            self._collapse(DeckId(int(arg)))
        elif cmd == "v2upgrade":
            self._confirm_upgrade()
        elif cmd == "v2upgradeinfo":
            if self.mw.col.sched_ver() == 1:
                openLink("https://faqs.ankiweb.net/the-anki-2.1-scheduler.html")
            else:
                openLink("https://faqs.ankiweb.net/the-2021-scheduler.html")
        elif cmd == "select":
            set_current_deck(
                parent=self.mw, deck_id=DeckId(int(arg))
            ).run_in_background()
        return False

    def set_current_deck(self, deck_id: DeckId) -> None:
        set_current_deck(parent=self.mw, deck_id=deck_id).success(
            lambda _: self.mw.onOverview()
        ).run_in_background(initiator=self)

    # HTML generation
    ##########################################################################

    # Speedrun: a white/blue app shell applied to every main-window view. Uses
    # explicit colours (not theme vars) per the requested light look.
    _STYLE = """
<style>
:root { --sr-blue:#2563eb; --sr-blue-soft:#eff4ff; --sr-ink:#1e293b;
    --sr-muted:#64748b; --sr-border:#e5e9f0; --sr-bg:#ffffff; }
html, body { background:var(--sr-bg) !important; color:var(--sr-ink) !important; }
#speedrunApp { max-width:1100px; margin:0 auto; padding:1.5em 2em 3em;
    text-align:left; font-size:15px; }
#speedrunApp h1 { font-size:1.6em; margin:0 0 0.15em; color:var(--sr-ink); }
#speedrunApp .lead { color:var(--sr-muted); margin:0 0 1.4em; }
#speedrunApp .section-head { display:flex; align-items:baseline;
    justify-content:space-between; margin:1.6em 0 0.7em; }
#speedrunApp .section-head h2 { font-size:1.15em; margin:0; }
#speedrunApp .section-head a { color:var(--sr-blue); cursor:pointer;
    font-size:0.9em; text-decoration:none; }
#speedrunApp .scorewrap { display:grid;
    grid-template-columns:repeat(3, 1fr); gap:1em; }
#speedrunApp .score { border:1px solid var(--sr-border); border-radius:14px;
    padding:1.2em 1.3em; background:#fff;
    box-shadow:0 1px 3px rgba(15,23,42,0.05); cursor:pointer; }
#speedrunApp .score:hover { border-color:var(--sr-blue); }
#speedrunApp .score .label { color:var(--sr-muted); font-size:0.8em;
    text-transform:uppercase; letter-spacing:0.04em; font-weight:600; }
#speedrunApp .score .big { font-size:2.6em; font-weight:700; line-height:1.1;
    font-variant-numeric:tabular-nums; color:var(--sr-ink); }
#speedrunApp .score .big .unit { font-size:0.35em; color:var(--sr-muted);
    font-weight:500; }
#speedrunApp .score .big.muted { color:var(--sr-muted); font-weight:500;
    font-size:2em; }
#speedrunApp .score .sub { color:var(--sr-muted); font-size:0.85em;
    margin-top:0.2em; }
#speedrunApp .bar { position:relative; height:0.55em; border-radius:999px;
    background:var(--sr-blue-soft); margin-top:0.8em; overflow:hidden; }
#speedrunApp .bar .fill { position:absolute; left:0; top:0; bottom:0;
    background:var(--sr-blue); border-radius:999px; }
#speedrunApp .deckgrid { display:grid;
    grid-template-columns:repeat(auto-fill, minmax(240px, 1fr)); gap:1em; }
#speedrunApp .deck-card { border:1px solid var(--sr-border); border-radius:14px;
    padding:1.1em 1.2em; background:#fff; cursor:pointer;
    box-shadow:0 1px 3px rgba(15,23,42,0.05); transition:border-color .12s; }
#speedrunApp .deck-card:hover { border-color:var(--sr-blue); }
#speedrunApp .deck-card .name { font-weight:600; font-size:1.05em;
    margin-bottom:0.6em; color:var(--sr-ink); }
#speedrunApp .deck-card .counts { display:flex; gap:1.1em; font-size:0.9em; }
#speedrunApp .deck-card .counts .n { font-weight:700;
    font-variant-numeric:tabular-nums; }
#speedrunApp .deck-card .counts .new .n { color:var(--sr-blue); }
#speedrunApp .deck-card .counts .learn .n { color:#dc2626; }
#speedrunApp .deck-card .counts .due .n { color:#16a34a; }
#speedrunApp .deck-card .counts .lbl { color:var(--sr-muted); }
#speedrunApp .deck-card.add { display:flex; align-items:center;
    justify-content:center; color:var(--sr-blue); font-weight:600;
    border-style:dashed; }
#speedrunApp .foot { margin-top:1.4em; color:var(--sr-muted); font-size:0.85em; }
#speedrunApp .chips .chip { display:inline-block; margin:0.15em 0.3em 0.15em 0;
    padding:0.2em 0.8em; border:1px solid var(--sr-border); border-radius:999px;
    cursor:pointer; color:var(--sr-blue); background:#fff; }
#speedrunApp .panel { border:1px solid var(--sr-border); border-radius:14px;
    padding:1.3em 1.5em; background:#fff; margin-bottom:1.2em; }
#speedrunApp .sec-row { display:flex; justify-content:space-between;
    align-items:center; padding:0.55em 0; border-bottom:1px solid var(--sr-border); }
#speedrunApp .sec-row:last-child { border-bottom:none; }
#speedrunApp .sec-row .k { font-weight:600; }
#speedrunApp .badge { padding:0.12em 0.7em; border-radius:999px;
    font-size:0.85em; background:#dc2626; color:#fff; }
#speedrunApp .badge.ok { background:#16a34a; }
#speedrunApp label.opt { display:flex; gap:0.7em; align-items:flex-start;
    padding:0.6em 0; cursor:pointer; }
#speedrunApp label.opt input { margin-top:0.25em; }
#speedrunApp label.opt .desc { color:var(--sr-muted); font-size:0.86em; }
#speedrunApp textarea, #speedrunApp input[type=text] { width:100%;
    border:1px solid var(--sr-border); border-radius:8px; padding:0.5em 0.7em;
    font-family:inherit; color:var(--sr-ink); background:#fff; box-sizing:border-box; }
#speedrunApp .btn { display:inline-block; padding:0.55em 1.4em; border:none;
    border-radius:8px; background:var(--sr-blue); color:#fff; cursor:pointer;
    font-size:1em; }
#speedrunApp .btn.ghost { background:#fff; color:var(--sr-blue);
    border:1px solid var(--sr-border); }
#speedrunApp .adv-links { display:flex; flex-wrap:wrap; gap:0.6em; }
#speedrunApp .saved { color:#16a34a; margin-left:1em; }
</style>
"""

    def _renderPage(self, reuse: bool = False) -> None:
        if not reuse:

            def get_data(col: Collection) -> RenderData:
                from aqt.speedrun_ai.config import get_config

                interleave = col.sched.get_interleave_config()
                tags = list(interleave.topic_tags) or _DEFAULT_MCAT_TAGS
                recent: list[tuple[int, str]] = []
                for did in col.recent_deck_ids(limit=6):
                    name = col.decks.name_if_exists(did)
                    if name:
                        recent.append((int(did), name))
                ai = get_config()
                settings = {
                    "interleave_enabled": interleave.enabled,
                    "weight_by_weakness": interleave.weight_by_weakness,
                    "topic_tags": tags,
                    "production_mode": self.mw.pm.production_mode_enabled(),
                    "type_in_default": self.mw.pm.type_in_default_enabled(),
                    "ai_key": ai.has_key,
                    "ai_model": ai.chat_model,
                    "ai_embed": ai.embed_model,
                }
                return RenderData(
                    tree=col.sched.deck_due_tree(),
                    current_deck_id=col.decks.get_current_id(),
                    studied_today=col.studied_today(),
                    sched_upgrade_required=not col.v3_scheduler(),
                    memory=col.sched.compute_memory_score(search="", topic_tags=tags),
                    performance=col.sched.compute_performance_score(
                        search="", topic_tags=tags
                    ),
                    readiness=col.sched.compute_readiness_score(
                        search="", topic_tags=tags
                    ),
                    recent=recent[:5],
                    settings=settings,
                )

            def success(output: RenderData) -> None:
                self._render_data = output
                self.__renderPage(None)

            QueryOp(
                parent=self.mw,
                op=get_data,
                success=success,
            ).run_in_background()
        else:
            self.web.evalWithCallback("window.pageYOffset", self.__renderPage)

    def __renderPage(self, offset: int | None) -> None:
        renderers = {
            "readiness": self._render_readiness,
            "settings": self._render_settings,
            "library": self._render_library,
        }
        body = renderers.get(self._view, self._render_home)()
        self.web.stdHtml(
            self._STYLE + body,
            css=["css/deckbrowser.css"],
            js=[
                "js/vendor/jquery.min.js",
                "js/vendor/jquery-ui.min.js",
                "js/deckbrowser.js",
            ],
            context=self,
        )
        # The Get-Shared / Create / Import bottom bar only makes sense on the
        # deck-oriented views; hide it on Progress and Settings.
        if self._view in ("home", "library"):
            self._drawButtons()
            self.mw.bottomWeb.show()
        else:
            self.mw.bottomWeb.hide()
        if offset is not None:
            self._scrollToOffset(offset)
        gui_hooks.deck_browser_did_render(self)

    def _scrollToOffset(self, offset: int) -> None:
        self.web.eval("window.scrollTo(0, %d, 'instant');" % offset)

    def _renderStats(self) -> str:
        return '<div id="studiedToday"><span>{}</span></div>'.format(
            self._render_data.studied_today
        )

    # Speedrun: in-window views (home / library / readiness / settings)
    ##########################################################################

    @staticmethod
    def _pct(fraction: float) -> int:
        return round(max(0.0, min(1.0, fraction)) * 100)

    def _bar(self, pct: int) -> str:
        return f'<div class="bar"><div class="fill" style="width:{pct}%"></div></div>'

    def _score_card(self, label: str, score: Any, sub: str) -> str:
        overall = getattr(score, "overall", None)
        if overall and overall.shown and overall.cards_with_state > 0:
            pct = self._pct(overall.estimate)
            big = f'<div class="big">{pct}<span class="unit">%</span></div>'
            bar = self._bar(pct)
        else:
            big = '<div class="big muted">—</div>'
            bar = ""
        return (
            '<div class="score" onclick="pycmd(\'view:readiness\')">'
            f'<div class="label">{label}</div>{big}'
            f'<div class="sub">{sub}</div>{bar}</div>'
        )

    def _readiness_card(self) -> str:
        r = self._render_data.readiness
        if r.shown:
            covered = round(r.coverage * 4)
            big = (
                f'<div class="big">{round(r.scaled_estimate)}'
                '<span class="unit">/528</span></div>'
            )
            sub = f"{covered}/4 sections studied"
            bar = self._bar(self._pct((r.scaled_estimate - 472) / 56))
        else:
            big = '<div class="big muted">—</div>'
            sub = "study more to unlock"
            bar = ""
        return (
            '<div class="score" onclick="pycmd(\'view:readiness\')">'
            f'<div class="label">Readiness</div>{big}'
            f'<div class="sub">{sub}</div>{bar}</div>'
        )

    def _scores_row(self) -> str:
        d = self._render_data
        return (
            '<div class="scorewrap">'
            + self._score_card("Memory", d.memory, "recall right now")
            + self._score_card("Performance", d.performance, "exam-style accuracy")
            + self._readiness_card()
            + "</div>"
        )

    def _deck_counts(self, node: DeckTreeNode) -> tuple[int, int, int]:
        new, learn, rev = node.new_count, node.learn_count, node.review_count
        for child in node.children:
            c_new, c_learn, c_rev = self._deck_counts(child)
            new, learn, rev = new + c_new, learn + c_learn, rev + c_rev
        return new, learn, rev

    def _deck_card(self, node: DeckTreeNode) -> str:
        new, learn, rev = self._deck_counts(node)
        return (
            f'<div class="deck-card" onclick="pycmd(\'study:{node.deck_id}\')">'
            f'<div class="name">{html.escape(node.name)}</div>'
            '<div class="counts">'
            f'<span class="new"><span class="n">{new}</span> <span class="lbl">new</span></span>'
            f'<span class="learn"><span class="n">{learn}</span> <span class="lbl">learn</span></span>'
            f'<span class="due"><span class="n">{rev}</span> <span class="lbl">due</span></span>'
            "</div></div>"
        )

    def _deck_cards(self, nodes: list[DeckTreeNode]) -> str:
        return "".join(self._deck_card(n) for n in nodes)

    def _render_home(self) -> str:
        data = self._render_data
        nodes = list(data.tree.children)
        shown = nodes[:6]
        more = (
            "<a onclick=\"pycmd('view:library')\">See all decks →</a>"
            if len(nodes) > 6
            else ""
        )
        add_card = (
            '<div class="deck-card add" onclick="pycmd(\'create\')">+ New deck</div>'
        )
        content = DeckBrowserContent(
            tree=self._deck_cards(shown),
            stats=self._renderStats(),
            scores=self._scores_row(),
        )
        gui_hooks.deck_browser_will_render_content(self, content)
        recent = ""
        if data.recent:
            chips = "".join(
                f'<span class="chip" onclick="pycmd(\'study:{did}\')">{html.escape(name)}</span>'
                for did, name in data.recent
            )
            recent = f'<div class="foot chips">Recent: {chips}</div>'
        return (
            self._v1_upgrade_message(data.sched_upgrade_required)
            + '<div id="speedrunApp">'
            "<h1>MCAT readiness</h1>"
            '<p class="lead">Your honest scores and where to study next.</p>'
            + content.scores
            + '<div class="section-head"><h2>Your decks</h2>'
            + more
            + "</div>"
            + '<div class="deckgrid">'
            + content.tree
            + add_card
            + "</div>"
            + recent
            + "</div>"
        )

    def _render_library(self) -> str:
        nodes = list(self._render_data.tree.children)
        add_card = (
            '<div class="deck-card add" onclick="pycmd(\'create\')">+ New deck</div>'
        )
        return (
            '<div id="speedrunApp">'
            '<div class="section-head"><h1>Decks</h1>'
            "<a onclick=\"pycmd('view:home')\">← Home</a></div>"
            '<div class="deckgrid">' + self._deck_cards(nodes) + add_card + "</div>"
            "</div>"
        )

    @staticmethod
    def _topic_label(label: str) -> str:
        return (label.split("::")[-1] if label else "").title()

    def _pct_rows(self, response: Any) -> str:
        """Per-topic percentage rows for a memory/performance response."""
        rows = ""
        for topic in response.topics:
            if topic.shown and topic.cards_with_state > 0:
                val = f"{self._pct(topic.estimate)}%"
            else:
                val = '<span style="color:var(--sr-muted)">not enough data</span>'
            rows += (
                f'<div class="sec-row"><span class="k">{self._topic_label(topic.label)}</span>'
                f"<span>{val}</span></div>"
            )
        return rows or '<div class="sec-row"><span>No topics configured.</span></div>'

    def _readiness_rows(self) -> str:
        rows = ""
        for topic in self._render_data.readiness.topics:
            mastery = topic.mastery
            label = self._topic_label(mastery.label if mastery else "")
            if mastery and mastery.shown and mastery.cards_with_state > 0:
                val = (
                    f"{round(topic.scaled_estimate)} "
                    f'<span style="color:var(--sr-muted)">'
                    f"({round(topic.scaled_low)}–{round(topic.scaled_high)})</span>"
                )
            else:
                val = '<span style="color:var(--sr-muted)">not enough data</span>'
            rows += f'<div class="sec-row"><span class="k">{label}</span><span>{val}</span></div>'
        rows += (
            '<div class="sec-row"><span class="k">CARS</span>'
            '<span style="color:var(--sr-muted)">coming with the CARS module</span></div>'
        )
        return rows

    def _render_readiness(self) -> str:
        d = self._render_data
        return (
            '<div id="speedrunApp">'
            '<div class="section-head"><h1>Progress</h1>'
            "<a onclick=\"pycmd('view:home')\">← Home</a></div>"
            '<p class="lead">Your three honest scores, broken down by MCAT '
            "section. Projected total is the sum of the four sections.</p>"
            + self._scores_row()
            + f'<div class="foot">{d.studied_today}</div>'
            + '<div class="section-head"><h2>Readiness by section</h2></div>'
            + f'<div class="panel">{self._readiness_rows()}</div>'
            + '<div class="section-head"><h2>Memory by section</h2></div>'
            + f'<div class="panel">{self._pct_rows(d.memory)}</div>'
            + '<div class="section-head"><h2>Performance by section</h2></div>'
            + f'<div class="panel">{self._pct_rows(d.performance)}</div>'
            + '<div class="section-head"><h2>Detailed history</h2>'
            "<a onclick=\"pycmd('advanced:stats')\">Open graphs →</a></div>" + "</div>"
        )

    def _render_settings(self) -> str:
        s = self._render_data.settings
        tags = "\n".join(s["topic_tags"])
        key_badge = (
            '<span class="badge ok">detected</span>'
            if s["ai_key"]
            else '<span class="badge">not detected</span>'
        )
        checked = lambda b: "checked" if b else ""  # noqa: E731
        int_dis = "" if s["interleave_enabled"] else "disabled"
        prod_dis = "" if s["production_mode"] else "disabled"
        return (
            '<div id="speedrunApp">'
            '<div class="section-head"><h1>Settings</h1>'
            "<a onclick=\"pycmd('view:home')\">← Home</a></div>"
            # Study
            '<div class="panel"><h2>Study</h2>'
            f'<label class="opt"><input type="checkbox" id="sr_int" {checked(s["interleave_enabled"])} '
            "onchange=\"document.getElementById('sr_weak').disabled=!this.checked\">"
            '<span><b>Interleave topics</b><div class="desc">Round-robin cards across your '
            "MCAT topics instead of one at a time.</div></span></label>"
            f'<label class="opt"><input type="checkbox" id="sr_weak" {checked(s["weight_by_weakness"])} {int_dis}>'
            '<span><b>Weight by weakness</b><div class="desc">Show weaker topics more often.</div></span></label>'
            '<label class="opt" style="display:block"><b>Topic tags</b>'
            '<div class="desc">One tag per line.</div>'
            f'<textarea id="sr_tags" rows="3">{html.escape(tags)}</textarea></label></div>'
            # Review
            '<div class="panel"><h2>Review</h2>'
            f'<label class="opt"><input type="checkbox" id="sr_prod" {checked(s["production_mode"])} '
            "onchange=\"document.getElementById('sr_typein').disabled=!this.checked\">"
            '<span><b>Free-text grading</b><div class="desc">Type your answer and have it graded '
            "instead of flipping a flashcard.</div></span></label>"
            f'<label class="opt"><input type="checkbox" id="sr_typein" {checked(s["type_in_default"])} {prod_dis}>'
            '<span><b>Apply to every card</b><div class="desc">Works on any card with a back field '
            "— no Change Notetype needed.</div></span></label></div>"
            # AI
            '<div class="panel"><h2>AI</h2>'
            f'<div class="sec-row"><span class="k">API key</span>{key_badge}</div>'
            f'<div class="sec-row"><span class="k">Chat model</span><span>{html.escape(s["ai_model"])}</span></div>'
            f'<div class="sec-row"><span class="k">Embedding model</span><span>{html.escape(s["ai_embed"])}</span></div>'
            "</div>"
            # Advanced
            '<div class="panel"><h2>Advanced</h2>'
            '<div class="adv-links">'
            '<button class="btn ghost" onclick="pycmd(\'advanced:preferences\')">Preferences</button>'
            '<button class="btn ghost" onclick="pycmd(\'advanced:notetypes\')">Note Types</button>'
            '<button class="btn ghost" onclick="pycmd(\'advanced:import\')">Import</button>'
            '<button class="btn ghost" onclick="pycmd(\'advanced:export\')">Export</button>'
            '<button class="btn ghost" onclick="pycmd(\'advanced:checkdb\')">Check Database</button>'
            '<button class="btn ghost" onclick="pycmd(\'advanced:emptycards\')">Empty Cards</button>'
            "</div></div>"
            # Save
            '<button class="btn" onclick="srSave()">Save</button>'
            "<script>function srSave(){pycmd('savesettings:'+JSON.stringify({"
            "interleave_enabled:document.getElementById('sr_int').checked,"
            "weight_by_weakness:document.getElementById('sr_weak').checked,"
            "production_mode:document.getElementById('sr_prod').checked,"
            "type_in_default:document.getElementById('sr_typein').checked,"
            "topic_tags:document.getElementById('sr_tags').value}));}</script>"
            "</div>"
        )

    def _save_settings(self, raw: str) -> None:
        import json

        try:
            data = json.loads(raw)
        except ValueError:
            return
        self.mw.pm.set_production_mode_enabled(bool(data.get("production_mode")))
        self.mw.pm.set_type_in_default_enabled(bool(data.get("type_in_default")))
        tags = [
            t.strip() for t in str(data.get("topic_tags", "")).split("\n") if t.strip()
        ]
        self.mw.col.sched.set_interleave_config(
            enabled=bool(data.get("interleave_enabled")),
            topic_tags=tags or _DEFAULT_MCAT_TAGS,
            weight_by_weakness=bool(data.get("weight_by_weakness")),
        )
        tooltip("Settings saved", parent=self.mw)
        self.mw.reset()

    def _open_stats(self) -> None:
        aqt.dialogs.open("NewDeckStats", self.mw)

    def _run_advanced(self, action: str) -> None:
        handlers: dict[str, Any] = {
            "preferences": self.mw.onPrefs,
            "notetypes": self.mw.onNoteTypes,
            "import": self.mw.onImport,
            "export": self.mw.onExport,
            "checkdb": self.mw.onCheckDB,
            "emptycards": self.mw.onEmptyCards,
            "stats": self._open_stats,
        }
        handler = handlers.get(action)
        if handler:
            handler()

    def _renderDeckTree(self, top: DeckTreeNode) -> str:
        buf = """
<tr><th colspan=5 align=start>{}</th>
<th class=count>{}</th>
<th class=count>{}</th>
<th class=count>{}</th>
<th class=optscol></th></tr>""".format(
            tr.decks_deck(),
            tr.actions_new(),
            tr.decks_learn_header(),
            tr.decks_review_header(),
        )
        buf += self._topLevelDragRow()

        ctx = RenderDeckNodeContext(current_deck_id=self._render_data.current_deck_id)

        for child in top.children:
            buf += self._render_deck_node(child, ctx)

        return buf

    def _render_deck_node(self, node: DeckTreeNode, ctx: RenderDeckNodeContext) -> str:
        if node.collapsed:
            prefix = "+"
        else:
            prefix = "−"

        def indent() -> str:
            return "&nbsp;" * 6 * (node.level - 1)

        if node.deck_id == ctx.current_deck_id:
            klass = "deck current"
        else:
            klass = "deck"

        buf = (
            "<tr class='%s' id='%d' onclick='if(event.shiftKey) return pycmd(\"select:%d\")'>"
            % (
                klass,
                node.deck_id,
                node.deck_id,
            )
        )
        # deck link
        if node.children:
            collapse = (
                "<a class=collapse href=# onclick='return pycmd(\"collapse:%d\")'>%s</a>"
                % (node.deck_id, prefix)
            )
        else:
            collapse = "<span class=collapse></span>"
        if node.filtered:
            extraclass = "filtered"
        else:
            extraclass = ""
        buf += """

        <td class=decktd colspan=5>%s%s<a class="deck %s"
        href=# onclick="return pycmd('open:%d')">%s</a></td>""" % (
            indent(),
            collapse,
            extraclass,
            node.deck_id,
            html.escape(node.name),
        )

        # due counts
        def nonzeroColour(cnt: int, klass: str) -> str:
            if not cnt:
                klass = "zero-count"
            return f'<span class="{klass}">{cnt}</span>'

        review = nonzeroColour(node.review_count, "review-count")
        learn = nonzeroColour(node.learn_count, "learn-count")

        buf += ("<td align=end>%s</td>" * 3) % (
            nonzeroColour(node.new_count, "new-count"),
            learn,
            review,
        )
        # options
        buf += (
            "<td align=center class=opts><a onclick='return pycmd(\"opts:%d\");'>"
            "<img src='/_anki/imgs/gears.svg' class=gears></a></td></tr>" % node.deck_id
        )
        # children
        if not node.collapsed:
            for child in node.children:
                buf += self._render_deck_node(child, ctx)
        return buf

    def _topLevelDragRow(self) -> str:
        return "<tr class='top-level-drag-row'><td colspan='6'>&nbsp;</td></tr>"

    # Options
    ##########################################################################

    def _showOptions(self, did: str) -> None:
        m = QMenu(self.mw)
        a = m.addAction(tr.actions_rename())
        assert a is not None
        qconnect(a.triggered, lambda b, did=did: self._rename(DeckId(int(did))))
        a = m.addAction(tr.actions_options())
        assert a is not None
        qconnect(a.triggered, lambda b, did=did: self._options(DeckId(int(did))))
        a = m.addAction(tr.actions_export())
        assert a is not None
        qconnect(a.triggered, lambda b, did=did: self._export(DeckId(int(did))))
        a = m.addAction(tr.actions_delete())
        assert a is not None
        qconnect(a.triggered, lambda b, did=did: self._delete(DeckId(int(did))))
        gui_hooks.deck_browser_will_show_options_menu(m, int(did))
        m.popup(QCursor.pos())

    def _export(self, did: DeckId) -> None:
        self.mw.onExport(did=did)

    def _rename(self, did: DeckId) -> None:
        def prompt(name: str) -> None:
            new_name = getOnlyText(
                tr.decks_new_deck_name(), default=name, title=tr.actions_rename()
            )
            if not new_name or new_name == name:
                return
            else:
                rename_deck(
                    parent=self.mw, deck_id=did, new_name=new_name
                ).run_in_background()

        QueryOp(
            parent=self.mw, op=lambda col: col.decks.name(did), success=prompt
        ).run_in_background()

    def _options(self, did: DeckId) -> None:
        display_options_for_deck_id(did)

    def _collapse(self, did: DeckId) -> None:
        node = self.mw.col.decks.find_deck_in_tree(self._render_data.tree, did)
        if node:
            node.collapsed = not node.collapsed
            set_deck_collapsed(
                parent=self.mw,
                deck_id=did,
                collapsed=node.collapsed,
                scope=DeckCollapseScope.REVIEWER,
            ).run_in_background()
            self._renderPage(reuse=True)

    def _handle_drag_and_drop(self, source: DeckId, target: DeckId) -> None:
        reparent_decks(
            parent=self.mw, deck_ids=[source], new_parent=target
        ).run_in_background()

    def _delete(self, did: DeckId) -> None:
        deck = self.mw.col.decks.find_deck_in_tree(self._render_data.tree, did)
        assert deck is not None
        deck_name = deck.name
        remove_decks(
            parent=self.mw, deck_ids=[did], deck_name=deck_name
        ).run_in_background()

    # Top buttons
    ######################################################################

    drawLinks = [
        ["", "shared", tr.decks_get_shared()],
        ["", "create", tr.decks_create_deck()],
        ["Ctrl+Shift+I", "import", tr.decks_import_file()],
    ]

    def _drawButtons(self) -> None:
        buf = ""
        drawLinks = deepcopy(self.drawLinks)
        for b in drawLinks:
            if b[0]:
                b[0] = tr.actions_shortcut_key(val=shortcut(b[0]))
            buf += """
<button title='%s' onclick='pycmd(\"%s\");'>%s</button>""" % tuple(b)
        self.bottom.draw(
            buf=buf,
            link_handler=self._linkHandler,
            web_context=DeckBrowserBottomBar(self),
        )

    def _onShared(self) -> None:
        openLink(f"{aqt.appShared}decks/")

    def _on_create(self) -> None:
        if op := add_deck_dialog(
            parent=self.mw, default_text=self.mw.col.decks.current()["name"]
        ):
            op.run_in_background()

    ######################################################################

    def _v1_upgrade_message(self, required: bool) -> str:
        if not required:
            return ""

        update_required = tr.scheduling_update_required().replace("V2", "v3")

        return f"""
<center>
<div class=callout>
    <div>
      {update_required}
    </div>
    <div>
      <button onclick='pycmd("v2upgrade")'>
        {tr.scheduling_update_button()}
      </button>
      <button onclick='pycmd("v2upgradeinfo")'>
        {tr.scheduling_update_more_info_button()}
      </button>
    </div>
</div>
</center>
"""

    def _confirm_upgrade(self) -> None:
        if self.mw.col.sched_ver() == 1:
            self.mw.col.mod_schema(check=True)
            self.mw.col.upgrade_to_v2_scheduler()
        self.mw.col.set_v3_scheduler(True)

        showInfo(tr.scheduling_update_done())
        self.refresh()
