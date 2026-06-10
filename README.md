# pwm_modifier

클립보드의 내용을 **자바 `pwm` 구문**과 **일반 쿼리 텍스트** 사이에서 한 번에 토글해 주는 도구입니다.

## 동작

각 줄을 보고 자동으로 방향을 결정합니다.

- `pwm` 으로 **시작하는** 줄 → `pwm.appendWithCR(" {query} ");` 구문을 **제거**하여 쿼리만 남깁니다.
- `pwm` 으로 **시작하지 않는** 줄 → 앞뒤에 `pwm.appendWithCR(" ... ");` 구문을 **추가**합니다.

줄 끝 주석도 함께 변환됩니다. (`//` ↔ `--`)

### 예시

실행하면 두 방향으로 왕복합니다.

```
and a.file_size = 0 -- 저장시 깨진 파일 크기 0
        ↕ (pwm_modifier 실행)
pwm.appendWithCR(" and a.file_size = 0 "); // 저장시 깨진 파일 크기 0
```

## 사용법

1. 변환할 내용을 복사합니다. (클립보드에 담기)
2. `pwm_modifier.exe` 를 실행합니다.
3. 변환된 결과가 클립보드에 들어갑니다. 그대로 붙여넣으면 됩니다.

## 빌드

[uv](https://docs.astral.sh/uv/) 가 필요합니다.

```cmd
build.bat
```

의존성 설치(`uv sync`)부터 exe 생성(PyInstaller)까지 자동으로 처리되며, 결과물은 `dist\pwm_modifier.exe` 에 만들어집니다.
