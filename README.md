# pwm_modifier

클립보드의 내용을 **자바 `pwm` 구문**과 **일반 쿼리 텍스트** 사이에서 한 번에 토글해 주는 도구입니다.

## 동작

각 줄을 보고 자동으로 방향을 결정합니다.

- `pwm` 으로 **시작하는** 줄 → `pwm.*( ... );` 호출을 **제거(언랩)**하여 SQL 조건문만 남깁니다.
- `pwm` 으로 **시작하지 않는** 줄 → 앞뒤에 `pwm.appendWithCR(" ... ");` 구문을 **추가(랩)**합니다.

줄 끝 주석도 함께 변환됩니다. (`//` ↔ `--`)

### 제거(언랩) 지원 메서드

`appendWithCR` 뿐 아니라 `PreparedWhereMaker` 의 주요 조건 메서드를 인식해 SQL 로 재조립합니다.

| 메서드 | 변환 결과 |
| --- | --- |
| `appendWithCR` / `appendWithParam` / `appendFormat` | 첫 인자(SQL) 그대로 |
| `append` (1·4인자) | SQL 그대로 / `CAT_OP col OP val` |
| `andEqual` / `andNotEqual` / `orEqual` | `AND col = val` / `AND col <> val` / `OR col = val` |
| `and` / `or` (1·3인자) | `AND compStr` / `AND col OP val` |
| `andLike` / `andLikeL` / `andLikeR` (및 `or` 계열) | `AND col LIKE '%val%'` / `'%val'` / `'val%'` |
| `andIn` / `andNotIn` / `orIn` / `orNotIn` | `AND col IN (val)` / `AND col NOT IN (val)` 등 |
| `andDateRange` / `orDateRange` / `appendDateRange` | `AND col >= fr AND col < to` 등 |

- 인자 안의 따옴표·콤마·배열(`new String[]{...}`)이 있어도 안전하게 분리합니다.
- `andEqual(..., true)` 처럼 `isEssential` 인자는 무시합니다.
- 매핑에 없는 메서드나 `pwm.*` 호출 형태가 아닌 줄은 **원본을 그대로 둡니다.**

> 재조립 결과는 컬럼·연산자 구조를 보기 위한 것으로, 변수명(`userId` 등)은 그대로 남으므로 그 자체로 실행 가능한 SQL 은 아닙니다. 또한 어떤 메서드였는지 정보가 사라지므로 랩(추가) 방향은 항상 `appendWithCR` 로만 되돌아갑니다.

### 예시

실행하면 두 방향으로 왕복합니다.

```
and a.file_size = 0 -- 저장시 깨진 파일 크기 0
        ↕ (pwm_modifier 실행)
pwm.appendWithCR(" and a.file_size = 0 "); // 저장시 깨진 파일 크기 0
```

제거 방향은 다양한 메서드를 풀어냅니다.

```
pwm.andEqual("USER_ID", userId);          →  AND USER_ID = userId
pwm.andLike("NAME", name);                →  AND NAME LIKE '%name%'
pwm.andIn("CODE", codes);                 →  AND CODE IN (codes)
pwm.andDateRange("REG_DT", fr, to);       →  AND REG_DT >= fr AND REG_DT < to
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

의존성 설치(`uv sync`)부터 exe 생성(PyInstaller)까지 자동으로 처리됩니다. 빌드가 끝나면 결과물 `pwm_modifier.exe` 를 **프로젝트 루트로 이동**시키고, 빌드 과정에서 생긴 잔여 폴더(`build\`, `dist\`, `__pycache__\`)를 자동으로 정리합니다.
