# 나의 영어 단어장

GitHub Pages로 여는 개인 영어 단어장입니다. 단어는 이 저장소의 `data/words.json`에 저장돼요.

## 파일 구성
| 파일 | 역할 |
|---|---|
| `index.html` | 단어장 앱 (단어장 · 카드 · 퀴즈, 엑셀 가져오기/내보내기) |
| `data/words.json` | 단어 데이터 (앱이 GitHub API로 직접 고쳐서 커밋) |
| `manifest.webmanifest`, `icon-*.png` | 홈 화면 아이콘 |

## 처음 설정
1. 이 파일들을 **Public** 저장소에 올립니다. (무료 계정의 GitHub Pages는 Public 저장소만 지원해요)
2. 저장소 **Settings → Pages**: Source를 `Deploy from a branch`, 브랜치 `main` / `/ (root)`로 저장합니다.
3. 1~2분 뒤 `https://<아이디>.github.io/<저장소이름>/`에서 열립니다.
4. **토큰 만들기**: 프로필 **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**
   - Repository access: **Only select repositories** → 이 저장소만 선택
   - Permissions → Repository permissions → **Contents: Read and write**
5. 앱 오른쪽 위 **⚙**에서 토큰을 붙여 넣고 **저장하고 연결**을 누릅니다. 기기마다 한 번씩 해 주세요.

## 알아 둘 점
- 토큰은 그 기기의 브라우저에만 저장되고 저장소에는 올라가지 않아요. 기기를 잃어버렸다면 GitHub에서 토큰을 삭제하세요.
- 저장소가 Public이라 `words.json` 내용은 누구나 볼 수 있어요.
- 토큰이 없는 기기에서는 읽기 전용으로 열려요 (보기 · 카드 · 퀴즈만 가능).
- 단어를 추가·삭제할 때마다 커밋이 하나씩 생겨요. 두 기기에서 동시에 저장해도 서로의 변경을 덮어쓰지 않아요.
- 토큰이 만료되면 새로 만들어 ⚙에 다시 넣어 주세요.
