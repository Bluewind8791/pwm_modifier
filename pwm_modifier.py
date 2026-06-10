import re
import pyperclip


# ─────────────────────────────────────────────────────────────
# 인자 파싱 유틸
# ─────────────────────────────────────────────────────────────

def _split_args(s):
    """top-level 콤마로 인자 분리 (따옴표/괄호 안의 콤마는 무시)."""
    args, cur, depth = [], "", 0
    in_str, str_ch = False, ""
    i = 0
    while i < len(s):
        c = s[i]
        if in_str:
            cur += c
            if c == "\\" and i + 1 < len(s):
                cur += s[i + 1]
                i += 1
            elif c == str_ch:
                in_str = False
        elif c in "\"'":
            in_str, str_ch = True, c
            cur += c
        elif c in "([{":
            depth += 1
            cur += c
        elif c in ")]}":
            depth -= 1
            cur += c
        elif c == "," and depth == 0:
            args.append(cur.strip())
            cur = ""
        else:
            cur += c
        i += 1
    if cur.strip():
        args.append(cur.strip())
    return args


def _unquote(a):
    """양끝 따옴표 제거 후 trim. 변수/식은 그대로 둠."""
    a = a.strip()
    if len(a) >= 2 and a[0] in "\"'" and a[-1] == a[0]:
        return a[1:-1].strip()
    return a


def _parse_call(line):
    """'pwm.method(...)' 에서 (메서드명, 인자문자열, 뒤쪽) 추출. 괄호 매칭 기반."""
    m = re.match(r"pwm\.(\w+)\s*\(", line)
    if not m:
        return None
    name, start = m.group(1), m.end()
    depth, in_str, str_ch, i = 1, False, "", start
    while i < len(line):
        c = line[i]
        if in_str:
            if c == "\\":
                i += 1
            elif c == str_ch:
                in_str = False
        elif c in "\"'":
            in_str, str_ch = True, c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    return name, line[start:i], line[i + 1:]


# ─────────────────────────────────────────────────────────────
# pwm.* 메서드 → SQL 재조립
# ─────────────────────────────────────────────────────────────

def _to_sql(name, raw_args):
    args = _split_args(raw_args)
    n = len(args)

    def a(i):
        return _unquote(args[i]) if i < n else ""

    # 첫 인자가 SQL 문자열인 메서드
    if name in ("appendWithCR", "appendWithParam", "appendFormat"):
        return a(0)
    if name == "append":
        # append(str) / append(CAT_OP, col, OP, val)
        return f"{a(0)} {a(1)} {a(2)} {a(3)}".strip() if n >= 4 else a(0)
    if name == "appendDateRange":  # (CAT_OP, col, from, to)
        return f"{a(0)} {a(1)} >= {a(2)} {a(0)} {a(1)} < {a(3)}"

    # and / or 연산자 분리형: and(col, OP, val) / and(compString)
    if name in ("and", "or"):
        cat = name.upper()
        return f"{cat} {a(0)} {a(1)} {a(2)}".rstrip() if n >= 3 else f"{cat} {a(0)}"

    # equal 계열
    if name == "andEqual":
        return f"AND {a(0)} = {a(1)}"
    if name == "andNotEqual":
        return f"AND {a(0)} <> {a(1)}"
    if name == "orEqual":
        return f"OR {a(0)} = {a(1)}"

    # like 계열
    if name == "andLike":
        return f"AND {a(0)} LIKE '%{a(1)}%'"
    if name == "andLikeL":
        return f"AND {a(0)} LIKE '%{a(1)}'"
    if name == "andLikeR":
        return f"AND {a(0)} LIKE '{a(1)}%'"
    if name == "orLike":
        return f"OR {a(0)} LIKE '%{a(1)}%'"
    if name == "orLikeL":
        return f"OR {a(0)} LIKE '%{a(1)}'"
    if name == "orLikeR":
        return f"OR {a(0)} LIKE '{a(1)}%'"

    # in 계열
    if name == "andIn":
        return f"AND {a(0)} IN ({a(1)})"
    if name == "andNotIn":
        return f"AND {a(0)} NOT IN ({a(1)})"
    if name == "orIn":
        return f"OR {a(0)} IN ({a(1)})"
    if name == "orNotIn":
        return f"OR {a(0)} NOT IN ({a(1)})"

    # date range 계열
    if name == "andDateRange":
        return f"AND {a(0)} >= {a(1)} AND {a(0)} < {a(2)}"
    if name == "orDateRange":
        return f"OR {a(0)} >= {a(1)} OR {a(0)} < {a(2)}"

    return None  # 알 수 없는 메서드 → 변환하지 않음


def process_line(line):
    stripped = line.strip()

    if stripped.startswith("pwm"):
        # 제거(언랩): pwm.메서드(...) → SQL 재조립
        parsed = _parse_call(stripped)
        if parsed is None:
            return line  # pwm.* 호출 형태가 아니면 원본 유지
        name, raw_args, trailing = parsed
        content = _to_sql(name, raw_args)
        if content is None:
            return line  # 매핑에 없는 메서드는 원본 유지

        trailing = trailing.strip()
        if trailing.startswith(";"):
            trailing = trailing[1:].strip()

        # 뒤에 자바 주석(//)이 있으면 SQL 주석(--)으로 변환
        if trailing.startswith("//"):
            return f"{content} -- {trailing[2:].strip()}"
        return content
    else:
        # 감싸기(랩): SQL → pwm.appendWithCR(...). SQL 주석(--)은 자바 주석(//)으로 빼냄
        idx = stripped.find("--")
        if idx != -1:
            content = stripped[:idx].strip()
            comment = stripped[idx + 2:].strip()
            return f'pwm.appendWithCR(" {content} "); // {comment}'
        return f'pwm.appendWithCR(" {stripped} ");'


if __name__ == "__main__":
    # 클립보드에서 내용을 가져옵니다.
    clipboard_content = pyperclip.paste()

    # 내용을 줄 단위로 분리합니다.
    lines = clipboard_content.splitlines()

    # 각 줄에 처리 적용
    modified_lines = [process_line(line) for line in lines]

    # 수정된 내용을 다시 하나의 문자열로 결합합니다.
    modified_content = "\n".join(modified_lines)

    # 변환된 내용을 클립보드에 다시 설정합니다.
    pyperclip.copy(modified_content)

    print("처리된 내용이 클립보드에 복사되었습니다:")
    print(modified_content)
