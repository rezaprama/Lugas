#!/usr/bin/env python3
"""Deterministic meaning guard for Indonesian and English rewrites.

Compares a source passage with a rewrite and reports changes to elements that a
paraphrase, edit, or translation must not alter silently: numbers and units,
statistical comparators, citations, direct quotations, negation, hedging and
boosting, association versus causation, direction of change, quantifier scope,
and non-significance. It also lints Indonesian text for common EYD V/KBBI slips
and translationese, and flags instruction-like text inside a manuscript.

The guard is a screening aid, not a judge of meaning. A clean report does not
prove that a rewrite is faithful, natural, original, or free of plagiarism; a
finding is a prompt for the author to look again.

This file has no third-party dependencies and is copied verbatim into the
bundled Agent Skill (``scripts/guard.py``). Edit ``src/lugas/guard.py`` and
rebuild; do not edit the copy.

Usage:
    python guard.py check SOURCE REWRITE [--translation] [--json]
    python guard.py lint FILE [--json]
    python guard.py extract FILE [--json]
Use ``-`` to read SOURCE or FILE from standard input.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Iterable

GUARD_VERSION = "1.0.0"

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

# --- Lexicons -----------------------------------------------------------------
# Lowercase surface forms. Multiword items are matched as phrases. The lists are
# deliberately short: each entry must carry meaning on its own in academic prose.

NEGATION = (
    # Indonesian
    "tidak", "tak", "bukan", "belum", "tanpa", "jangan", "tiada", "nihil",
    # English
    "not", "no", "never", "without", "none", "cannot", "neither", "nor", "n't",
    # Lexical negatives that often replace an explicit negator in a faithful rewrite
    "di luar cakupan", "alih-alih", "bukannya", "gagal", "rather than", "instead of",
    "fail to", "failed to", "fails to", "lack", "lacked", "lacks", "absence of",
    "unmentioned", "outside the scope",
)
# Expressions that contain a negator but do not negate the proposition.
NEGATION_EXEMPT = (
    "tidak hanya", "bukan hanya", "tak hanya", "tidak sekadar", "bukan sekadar",
    "tidak lain", "tak lain", "bukan main", "not only", "no longer than", "not least",
)

HEDGE = (
    "mungkin", "kemungkinan", "barangkali", "diduga", "dugaan", "cenderung",
    "tampaknya", "agaknya", "mengindikasikan", "mengisyaratkan", "menyiratkan",
    "belum tentu", "relatif", "sebagian besar", "kebanyakan", "diperkirakan", "berpotensi",
    "may", "might", "could", "suggest", "suggests", "suggested", "indicate",
    "indicates", "likely", "possibly", "perhaps", "appear", "appears", "tend",
    "tends", "potentially", "probably", "presumably",
)
BOOSTER = (
    "terbukti", "membuktikan", "pembuktian", "pasti", "dipastikan", "jelas",
    "nyata", "selalu", "mutlak", "tidak diragukan", "sangat signifikan",
    "secara signifikan", "meyakinkan", "prove", "proves", "proved", "proven",
    "demonstrate", "demonstrates", "demonstrated", "clearly", "definitely",
    "always", "confirm", "confirms", "confirmed", "undoubtedly", "conclusively",
    "establishes",
)
CAUSAL = (
    "menyebabkan", "penyebab", "mengakibatkan", "akibat", "berdampak", "dampak",
    "memengaruhi", "mempengaruhi", "pengaruh", "berpengaruh", "efek", "memicu",
    "mendorong", "cause", "causes", "caused", "causal", "causing", "leads to",
    "led to", "lead to", "results in", "resulted in", "effect of", "effects of",
    "impact", "impacts", "affects", "affected", "drives", "drove", "due to",
    "because of", "attributable to",
)
ASSOCIATION = (
    "berhubungan", "hubungan", "berkorelasi", "korelasi", "berasosiasi",
    "asosiasi", "terkait", "berkaitan", "keterkaitan", "seiring",
    "associated", "association", "correlated", "correlation", "correlates",
    "linked", "related", "relationship", "covaried", "co-occurred",
)
UP = (
    "meningkat", "meningkatkan", "peningkatan", "naik", "kenaikan", "bertambah",
    "lebih tinggi", "lebih besar", "lebih banyak", "melonjak",
    "increase", "increased", "increases", "increasing", "higher", "greater",
    "rise", "rose", "risen", "more",
)
DOWN = (
    "menurun", "menurunkan", "penurunan", "turun", "berkurang", "mengurangi",
    "pengurangan", "lebih rendah", "lebih kecil", "lebih sedikit", "merosot",
    "decrease", "decreased", "decreases", "decreasing", "lower", "smaller",
    "reduce", "reduced", "reduces", "reduction", "decline", "declined", "fewer",
    "less", "fell", "drop", "dropped",
)
UNIVERSAL = (
    "semua", "seluruh", "setiap", "selalu", "tiap", "segala",
    "all", "every", "each", "always", "universally",
)
PARTIAL = (
    "sebagian", "beberapa", "sejumlah", "sebagian besar", "mayoritas", "kebanyakan",
    "some", "several", "most", "many", "a subset", "majority",
)
NONSIG_RE = re.compile(
    r"\b(?:tidak|tak|not|non-?|did not|does not|was not|were not)\W+(?:\w+\W+){0,3}?"
    r"(?:signifikan|significant(?:ly)?|bermakna|nyata)\b"
)
NO_EFFECT_RE = re.compile(
    r"\b(?:tidak|tak|tanpa|no|not|did not|does not|had no|has no|without)\W+(?:(?:ada|memiliki|any|an?)\W+)?"
    r"(?:pengaruh|berpengaruh|memengaruhi|mempengaruhi|efek|dampak|berdampak|hubungan|effect|effects|impact|"
    r"influence|affect|affects|association|relationship)\b"
)
NUMBER_WORDS = {
    "nol": "0", "satu": "1", "dua": "2", "tiga": "3", "empat": "4", "lima": "5", "enam": "6",
    "tujuh": "7", "delapan": "8", "sembilan": "9", "sepuluh": "10", "sebelas": "11",
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
    "seven": "7", "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12",
}
POSITIVE = ("positif", "berbanding lurus", "positive", "positively", "direct relationship")
NEGATIVE = ("negatif", "berbanding terbalik", "negative", "negatively", "inverse", "inversely")
INJECTION = (
    r"\babaikan (?:semua |seluruh )?(?:instruksi|perintah|aturan)",
    r"\blupakan (?:semua |seluruh )?(?:instruksi|perintah)",
    r"\bignore (?:all |any |the )?(?:previous |prior |above )?(?:instructions|rules|prompts?)",
    r"\bdisregard (?:all |the )?(?:previous |prior |above )?(?:instructions|rules)",
    r"\b(?:system prompt|you are now|kamu sekarang adalah|anda sekarang adalah)\b",
)

# --- Regular expressions ---------------------------------------------------------

_WORD = r"[A-Za-zÀ-ÖØ-öø-ÿ]"
_NUM = r"(?<![\w.,])[-−–+]?\d+(?:[.,]\d+)*"
UNIT = (
    r"%|‰|°C|°F|K|kg|mg|µg|μg|g|t|ton|km|cm|mm|µm|μm|nm|m²|m2|m³|m3|m|L|l|mL|ml|dL|"
    r"Hz|kHz|MHz|GHz|kW|MW|W|kWh|V|mV|kV|A|mA|Pa|kPa|MPa|GPa|N|kN|J|kJ|dB|ppm|ppb|"
    r"s|ms|min|h|jam|menit|detik|hari|minggu|pekan|bulan|tahun|days?|weeks?|months?|"
    r"years?|hours?|minutes?|seconds?|orang|responden|sampel|peserta|pasien|"
    r"participants?|patients?|respondents?|samples?|kali|times|USD|IDR|Rp|juta|"
    r"miliar|triliun|ribu|million|billion|thousand"
)
NUM_ONLY_RE = re.compile(r"[-−–+]?\d+(?:[.,]\d+)*")
NUMBER_RE = re.compile(_NUM + r"(?:\s?(?:" + UNIT + r")(?![\w]))?")
COMPARATOR_RE = re.compile(
    r"\b([pPnNrRtFβχ]|OR|RR|HR|CI|SD|SE|R²|R2|d|η²)\s*([<>=≤≥≈])\s*(" + _NUM.replace("(?<![\\w.,])", "") + r")"
)
NUMERIC_CITATION_RE = re.compile(r"\[(\d+(?:\s*[–,-]\s*\d+)*)\]")
AUTHOR_YEAR_RE = re.compile(
    r"([A-Z][A-Za-zÀ-ÖØ-öø-ÿ'’-]+)"
    r"(?:\s+(?:et al\.?|dkk\.?|&|and|dan)(?:\s+[A-Z][A-Za-zÀ-ÖØ-öø-ÿ'’-]+)?)?"
    r"(?:,\s*|\s+\(\s*)((?:1[5-9]|20)\d{2}[a-z]?|n\.d\.|t\.t\.)"
)
QUOTE_RE = re.compile(r'["“]([^"”]{8,400})["”]')


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    detail: str = ""

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def _fold(text: str) -> str:
    text = text.replace("’", "'").replace("−", "-").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", text.casefold())


def _phrase_counts(text: str, phrases: Iterable[str], exempt: Iterable[str] = ()) -> Counter:
    folded = _fold(text)
    for item in exempt:
        folded = re.sub(r"(?<!\w)" + re.escape(item) + r"(?!\w)", " ", folded)
    counts: Counter = Counter()
    for phrase in sorted(set(phrases), key=len, reverse=True):
        if phrase == "n't":
            hits = len(re.findall(r"\w+n't\b", folded))
        else:
            pattern = r"(?<![\w-])" + re.escape(phrase) + r"(?:nya|lah|kah)?(?![\w-])"
            hits = len(re.findall(pattern, folded))
            if hits:
                folded = re.sub(pattern, " ", folded)
        if hits:
            counts[phrase] += hits
    return counts


def _canonical_number(raw: str, swap_decimal: bool) -> str:
    value = raw.strip().replace("−", "-").replace("–", "-").replace("+", "")
    value = re.sub(r"\s+", " ", value)
    if swap_decimal:
        value = value.replace(",", "·").replace(".", "·")
    return value


def extract(text: str, swap_decimal: bool = False) -> dict[str, object]:
    """Return protected elements found in *text*."""

    # Citation years and reference numbers are tracked as citations, not numbers.
    numeric_text = NUMERIC_CITATION_RE.sub(" ", AUTHOR_YEAR_RE.sub(" ", text))
    numbers: Counter = Counter(
        _canonical_number(NUM_ONLY_RE.match(m.group(0)).group(0), swap_decimal)  # type: ignore[union-attr]
        for m in NUMBER_RE.finditer(numeric_text)
    )
    worded: set[str] = set()
    for word, digit in NUMBER_WORDS.items():
        hits = len(re.findall(r"(?<![\w-])" + word + r"(?![\w-])", numeric_text, re.I))
        if hits:
            numbers[digit] += hits
            worded.add(digit)
    comparators = Counter(
        f"{m.group(1)} {m.group(2)} {_canonical_number(m.group(3), swap_decimal)}"
        for m in COMPARATOR_RE.finditer(text)
    )
    citations: Counter = Counter()
    for m in AUTHOR_YEAR_RE.finditer(text):
        citations[f"{m.group(1)} {m.group(2)}"] += 1
    for m in NUMERIC_CITATION_RE.finditer(text):
        citations["[" + re.sub(r"\s", "", m.group(1)).replace("–", "-") + "]"] += 1
    quotes = [m.group(1).strip() for m in QUOTE_RE.finditer(text) if len(m.group(1).split()) >= 3]
    return {
        "numbers": {k: v for k, v in numbers.items() if v},
        "worded_numbers": sorted(worded),
        "comparators": dict(comparators),
        "citations": dict(citations),
        "quotes": quotes,
        "negation": sum(_phrase_counts(text, NEGATION, NEGATION_EXEMPT).values()),
        "hedges": sum(_phrase_counts(text, HEDGE).values()),
        "boosters": sum(_phrase_counts(text, BOOSTER).values()),
        "causal": sum(_phrase_counts(text, CAUSAL).values()),
        "association": sum(_phrase_counts(text, ASSOCIATION).values()),
        "up": sum(_phrase_counts(text, UP).values()),
        "down": sum(_phrase_counts(text, DOWN).values()),
        "universal": sum(_phrase_counts(text, UNIVERSAL).values()),
        "partial": sum(_phrase_counts(text, PARTIAL).values()),
        "nonsignificant": len(NONSIG_RE.findall(_fold(text))),
        "no_effect": len(NO_EFFECT_RE.findall(_fold(text))),
        "positive": sum(_phrase_counts(text, POSITIVE).values()),
        "negative": sum(_phrase_counts(text, NEGATIVE).values()),
        "injection": [p for p in INJECTION if re.search(p, _fold(text))],
    }


def _missing(source: dict, output: dict) -> list[str]:
    return sorted(k for k, v in source.items() if output.get(k, 0) < v)


def _added(source: dict, output: dict) -> list[str]:
    return sorted(k for k, v in output.items() if source.get(k, 0) < v)


def _sentences(text: str) -> int:
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if len(s.split()) >= 3])


def check(source: str, rewrite: str, translation: bool = False, summary: bool = False) -> list[Finding]:
    """Compare *rewrite* against *source* and return findings, most severe first."""

    a = extract(source, swap_decimal=translation)
    b = extract(rewrite, swap_decimal=translation)
    findings: list[Finding] = []

    for label, key in (("number", "numbers"), ("statistic", "comparators"), ("citation", "citations")):
        missing = _missing(a[key], b[key])  # type: ignore[arg-type]
        added = _added(a[key], b[key])  # type: ignore[arg-type]
        if missing and key == "comparators":
            # Notation may change legitimately ("n = 46" -> "46 bridges") if the value survives.
            values = set(b["numbers"])  # type: ignore[arg-type]
            severe = [m for m in missing if m.split(" ", 2)[2] not in values]
            if severe:
                findings.append(Finding("high", "statistic-missing", "Source statistic absent or changed in rewrite", "; ".join(severe)))
            if len(severe) < len(missing):
                findings.append(Finding("low", "statistic-notation-changed", "Statistic value kept but notation changed; confirm it is still reported correctly", "; ".join(m for m in missing if m not in severe)))
        elif missing:
            gone = [m for m in missing if m not in b[key]]  # type: ignore[operator]
            if gone:
                findings.append(Finding("high", f"{label}-missing", f"Source {label}(s) absent or changed in rewrite", "; ".join(gone)))
            if len(gone) < len(missing):
                findings.append(Finding("low", f"{label}-repeat-dropped", f"A repeated {label} now appears fewer times; confirm nothing was lost", "; ".join(m for m in missing if m not in gone)))
        if added:
            spelled = [x for x in added if key == "numbers" and x in b["worded_numbers"] and x not in a[key]]  # type: ignore[operator]
            hard = [x for x in added if x not in spelled]
            if hard:
                findings.append(Finding("high", f"{label}-added", f"Rewrite introduces {label}(s) not in source", "; ".join(hard)))
            if spelled:
                findings.append(Finding("medium", "number-word-added", "Rewrite adds a spelled-out number not in source; check it is derived, not invented", "; ".join(spelled)))

    if not translation:
        flat = _fold(rewrite)
        lost = [q for q in a["quotes"] if _fold(q) not in flat]  # type: ignore[union-attr]
        if lost:
            findings.append(Finding("high", "quote-altered", "Direct quotation not reproduced verbatim", " | ".join(lost)))

    if b["negation"] < a["negation"]:
        findings.append(Finding("medium" if translation else "high", "negation-lost", "Fewer negators in rewrite; a negative claim may have flipped", f"{a['negation']} → {b['negation']}"))
    elif b["negation"] > a["negation"]:
        findings.append(Finding("medium", "negation-added", "More negators in rewrite; check polarity", f"{a['negation']} → {b['negation']}"))

    if a["association"] and not a["causal"] and b["causal"]:
        findings.append(Finding("high", "association-to-causation", "Source states association; rewrite uses causal language", f"causal terms 0 → {b['causal']}"))
    elif a["association"] and not b["association"] and not a["causal"]:
        findings.append(Finding("medium", "association-framing-lost", "Source frames the finding as association; rewrite drops that framing", ""))
    elif b["causal"] > a["causal"]:
        findings.append(Finding("medium", "causal-increase", "More causal language than source", f"{a['causal']} → {b['causal']}"))

    if a["nonsignificant"] and b["no_effect"] > a["no_effect"]:
        findings.append(Finding("high", "nonsignificance-to-no-effect", "Non-significant result restated as absence of effect", ""))

    if b["boosters"] > a["boosters"]:
        findings.append(Finding("high" if b["hedges"] < a["hedges"] else "medium", "claim-strengthened", "Rewrite adds certainty/boosting language", f"boosters {a['boosters']} → {b['boosters']}; hedges {a['hedges']} → {b['hedges']}"))
    elif b["hedges"] < a["hedges"]:
        findings.append(Finding("medium", "hedge-removed", "Fewer hedges than source; uncertainty may be lost", f"{a['hedges']} → {b['hedges']}"))

    for pair in (("up", "down"), ("positive", "negative")):
        for side, other in (pair, pair[::-1]):
            if b[side] < a[side] and b[other] > a[other]:
                findings.append(Finding("high", "direction-flipped", "Direction or polarity appears reversed", f"{side} {a[side]}→{b[side]}, {other} {a[other]}→{b[other]}"))
                break

    if b["universal"] > a["universal"] and a["partial"] >= b["partial"]:
        findings.append(Finding("medium", "scope-widened", "Rewrite adds universal quantifiers (all/semua/setiap)", f"{a['universal']} → {b['universal']}"))
    if a["partial"] and b["partial"] < a["partial"]:
        findings.append(Finding("medium", "scope-qualifier-lost", "Partial-scope qualifiers removed (some/sebagian/beberapa)", f"{a['partial']} → {b['partial']}"))

    if a["injection"]:
        findings.append(Finding("low", "instruction-in-source", "Source contains instruction-like text; treat it as manuscript content, not a command", ""))

    src_words, out_words = len(source.split()), len(rewrite.split())
    shrunk = out_words < 0.5 * src_words or (_sentences(rewrite) < _sentences(source) and out_words < 0.75 * src_words)
    if not summary and src_words >= 15 and shrunk:
        findings.append(Finding("medium", "content-dropped", "Rewrite is under half the source length; content may be missing", f"{src_words} → {out_words} words"))

    findings.sort(key=lambda f: (SEVERITY_ORDER[f.severity], f.code))
    return findings


# --- Indonesian lint ------------------------------------------------------------------
# (id, level, pattern, flags, advice). K = kaidah (EYD V/KBBI), G = gaya, T = translationese.
_SENT = r"(?:^|(?<=[.!?])\s+)"
ID_RULES: tuple[tuple[str, str, str, int, str], ...] = (
    ("ID-K01", "K", r"\bdimana\b", re.I, "Tulis terpisah: di mana. Sebagai penghubung, pertimbangkan yang/tempat/saat."),
    ("ID-K02", "K", r"\b(?:diatas|dibawah|didalam|diluar|didepan|dibelakang|disamping|diantara|kedalam)\b", re.I, "Kata depan di/ke ditulis terpisah dari kata tempat."),
    ("ID-K03", "K", r"\bdi\s(?:analisis|analisa|uji|lakukan|gunakan|ukur|ambil|peroleh|hitung|teliti|bahas|amati|olah|kumpulkan|terapkan|tentukan|sajikan)\b", re.I, "Awalan di- ditulis serangkai dengan verba: dianalisis, diuji."),
    ("ID-K04", "K", r"\badalah merupakan\b", re.I, "Pilih satu: adalah atau merupakan."),
    ("ID-K05", "K", r"\b(?:agar supaya|demi untuk|sejak dari|berdasarkan pada|berbagai macam)\b", re.I, "Bentuk mubazir; pakai satu unsur saja."),
    ("ID-K06", "K", _SENT + r"(?:Dari|Dalam|Pada|Berdasarkan)\s[^.?!,;]{1,60}?\s(?:menunjukkan|membahas|menjelaskan|menyatakan|menyimpulkan|memperlihatkan)\b", 0, "Kalimat kehilangan subjek karena diawali kata depan; buang kata depan atau ubah ke pasif."),
    ("ID-K07", "K", _SENT + r"(?:Sehingga|Sedangkan|Dan|Tetapi)\b", 0, "Konjungsi intrakalimat di awal kalimat; gabungkan atau ganti (Akibatnya, Adapun, Namun)."),
    ("ID-K08", "K", r"\b(?:meskipun|walaupun|walau|kendatipun)\b[^.;]{1,120}?,\s*(?:tetapi|namun)\b", re.I, "Dua konjungsi untuk satu hubungan; hapus tetapi/namun."),
    ("ID-K09", "K", r"\blebih\s+\w+\s+dari\b(?!\s+(?:pada|sekadar))", re.I, "Perbandingan baku memakai daripada."),
    ("ID-K10", "K", r"\b(?:merubah|dirubah|mempengaruhi|analisa|resiko|praktek|sistim|aktifitas|efektifitas|kwalitas|obyek|subyek|nampak|ijin|jaman|kharisma|apotik|hakekat|nasehat|silahkan|antri)\b", re.I, "Bentuk tidak baku (KBBI): mengubah, memengaruhi, analisis, risiko, praktik, sistem, aktivitas, efektivitas, kualitas, objek, subjek, tampak, izin, zaman, karisma, apotek, hakikat, nasihat, silakan, antre."),
    ("ID-K11", "K", r"\b\d+\.\d+\s?(?:%|kg|g|mg|cm|mm|km|m|V|A|W|Hz|°C)(?!\w)", 0, "Dalam teks Indonesia, desimal memakai koma (4,8%); kecuali gaya selingkung jurnal menetapkan lain."),
    ("ID-K12", "K", r"\b\d+(?:,\d+)?(?:kg|mg|cm|mm|km|kW|kHz|MHz|ms)\b", 0, "Beri spasi antara angka dan lambang satuan (10 kg); persen (%) ditulis rapat."),
    ("ID-K13", "K", r"\b(?:para|banyak|beberapa|berbagai)\s+(\w+)-\1\b", re.I, "Penanda jamak ganda; cukup satu (para peneliti, bukan para peneliti-peneliti)."),
    ("ID-K14", "K", r"\bsangat\s+\w+\s+sekali\b", re.I, "Pilih sangat atau sekali."),
    ("ID-K15", "K", r"\b(?:antar|pasca|non|multi|sub|pra|semi|inter|intra|ekstra) (?=[a-z]{3,})", 0, "Bentuk terikat ditulis serangkai (antarvariabel, pascapanen, nonlinear)."),
    ("ID-K16", "K", r"\bantara\s+(?!lain\b)[^.,;]{1,40}?\sdengan\b", re.I, "Pasangan baku: antara … dan …."),
    ("ID-T01", "T", r"\bmemainkan peran\w*\b", re.I, "Kalke play a role; pakai berperan atau jelaskan perannya."),
    ("ID-T02", "T", r"\bmengambil tempat\b", re.I, "Kalke take place; pakai berlangsung/terjadi."),
    ("ID-T03", "T", r"\b(?:di|pada)\s+mana\b|\byang mana\b", re.I, "Kalke where/which sebagai penghubung; pakai yang, tempat, atau pecah kalimat."),
    ("ID-T04", "T", r"\bmelakukan (?:pengukuran|analisis|pengujian|pengamatan|perhitungan|penelitian)\b", re.I, "Verba langsung lebih ringkas: mengukur, menganalisis, menguji."),
    ("ID-T05", "T", r"\bmengalami (?:peningkatan|penurunan|kenaikan|perubahan)\b", re.I, "Verba langsung: meningkat, menurun, naik, berubah."),
    ("ID-G01", "G", r"\b(?:di era (?:digital|modern|globalisasi)|seiring (?:dengan )?perkembangan zaman|t(?:idak|ak) dapat dipungkiri|seperti yang kita ketahui)\b", re.I, "Pembuka generik; mulai dari masalah yang konkret."),
    ("ID-G02", "G", r"\bsangat signifikan\b", re.I, "Signifikansi statistik tidak bergradasi; laporkan nilai uji dan besaran efek."),
    ("ID-G03", "G", r"\b(?:solusi inovatif|sangat krusial|memegang peranan yang sangat)\b", re.I, "Penguat promosi; ganti dengan bukti atau hapus."),
)


def lint_id(text: str) -> list[dict[str, object]]:
    """Return Indonesian rule hits with line numbers. Hints, not verdicts."""

    hits: list[dict[str, object]] = []
    body = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    for rule_id, level, pattern, flags, advice in ID_RULES:
        for match in re.finditer(pattern, body, flags | re.M):
            line = body.count("\n", 0, match.start()) + 1
            hits.append({"id": rule_id, "level": level, "line": line, "match": match.group(0).strip(), "advice": advice})
    hal_ini = len(re.findall(r"\bhal ini\b", body, re.I))
    paragraphs = max(1, len([p for p in body.split("\n\n") if p.strip()]))
    if hal_ini >= 3 and hal_ini / paragraphs >= 1:
        hits.append({"id": "ID-G04", "level": "G", "line": 0, "match": f"hal ini ×{hal_ini}", "advice": "Rujukan 'hal ini' berulang; sebut subjeknya secara langsung."})
    hits.sort(key=lambda h: (h["line"], h["id"]))
    return hits


# --- CLI ---------------------------------------------------------------------------


def _read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="guard", description="Deterministic meaning guard (ID/EN).")
    parser.add_argument("--version", action="version", version=GUARD_VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("check", help="compare source and rewrite")
    c.add_argument("source")
    c.add_argument("rewrite")
    c.add_argument("--translation", action="store_true", help="allow decimal comma/point swap; skip verbatim quote check")
    c.add_argument("--summary", action="store_true", help="the rewrite is a summary; do not flag shortening")
    c.add_argument("--json", action="store_true")
    l = sub.add_parser("lint", help="Indonesian EYD V/KBBI and translationese hints")
    l.add_argument("file")
    l.add_argument("--json", action="store_true")
    e = sub.add_parser("extract", help="list protected elements")
    e.add_argument("file")
    e.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "check":
        findings = check(_read(args.source), _read(args.rewrite), translation=args.translation, summary=args.summary)
        if args.json:
            print(json.dumps({"version": GUARD_VERSION, "findings": [f.as_dict() for f in findings]}, ensure_ascii=False, indent=2))
        elif not findings:
            print("No guarded change detected. Still read the rewrite yourself: this check is lexical.")
        else:
            for f in findings:
                print(f"[{f.severity}] {f.code}: {f.message}" + (f" ({f.detail})" if f.detail else ""))
        return 1 if any(f.severity == "high" for f in findings) else 0

    if args.command == "lint":
        hits = lint_id(_read(args.file))
        if args.json:
            print(json.dumps(hits, ensure_ascii=False, indent=2))
        else:
            for h in hits:
                print(f"{h['line']}: {h['id']} [{h['level']}] {h['match']!r} — {h['advice']}")
            if not hits:
                print("No rule hits. Hints only; read in context.")
        return 1 if any(h["level"] == "K" for h in hits) else 0

    value = extract(_read(args.file))
    print(json.dumps(value, ensure_ascii=False, indent=2) if args.json else value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
