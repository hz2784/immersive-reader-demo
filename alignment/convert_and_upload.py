"""Convert aeneas paragraph-level output into word-level timings by linear
character-count interpolation within each fragment, then POST to the Laravel
API at /api/chapters/{id}/timings."""
import json
import re
import sys
import urllib.request

AENEAS_JSON = "chapter_2_aeneas.json"
API_URL = "http://127.0.0.1:8001/api/chapters/2/timings"

with open(AENEAS_JSON) as f:
    aeneas = json.load(f)

paragraphs = []
total_duration = 0.0

for i, frag in enumerate(aeneas["fragments"]):
    text = " ".join(frag["lines"]).strip()
    if not text:
        continue
    begin = float(frag["begin"])
    end = float(frag["end"])
    total_duration = max(total_duration, end)

    # Split into words, keep trailing punctuation with each word.
    tokens = re.findall(r"\S+", text)
    if not tokens:
        continue

    # Allocate time per word by character length (longer words take longer).
    char_counts = [len(t) for t in tokens]
    total_chars = sum(char_counts) or 1
    span = end - begin

    words = []
    cursor = 0  # chars consumed so far
    for tok, c in zip(tokens, char_counts):
        w_start = begin + (cursor / total_chars) * span
        w_end = begin + ((cursor + c) / total_chars) * span
        words.append({"text": tok, "start": round(w_start, 3), "end": round(w_end, 3)})
        cursor += c

    paragraphs.append({"id": f"p{i}", "text": text, "words": words})

payload = {"duration": round(total_duration, 2), "paragraphs": paragraphs}

print(f"Converted {len(paragraphs)} paragraphs, duration {payload['duration']}s")
print(f"Total words: {sum(len(p['words']) for p in paragraphs)}")

# POST to the Laravel API.
req = urllib.request.Request(
    API_URL,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json", "Accept": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req) as r:
        print(f"HTTP {r.status}")
        print(r.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}")
    print(e.read().decode())
    sys.exit(1)
