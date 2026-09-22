# -*- coding: utf-8 -*-
"""RushCut — Interface graphique (Tkinter, 100% hors ligne)."""
import os, sys, threading, tkinter as tk
from tkinter import ttk, filedialog, messagebox
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

BG, PANEL = "#0b0f0e", "#131a18"
GREEN, RED, TXT = "#2dff8f", "#ff4d5e", "#d8e6df"

class RushCut(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RUSHCUT — Montage local")
        self.geometry("520x640")
        self.configure(bg=BG)
        self.file = tk.StringVar()
        self.opt_silence = tk.BooleanVar(value=True)
        self.opt_beats   = tk.BooleanVar(value=False)
        self.opt_voice   = tk.BooleanVar(value=False)
        self.opt_speed   = tk.BooleanVar(value=False)
        self.speed_val   = tk.DoubleVar(value=1.5)
        self.thresh      = tk.DoubleVar(value=-35.0)

        f = ("Segoe UI", 10)
        tk.Label(self, text="RUSHCUT", bg=BG, fg=GREEN,
                 font=("Segoe UI", 22, "bold")).pack(pady=(14, 0))
        tk.Label(self, text="Montage express · 100% hors ligne",
                 bg=BG, fg=TXT, font=f).pack()

        box = tk.Frame(self, bg=PANEL, padx=16, pady=14)
        box.pack(fill="x", padx=16, pady=12)
        tk.Button(box, text="📁  IMPORTER UN FICHIER", command=self.pick,
                  bg=GREEN, fg="#04140b", font=("Segoe UI", 10, "bold"),
                  relief="flat", width=28).pack(pady=(0, 8))
        self.lbl = tk.Label(box, textvariable=self.file, bg=PANEL, fg=TXT,
                            font=f, wraplength=440)
        self.lbl.pack()

        opts = tk.Frame(self, bg=BG)
        opts.pack(fill="x", padx=24)
        def chk(txt, var):
            tk.Checkbutton(opts, text=txt, variable=var, bg=BG, fg=TXT,
                           selectcolor=PANEL, activebackground=BG,
                           activeforeground=TXT, font=f).pack(anchor="w", pady=2)
        chk("🎤  VOICE CUT — supprimer les silences", self.opt_silence)
        chk("🎵  BEAT CUT — exporter les marqueurs (CSV)", self.opt_beats)
        chk("✨  AMÉLIORER LA VOIX", self.opt_voice)
        chk("⏩  ACCÉLÉRER (pitch préservé)", self.opt_speed)

        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=24, pady=6)
        tk.Label(row, text="Seuil silences (dB) :", bg=BG, fg=TXT,
                 font=f).pack(side="left")
        tk.Entry(row, textvariable=self.thresh, width=6, bg=PANEL, fg=TXT,
                 insertbackground=TXT, relief="flat",
                 font=f).pack(side="left", padx=6)
        tk.Label(row, text="Vitesse x", bg=BG, fg=TXT, font=f).pack(side="left")
        tk.Entry(row, textvariable=self.speed_val, width=5, bg=PANEL, fg=TXT,
                 insertbackground=TXT, relief="flat",
                 font=f).pack(side="left", padx=6)

        tk.Button(self, text="▶  LANCER LE TRAITEMENT", command=self.run,
                  bg=GREEN, fg="#04140b", font=("Segoe UI", 11, "bold"),
                  relief="flat", height=2).pack(fill="x", padx=24, pady=10)

        self.bar = ttk.Progressbar(self, mode="indeterminate")
        self.bar.pack(fill="x", padx=24)
        self.logw = tk.Text(self, bg=PANEL, fg=GREEN, height=12,
                            insertbackground=GREEN, relief="flat", font=("Consolas", 9))
        self.logw.pack(fill="both", expand=True, padx=16, pady=12)
        self.log("RushCut prêt. Importez un fichier pour commencer.")

    def log(self, m):
        self.logw.insert("end", m + "\n")
        self.logw.see("end")

    def pick(self):
        p = filedialog.askopenfilename(filetypes=[
            ("Médias", "*.mp4 *.mov *.mkv *.avi *.mp3 *.wav *.m4a")])
        if p:
            self.file.set(p)

    def run(self):
        src = self.file.get()
        if not src or not os.path.exists(src):
            messagebox.showwarning("RushCut", "Importez d'abord un fichier.")
            return
        outdir = filedialog.askdirectory(title="Dossier de sortie")
        if not outdir:
            return
        threading.Thread(target=self._process,
                         args=(src, outdir), daemon=True).start()

    def _process(self, src, outdir):
        self.bar.start(10)
        name = os.path.splitext(os.path.basename(src))[0]
        try:
            cur = src
            if self.opt_silence.get():
                self.log("— Voice Cut —")
                core.remove_silences(cur, os.path.join(outdir, name + "_nocut.mp4"),
                                     threshold_db=self.thresh.get(), log=self.log)
                cur = os.path.join(outdir, name + "_nocut.mp4")
            if self.opt_voice.get():
                self.log("— Amélioration vocale —")
                core.enhance_voice(cur, os.path.join(outdir, name + "_voice.mp4"),
                                   log=self.log)
                cur = os.path.join(outdir, name + "_voice.mp4")
            if self.opt_speed.get():
                self.log("— Accélération —")
                core.speed_up(cur, os.path.join(outdir, name + "_x" +
                                 str(self.speed_val.get()).replace(".", "p") + ".mp4"),
                              self.speed_val.get(), log=self.log)
            if self.opt_beats.get():
                self.log("— Beat Cut —")
                core.detect_beats(cur, os.path.join(outdir, name + "_beats.csv"),
                                  log=self.log)
            self.log("✔ Terminé !")
        except Exception as ex:
            self.log("! Erreur : " + str(ex))
        finally:
            self.bar.stop()

if __name__ == "__main__":
    RushCut().mainloop()
