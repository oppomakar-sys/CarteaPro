# -*- coding: utf-8 -*-
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar

# ---------------------------------------------
# FUNDAL GENERAL – modul DARK
# ---------------------------------------------
Window.clearcolor = (0.05, 0.05, 0.05, 1)

# ---------------------------------------------
# CONȚINUTUL CĂRȚII – PAGINI
# ---------------------------------------------
carte_trading = {
    "Capitolul 1 – Ce este tradingul?": [
        [
            "1: Tradingul înseamnă cumpărarea și vânzarea de active pe piețe financiare.",
            "2: Activele pot fi: acțiuni, Forex, crypto etc.",
            "3: Scopul tradingului: gestionarea riscului, nu ghicitul.",
            "4: Tradingul sănătos înseamnă disciplină, nu emoții.",
            "5: Fiecare tranzacție este doar o parte dintr-un plan."
        ],
        [
            "Pagina 2 – Tipuri de piețe:",
            "- Piața spot.",
            "- Piața derivatelor.",
            "- Piața OTC.",
            "- Tipuri de brokeri.",
        ],
    ],

    "Capitolul 2 – Riscurile": [
        [
            "1: Folosește doar bani pe care îți permiți să îi pierzi.",
            "2: Tradingul nu rezolvă probleme financiare rapide.",
            "3: Nu mări miza după câteva profituri mici.",
            "4: Fii disciplinat, nu emoțional.",
        ]
    ]
}

# memorează ultima pagină citită pentru fiecare capitol
indice_pag_capitol = {}


# ---------------------------------------------
# Buton Capitol Rotunjit
# ---------------------------------------------
class RoundedButton(ButtonBehavior, BoxLayout):
    def __init__(self, text="", **kwargs):
        super().__init__(orientation="horizontal", **kwargs)
        self.padding = dp(10)
        self.size_hint = (1, None)
        self.height = dp(55)

        self.lbl = Label(
            text=text,
            color=(0, 0, 0, 1), # negru
            font_size=dp(16),
            bold=True,
            halign="left",
            valign="middle",
        )
        self.lbl.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        self.add_widget(self.lbl)

        with self.canvas.before:
            Color(0.79, 0.64, 0.15, 1)
            self.bg = RoundedRectangle(
                radius=[dp(20)],
                pos=self.pos,
                size=self.size
            )
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

# ==============================
# Buton săgeată înapoi (sus stânga)
# ==============================
class BackButton(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", **kwargs)
        self.size_hint = (None, None)
        self.width = dp(48)
        self.height = dp(40)
        self.padding = dp(8)

        self.lbl = Label(
            text="<<", # SĂGEATĂ COMPATIBILĂ
            color=(0, 0, 0, 1), # NEGRU
            font_size=dp(28), # MĂRIME MARE ȘI CLARĂ
            bold=True,
            halign="center",
            valign="middle"
        )
        self.lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.add_widget(self.lbl)

        # Fundal galben închis cu colțuri rotunjite
        with self.canvas.before:
            Color(0.79, 0.64, 0.15, 1) # GALBEN ÎNCHIS
            self.bg = RoundedRectangle(
                radius=[dp(20)],
                pos=self.pos,
                size=self.size
            )

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

# ---------------------------------------------
# Ecran LISTĂ Capitole
# ---------------------------------------------
class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(16), spacing=dp(8), **kwargs)

        title = Label(
            text="Manual de Trading Responsabil",
            font_size=dp(24),
            size_hint=(1, 0.15),
            bold=True
        )
        subtitle = Label(
            text="Bazele unui trading fără iluzii",
            font_size=dp(14),
            size_hint=(1, 0.1)
        )
        self.add_widget(title)
        self.add_widget(subtitle)

        self.add_widget(Widget(size_hint=(1, 0.02)))

        scroll = ScrollView(size_hint=(1, 0.63))
        box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8),
            padding=(0, 0, 0, dp(8))
        )
        box.bind(minimum_height=box.setter("height"))

        for nume_capitol in carte_trading.keys():
            btn = RoundedButton(text=nume_capitol)
            btn.bind(on_press=lambda b, t=nume_capitol: self.open_capitol(t))
            box.add_widget(btn)

        scroll.add_widget(box)
        self.add_widget(scroll)

        footer = Label(
            text="Acest material nu este recomandare financiară.",
            font_size=dp(10),
            size_hint=(1, 0.1)
        )
        self.add_widget(footer)

    def open_capitol(self, nume_capitol):
        app = App.get_running_app()
        start_index = indice_pag_capitol.get(nume_capitol, 0)
        app.root.clear_widgets()
        app.root.add_widget(
            CapitolScreen(
                pagini=carte_trading[nume_capitol],
                titlu=nume_capitol,
                start_index=start_index
            )
        )


