BANNED_WORDS = ["küfür1", "küfür2", "hakaret"]

def moderate_text(text: str):
    text_lower = text.lower()
    signals = {}
    score = 0.0

    for word in BANNED_WORDS:
        if word in text_lower:
            signals[word] = True
            score += 0.5

    approve = score == 0
    return {"approve": approve, "score": score, "signals": signals}
