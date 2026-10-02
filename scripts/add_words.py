#!/usr/bin/env python3
"""
data/words.json 에 단어를 추가(또는 수정)하는 스크립트.

앱(index.html)과 같은 규칙으로 정리·저장하므로, 앱과 Claude가 같은 파일을
번갈아 고쳐도 형식이 깨지지 않습니다.

사용법
  python3 scripts/add_words.py words.json            # JSON 파일
  python3 scripts/add_words.py words.tsv             # TSV (단어<TAB>뜻<TAB>예문<TAB>태그)
  cat words.json | python3 scripts/add_words.py -    # 표준 입력
  옵션: --tag Day3      모든 단어에 태그 추가
        --update        이미 있는 단어는 새 뜻/예문으로 바꾸고 태그는 합침 (기본: 건너뜀)
        --dry-run       파일은 바꾸지 않고 결과만 출력

JSON 입력 형식: [{"w": "단어", "m": "뜻", "e": "예문(선택)", "t": ["태그"] 또는 "태그1, 태그2"}]
  키 이름은 word/meaning/example/tags 도 허용합니다.
"""
import argparse
import json
import os
import random
import re
import string
import sys
import time
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "words.json")
MAX_FIELD = 500   # 앱과 동일: 칸 하나당 최대 글자 수
MAX_TAG = 40      # 앱과 동일: 태그 하나당 최대 글자 수
ID_RE = re.compile(r"^[\w-]{1,64}$")


def norm(s) -> str:
    """앱의 norm()과 동일: NFC 정규화, 앞뒤 공백 제거, 연속 공백을 하나로."""
    if s is None:
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(s)).strip())


def key_of(w) -> str:
    return norm(w).lower()


def parse_tags(v) -> list:
    """'토익, Day3 / #명사' 또는 리스트 → ['토익', 'Day3', '명사'] (중복 제거, 순서 유지)."""
    parts = v if isinstance(v, list) else re.split(r"[,;/|]+", str(v or ""))
    out = []
    for p in parts:
        t = norm(p).lstrip("#")[:MAX_TAG]
        if t and t not in out:
            out.append(t)
    return out


def new_id(now_ms: int) -> str:
    """앱의 rid('w')와 같은 모양: 'w' + 36진수 시각 + 무작위 6자."""
    alphabet = string.digits + string.ascii_lowercase
    n, b36 = now_ms, ""
    while n:
        n, r = divmod(n, 36)
        b36 = alphabet[r] + b36
    return "w" + b36 + "".join(random.choices(alphabet, k=6))


def load_doc() -> dict:
    """words.json 읽기 + 앱의 sanitizeDoc()과 같은 검증. 없으면 빈 단어장."""
    if not os.path.exists(DATA):
        return {"version": 1, "words": {}}
    with open(DATA, encoding="utf-8") as f:
        raw = json.load(f)  # 깨진 파일이면 여기서 예외 → 덮어쓰지 않고 중단
    words = {}
    for wid, e in (raw.get("words") or {}).items():
        if not isinstance(e, dict) or not ID_RE.match(wid):
            continue
        w, m = norm(e.get("w"))[:MAX_FIELD], norm(e.get("m"))[:MAX_FIELD]
        if not w or not m:
            continue
        words[wid] = {"w": w, "m": m, "e": norm(e.get("e"))[:MAX_FIELD],
                      "t": parse_tags(e.get("t") or []), "c": int(e.get("c") or 0)}
    return {"version": 1, "words": words}


def serialize(doc: dict) -> str:
    """앱의 serialize()와 같은 형식: 단어 하나당 한 줄, 추가순 정렬."""
    words = doc["words"]
    if not words:
        return '{\n"version": 1,\n"words": {}\n}\n'
    ids = sorted(words, key=lambda i: (words[i].get("c") or 0, i))
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    lines = ",\n".join(f"{dump(i)}: {dump(words[i])}" for i in ids)
    return '{\n"version": 1,\n"words": {\n' + lines + "\n}\n}\n"


def read_input(path: str) -> list:
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8-sig").read()
    text = text.strip()
    if not text:
        return []
    if text[0] in "[{":
        data = json.loads(text)
        if isinstance(data, dict):  # {"words":[...]} 또는 앱 형식 {"words":{id:{...}}}
            data = data.get("words", data)
            data = list(data.values()) if isinstance(data, dict) else data
        return [{"w": d.get("w", d.get("word")), "m": d.get("m", d.get("meaning")),
                 "e": d.get("e", d.get("example", "")), "t": d.get("t", d.get("tags", []))}
                for d in data if isinstance(d, dict)]
    rows = []
    for line in text.splitlines():  # TSV
        cols = line.split("\t") + ["", "", "", ""]
        if key_of(cols[0]) in ("단어", "word"):  # 제목 줄 건너뜀
            continue
        rows.append({"w": cols[0], "m": cols[1], "e": cols[2], "t": cols[3]})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="data/words.json에 단어 추가")
    ap.add_argument("input", help="JSON/TSV 파일 경로, 또는 - (표준 입력)")
    ap.add_argument("--tag", default="", help="모든 단어에 붙일 태그 (쉼표로 여러 개)")
    ap.add_argument("--update", action="store_true", help="이미 있는 단어를 새 내용으로 수정")
    ap.add_argument("--dry-run", action="store_true", help="저장하지 않고 결과만 출력")
    args = ap.parse_args()

    doc = load_doc()
    by_key = {key_of(e["w"]): wid for wid, e in doc["words"].items()}
    extra = parse_tags(args.tag)
    now = int(time.time() * 1000)
    added, updated, skipped, bad = [], [], [], 0

    for i, it in enumerate(read_input(args.input)):
        w, m = norm(it.get("w"))[:MAX_FIELD], norm(it.get("m"))[:MAX_FIELD]
        if not w or not m:
            bad += 1
            continue
        e = norm(it.get("e"))[:MAX_FIELD]
        t = parse_tags(parse_tags(it.get("t")) + extra)
        k = key_of(w)
        if k in by_key:
            if not args.update:
                skipped.append(w)
                continue
            old = doc["words"][by_key[k]]
            old.update({"w": w, "m": m, "e": e or old["e"], "t": parse_tags(old["t"] + t)})
            updated.append(w)
        else:
            wid = new_id(now)
            while wid in doc["words"]:
                wid = new_id(now)
            doc["words"][wid] = {"w": w, "m": m, "e": e, "t": t, "c": now + i}
            by_key[k] = wid
            added.append(w)

    print(f"추가 {len(added)} · 수정 {len(updated)} · 건너뜀(이미 있음) {len(skipped)} · 제외(단어/뜻 없음) {bad}")
    if skipped:
        print("건너뛴 단어:", ", ".join(skipped[:30]) + (" …" if len(skipped) > 30 else ""))
    print(f"전체 단어 수: {len(doc['words'])}")
    if args.dry_run or not (added or updated):
        return 0
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(serialize(doc))
    os.replace(tmp, DATA)  # 중간에 실패해도 원본이 깨지지 않도록 원자적 교체
    return 0


if __name__ == "__main__":
    sys.exit(main())