# ---------------------------------------------
# Ecran Capitol (Text + Swipe + Card + Progres)
# ---------------------------------------------
class CapitolScreen(BoxLayout):
    def __init__(self, pagini, titlu, start_index=0, **kwargs):
        super().__init__(orientation="vertical", padding=dp(16), spacing=dp(8), **kwargs)

        self.titlu = titlu
        self.pagini = pagini
        self.index_pagina = max(0, min(start_index, len(pagini) - 1))
        self._touch_start_pos = None

        # Bară sus
        top_bar = BoxLayout(orientation="horizontal", size_hint=(1, 0.15), spacing=dp(8))
        btn_back = BackButton()
        btn_back.bind(on_press=lambda x: self.go_back())
        self.lbl_title = Label(text=titlu, font_size=dp(20), bold=True)
        top_bar.add_widget(btn_back)
        top_bar.add_widget(self.lbl_title)
        self.add_widget(top_bar)

        # CARD text
        self.card = BoxLayout(orientation="vertical", size_hint=(1, 0.6), padding=dp(12))
        with self.card.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.card_bg = RoundedRectangle(
                radius=[dp(16)],
                pos=self.card.pos,
                size=self.card.size
            )
        self.card.bind(pos=self.update_card, size=self.update_card)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.box_text = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        self.box_text.bind(minimum_height=self.box_text.setter("height"))
        self.scroll.add_widget(self.box_text)
        self.card.add_widget(self.scroll)
        self.add_widget(self.card)

        # Progres
        self.progress = ProgressBar(max=len(self.pagini), size_hint=(1, 0.05))
        self.add_widget(self.progress)

        # Pagină curentă
        self.lbl_page = Label(text="", size_hint=(1, 0.2), font_size=dp(14))
        self.add_widget(self.lbl_page)

        self.afiseaza_pagina()

    def update_card(self, *args):
        self.card_bg.pos = self.card.pos
        self.card_bg.size = self.card.size

    def afiseaza_pagina(self):
        self.box_text.clear_widgets()
        pagina = self.pagini[self.index_pagina]

        for linie in pagina:
            lbl = Label(
                text=linie,
                font_size=dp(16),
                size_hint_y=None,
                height=dp(40),
                halign="left",
                valign="middle"
            )
            lbl.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
            self.box_text.add_widget(lbl)

        total = len(self.pagini)
        self.lbl_page.text = f"Pagina {self.index_pagina + 1} / {total}"
        self.progress.value = self.index_pagina + 1

        indice_pag_capitol[self.titlu] = self.index_pagina

    def schimba_pagina(self, directie):
        nou = self.index_pagina + directie
        if 0 <= nou < len(self.pagini):
            self.index_pagina = nou
            self.afiseaza_pagina()

    def on_touch_down(self, touch):
        self._touch_start_pos = touch.pos
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._touch_start_pos:
            sx, sy = self._touch_start_pos
            ex, ey = touch.pos
            dx = ex - sx

            if abs(dx) > dp(60):
                if dx < 0:
                    self.schimba_pagina(1)
                else:
                    self.schimba_pagina(-1)

        self._touch_start_pos = None
        return super().on_touch_up(touch)

    def go_back(self):
        indice_pag_capitol[self.titlu] = self.index_pagina
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(MainScreen())


# ---------------------------------------------
# Splash Screen cu LOGO !!! 🔥
# ---------------------------------------------
class SplashScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(16), spacing=dp(8), **kwargs)

        self.add_widget(Widget(size_hint=(1, 0.2)))

        # LOGO PNG
        if os.path.exists("logo.png"):
            logo = Image(
                source="logo.png",
                size_hint=(0.5, 0.35),
                allow_stretch=True,
                keep_ratio=True
            )
            box_logo = BoxLayout(size_hint=(1, 0.4))
            box_logo.add_widget(Widget(size_hint=(0.25, 1)))
            box_logo.add_widget(logo)
            box_logo.add_widget(Widget(size_hint=(0.25, 1)))
            self.add_widget(box_logo)
        else:
            self.add_widget(Label(text="", size_hint=(1, 0.4)))

        # TEXTE SUB LOGO
        title = Label(
            text="Manual de Trading Responsabil",
            font_size=dp(22),
            bold=True,
            size_hint=(1, 0.15)
        )
        subtitle = Label(
            text="Trading real, fără iluzii",
            font_size=dp(14),
            size_hint=(1, 0.1)
        )
        loading = Label(
            text="Se încarcă...",
            font_size=dp(12),
            size_hint=(1, 0.1)
        )

        self.add_widget(title)
        self.add_widget(subtitle)
        self.add_widget(loading)

        self.add_widget(Widget(size_hint=(1, 0.1)))

        Clock.schedule_once(self.to_main, 2.0)

    def to_main(self, dt):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(MainScreen())


# ---------------------------------------------
# APLICAȚIA
# ---------------------------------------------
class TradingBookApp(App):
    def build(self):
        root = BoxLayout()
        root.add_widget(SplashScreen())
        return root


if __name__ == "__main__":
    TradingBookApp().run()