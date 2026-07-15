# 설치 순서

## 1. ZIP 압축 해제

`lotto_pattern_lab_github_b.zip`을 압축 해제합니다.

압축을 풀었을 때 `index.html`, `data`, `scripts`, `.github`가 같은 최상위 폴더에 있어야 합니다.

## 2. 기존 저장소에 덮어쓰기

저장소:

`https://github.com/codekimmy/lotto-pattern-lab`

권장 방법은 GitHub Desktop 또는 Git 명령입니다.

```bash
git clone https://github.com/codekimmy/lotto-pattern-lab.git
cd lotto-pattern-lab
```

압축을 푼 파일 전체를 이 폴더에 복사한 뒤:

```bash
git add .
git commit -m "feat: add Google Sheets sync and Pages deployment"
git push
```

## 3. Pages 배포 방식을 변경

GitHub 저장소에서:

`Settings → Pages → Build and deployment → Source → GitHub Actions`

로 변경합니다.

## 4. 첫 수동 실행

`Actions → Sync Lotto Data and Deploy Pages → Run workflow`

를 누릅니다.

정상 실행되면 다음 단계가 모두 초록색으로 끝납니다.

1. Google Sheets 다운로드
2. CSV 검증
3. data 파일 자동 커밋
4. Pages artifact 생성
5. GitHub Pages 배포

## 5. 확인할 파일

저장소에서:

- `data/lotto_history.csv`
- `data/meta.json`

사이트에서:

- 최신 회차
- 데이터 원본 `GitHub 검증 CSV`
- 마지막 동기화 시각

을 확인합니다.

## 연결된 Google Sheets

- Spreadsheet ID: `1w1AZshic7KGnbb0lqjfg_aUx5F9RzGBtJykFJuaP-lM`
- gid: `0`
- CSV endpoint: `https://docs.google.com/spreadsheets/d/1w1AZshic7KGnbb0lqjfg_aUx5F9RzGBtJykFJuaP-lM/export?format=csv&gid=0`

시트 URL은 워크플로에 이미 입력되어 있으므로 Repository Variable이나 Secret 등록은 필요 없습니다.
