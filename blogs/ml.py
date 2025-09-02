import re
import math

OFFENSIVE = {
    "salak","aptal","gerizekalı","mal","orospu","lanet","siktir","bok","piç",
    "idiot","stupid","trash","dumb","f*k","f**k","shit","bastard","moron","oe","amk","sik","ananısikiyim","göt",
}
POSITIVE = {"harika","mükemmel","güzel","teşekkür","beğendim","süper","iyi","şahane","perfect","great","awesome","nice","bravo"}
NEGATIVE = {"kötü","berbat","rezil","iğrenç","nefret","beğenmedim","saçma","yersiz","hatalı","useless","bad","terrible","awful","worst"}

URL_PAT = re.compile(r"(https?://|www\.)|\b(t\.me|wa\.me|bit\.ly|tinyurl)\b", re.I)
CONTACT_PAT = re.compile(r"(\b\d{10,}\b|@[\w\d_]{3,})")
REPEAT_PAT = re.compile(r"(.)\1{4,}")

def _toxicity_score(text: str) -> float:
    t = (text or "").lower()
    hits = sum(1 for w in OFFENSIVE if w in t)
    return max(0.0, min(1.0, 1 - math.exp(-1.2 * hits)))

def _sentiment_score(text: str) -> float:
    t = (text or "").lower()
    pos = sum(1 for w in POSITIVE if w in t)
    neg = sum(1 for w in NEGATIVE if w in t)
    if pos == 0 and neg == 0:
        return 0.0
    raw = (pos - neg) / (pos + neg)
    return max(-1.0, min(1.0, raw))

def _is_spam(text: str):
    t = (text or "").lower()
    reasons = []
    if URL_PAT.search(t): reasons.append("url/shortener")
    if CONTACT_PAT.search(t): reasons.append("iletişim/handle")
    if REPEAT_PAT.search(t): reasons.append("aşırı tekrar")
    if len(t.strip()) < 5: reasons.append("çok kısa")
    if sum(ch.isalpha() for ch in t) < 6 and (URL_PAT.search(t) or CONTACT_PAT.search(t)):
        reasons.append("metin yok")
    return (True, ", ".join(reasons)) if reasons else (False, "")

def analyze_text(text: str):
    tox = _toxicity_score(text)
    sen = _sentiment_score(text)
    spam, reason = _is_spam(text)

    decision, dec_reason = "APPROVED", "temiz"
    if spam:
        decision, dec_reason = "REJECTED", f"spam: {reason}"
    elif tox >= 0.40:
        decision, dec_reason = "REJECTED", "toxic içerik"
    elif 0.25 <= tox < 0.40:
        decision, dec_reason = "PENDING", "el kontrolü (orta toksisite)"

    return {
        "toxicity": round(tox, 3),
        "sentiment": round(sen, 3),
        "is_spam": spam,
        "reason": dec_reason,
        "decision": decision,
    }
