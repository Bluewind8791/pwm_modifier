import pyperclip

# 클립보드에서 내용을 가져옵니다.
clipboard_content = pyperclip.paste()

# 제거할 앞 문자열과 뒤 문자열 정의
prefixes_to_remove = ['pwm.appendWithCR("', 'pwm.appendWithParam("']
suffix_to_remove = '");'

# 내용을 줄 단위로 분리합니다.
lines = clipboard_content.splitlines()

# 각 줄을 처리하는 함수 정의
def process_line(line, prefixes, suffix):
    stripped_line = line.strip()

    if stripped_line.startswith("pwm"):
        # pwm으로 시작하면 제거: 앞 prefix 제거 후 ");" 위치에서 내용/뒤 분리
        for prefix in prefixes:
            if stripped_line.startswith(prefix):
                stripped_line = stripped_line[len(prefix):]
                break  # 가장 먼저 매칭된 prefix만 제거

        idx = stripped_line.find(suffix)  # 닫는 "); 위치
        if idx != -1:
            content = stripped_line[:idx].strip()
            trailing = stripped_line[idx + len(suffix):].strip()  # "); 뒤쪽
        else:
            content = stripped_line.strip()
            trailing = ""

        # 뒤에 자바 주석(//)이 있으면 SQL 주석(--)으로 변환
        if trailing.startswith("//"):
            comment = trailing[2:].strip()
            return f"{content} -- {comment}"
        return content
    else:
        # pwm으로 시작하지 않으면 감싸기: SQL 주석(--)은 자바 주석(//)으로 빼냄
        idx = stripped_line.find("--")
        if idx != -1:
            content = stripped_line[:idx].strip()
            comment = stripped_line[idx + 2:].strip()
            return f'pwm.appendWithCR(" {content} "); // {comment}'
        return f'pwm.appendWithCR(" {stripped_line} ");'

# 각 줄에 처리 적용
modified_lines = [process_line(line, prefixes_to_remove, suffix_to_remove) for line in lines]

# 수정된 내용을 다시 하나의 문자열로 결합합니다.
modified_content = "\n".join(modified_lines)

# 변환된 내용을 클립보드에 다시 설정합니다.
pyperclip.copy(modified_content)

print("처리된 내용이 클립보드에 복사되었습니다:")
print(modified_content)
