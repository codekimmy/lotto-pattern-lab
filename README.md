# Lotto Pattern Lab

GitHub Pages site:

`https://codekimmy.github.io/lotto-pattern-lab/`

Google Sheets source:

`https://docs.google.com/spreadsheets/d/1w1AZshic7KGnbb0lqjfg_aUx5F9RzGBtJykFJuaP-lM/edit?gid=0#gid=0`

## Data pipeline

```text
Google Sheets
  → GitHub Actions
  → validation and normalized CSV
  → data/lotto_history.csv + data/meta.json
  → GitHub commit
  → GitHub Pages deployment
```

## Repository structure

```text
.
├─ index.html
├─ .nojekyll
├─ data/
│  ├─ lotto_history.csv
│  └─ meta.json
├─ scripts/
│  └─ sync_sheet.py
└─ .github/
   └─ workflows/
      └─ sync-and-deploy.yml
```

## Automatic schedule

The workflow runs in `Asia/Seoul` every Sunday at:

- 08:17
- 14:17

It can also be run manually from:

`Actions → Sync Lotto Data and Deploy Pages → Run workflow`

## Validation

The workflow rejects the update instead of overwriting the working data when:

- the header is not `draw,date,n1,n2,n3,n4,n5,n6,bonus`
- a draw is duplicated or missing
- a main number is duplicated or outside 1–45
- a bonus number is outside 1–45 or duplicates a main number
- the date format is invalid
- the downloaded latest draw goes backward

## Important GitHub Pages setting

Open:

`Settings → Pages → Build and deployment → Source`

Select:

`GitHub Actions`

Do not keep `Deploy from a branch`, because data commits made with `GITHUB_TOKEN`
do not trigger a separate Pages branch build.

## 본번호 6수 후속 추적 규칙

- 최신 회차: 본번호 6개만 사용
- 조합 생성: `6C3 = 20개`
- 과거 일치 검색: 과거 회차 본번호 6개만 사용
- 직후 회차 분석: 직후 회차 본번호 6개만 사용
- 보너스 번호: 이 예측 모듈과 순차 백테스트의 전 과정에서 제외

## 개선형 20조합 점수 모델 v0.8
- 보너스 번호 전 과정 제외
- 완전 교집합 대신 후속 출현률 점수
- 표본 수 sqrt(n) 신뢰도 가중치
- 최근 일치 반감기 100회 가중치
- 여러 조합 지지 수 추가 점수
- 표본 2·3·4회 × 최소 후속률 20·25·30%의 9개 설정 비교
- 앞 60% 개발, 중간 20% 모델 선택, 마지막 20% 최종시험

## 냉각 반등 10/50

- 예측 입력: 본번호 6개만 사용, 보너스 번호 제외
- 중기 구간: 최근 10회를 제외한 직전 40회
- 단기 구간: 가장 최근 10회
- 점수: `(직전 40회 출현 횟수 / 40) - (최근 10회 출현 횟수 / 10)`
- 동점 규칙: 직전 40회 출현 횟수 내림차순 → 전체 누적 출현 오름차순 → 번호 오름차순
- 상위 6개를 그림자 예측번호로 기록
- 매 회차 이전 50회만 사용하는 순차 검증 제공

## 모델 연구실 메뉴

- 내비게이션에 `모델 연구실` 메뉴를 추가했습니다.
- 1~15차 검증 흐름, 현재 주력·그림자·대조 모델의 포커스와 역할, 고정 운영 규칙, 공식 5세트를 정리했습니다.
- `research_results/` 폴더에 단계별 XLSX, 사전등록 Manifest, 현재 공식 세트 CSV를 포함했습니다.
- 모든 모델 설명과 채점은 본번호 6개 기준이며 보너스 번호는 제외합니다.
