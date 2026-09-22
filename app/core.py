# -*- coding: utf-8 -*-
"""
RushCut - Moteur de traitement local (100% hors ligne)
Fonctions : suppression de silences, détection de beats,
amélioration vocale, accélération pitch-préservé.
"""
import subprocess, re, os, shutil, csv, io
import numpy as np

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"

def _run(cmd, capture=False):
    """Exécute une commande ffmpeg et retourne (returncode, stderr)."""
    p = subprocess.run(cmd, stdout=subprocess.PIPE if capture else None,
                       stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stderr or ""

def has_audio(path):
    rc, err = _run([FFMPEG, "-i", path, "-hide_banner"], capture=True)
    return "Stream #" in err and "Audio:" in err

# ------------------------------------------------------------------
# 1. SUPPRESSION DES SILENCES (Voice Cut)
# ------------------------------------------------------------------
def detect_silences(path, threshold_db=-35.0, min_dur=0.5):
    """Retourne la liste des segments de silence (start, end)."""
    cmd = [FFMPEG, "-i", path, "-af",
           f"silencedetect=n={threshold_db}dB:d={min_dur}", "-f", "null", "-"]
    _, err = _run(cmd, capture=True)
    starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", err)]
    ends   = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(starts, ends[:len(starts)]))

def keep_segments(duration, silences, padding=0.08):
    """Convertit les silences en segments à GARDER, avec padding."""
    segs, cur = [], 0.0
    for s, e in silences:
        s2, e2 = max(0.0, s - padding), e + padding
        if s2 > cur:
            segs.append((cur, s2))
        cur = max(cur, e2)
    if cur < duration:
        segs.append((cur, duration))
    return [(a, b) for a, b in segs if b - a > 0.05]

def get_duration(path):
    cmd = [FFMPEG, "-i", path, "-f", "null", "-"]
    _, err = _run(cmd, capture=True)
    m = re.findall(r"time=(\d+):(\d+):([\d.]+)", err)
    if m:
        h, mn, s = m[-1]
        return int(h) * 3600 + int(mn) * 60 + float(s)
    return 0.0

def remove_silences(input_path, output_path, threshold_db=-35.0,
                    min_dur=0.5, padding=0.08, log=print):
    """Découpe audio+vidéo en supprimant les silences."""
    if not has_audio(input_path):
        log("! Aucune piste audio : copie simple du fichier.")
        shutil.copy(input_path, output_path)
        return
    duration = get_duration(input_path)
    silences = detect_silences(input_path, threshold_db, min_dur)
    segs = keep_segments(duration, silences, padding)
    log(f"  {len(silences)} silence(s) détecté(s) → {len(segs)} segment(s) conservé(s)")
    if not segs:
        log("! Tout le fichier serait supprimé, seuil trop élevé.")
        return
    fc, inputs = [], ""
    for i, (a, b) in enumerate(segs):
        fc.append(f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{i}]")
        inputs += f"[v{i}][a{i}]"
    fc.append(f"{inputs}concat=n={len(segs)}:v=1:a=1[vout][aout]")
    cmd = [FFMPEG, "-y", "-i", input_path, "-filter_complex", ";".join(fc),
           "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", "fast", "-crf", "20",
           "-c:a", "aac", "-b:a", "192k", output_path]
    log("  Ré-encodage en cours...")
    rc, err = _run(cmd, capture=True)
    if rc != 0:
        log("! Erreur ffmpeg : " + err[-500:])
    else:
        log(f"  OK → {output_path}")

# ------------------------------------------------------------------
# 2. DÉTECTION DE BEATS (Beat Cut) -> export CSV de marqueurs
# ------------------------------------------------------------------
def detect_beats(input_path, output_csv, sensitivity=1.5, log=print):
    """Détection d'impacts par flux d'énergie (numpy pur, hors ligne)."""
    cmd = [FFMPEG, "-i", input_path, "-vn", "-ac", "1", "-ar", "22050",
           "-f", "s16le", "pipe:1"]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    x = np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    if len(x) < 4096:
        log("! Fichier audio trop court.")
        return []
    sr, frame, hop = 22050, 1024, 256
    nf = (len(x) - frame) // hop
    idx = np.arange(nf)[:, None] * hop + np.arange(frame)[None, :]
    e = np.sum(x[idx] ** 2, axis=1)
    le = np.log10(e + 1e-10)
    onset = np.maximum(np.diff(le, prepend=le[0]), 0)
    thr = np.median(onset) + sensitivity * np.std(onset)
    min_gap = int(0.25 * sr / hop)  # 4 beats/sec max
    beats, last = [], -min_gap
    for i in np.where(onset > thr)[0]:
        if i - last >= min_gap:
            beats.append(round(i * hop / sr, 3))
            last = i
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["time_sec", "beat"])
        for n, t in enumerate(beats, 1):
            w.writerow([t, n])
    log(f"  {len(beats)} beat(s) détecté(s) → {output_csv}")
    return beats

# ------------------------------------------------------------------
# 3. AMÉLIORATION DE LA VOIX (filtres broadcast)
# ------------------------------------------------------------------
def enhance_voice(input_path, output_path, log=print):
    af = ("highpass=f=70,lowpass=f=13000,afftdn=nf=-25,"
          "acompressor=threshold=0.35:ratio=3:attack=8:release=120:makeup=2,"
          "loudnorm=I=-16:TP=-1.5:LRA=11")
    cmd = [FFMPEG, "-y", "-i", input_path, "-af", af,
           "-c:v", "copy", output_path]
    log("  Traitement vocal : dé-bruitage, compression, normalisation...")
    rc, err = _run(cmd, capture=True)
    log("  OK → " + output_path if rc == 0 else "! Erreur : " + err[-400:])

# ------------------------------------------------------------------
# 4. ACCÉLÉRATION PITCH-PRÉSERVÉE (atempo)
# ------------------------------------------------------------------
def speed_up(input_path, output_path, factor=1.5, log=print):
    factor = min(max(factor, 0.5), 4.0)
    at = []
    f = factor
    while f > 2.0:
        at.append("atempo=2.0"); f /= 2.0
    while f < 0.5:
        at.append("atempo=0.5"); f /= 0.5
    at.append(f"atempo={f:.3f}")
    vf = f"setpts=PTS/{factor:.3f}"
    cmd = [FFMPEG, "-y", "-i", input_path, "-filter_complex",
           f"[0:v]{vf}[v];[0:a]{','.join(at)}[a]",
           "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "fast", "-crf", "20",
           "-c:a", "aac", "-b:a", "192k", output_path]
    log(f"  Accélération x{factor} (voix naturelle conservée)...")
    rc, err = _run(cmd, capture=True)
    log("  OK → " + output_path if rc == 0 else "! Erreur : " + err[-400:])
