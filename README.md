# BE
⚙️ BackEnd 코드 리펙토링을 위한 레포지토리
> 기존 레포지토리 링크 -> https://github.com/iamjunhyeong/KGU-Digital-Assistant-BE

## ⚒️ Refactoring
<img width="410" height="470" alt="image" src="https://github.com/user-attachments/assets/8d9a36cc-de80-4f13-b126-b71cc92d8d97" />

- 관심사 분리 (Separation of Concerns)

- 의존성 역전 (Dependency Inversion)
  → 예: application은 infra에 의존하지 않음.

- 확장성과 테스트 용이성 증가

- 도메인 중심 개발 + 계층 분리 (interface / application / domain / infra)




## 🌊Flow
![누메이트_시퀀스다이어그램rev0](https://github.com/user-attachments/assets/086a3718-eaeb-4635-a5bf-7d1fa15cee16)

## Poster
![image](https://github.com/user-attachments/assets/bf1ec2f0-556a-4207-badd-cfb43b277d1a)

## 🤝 Commit Convention

| 머릿말           | 설명                                                                      |
| ---------------- | ------------------------------------------------------------------------- |
| feat             | 새로운 기능 추가                                                          |
| fix              | 버그 수정                                                                 |
| design           | CSS 등 사용자 UI 디자인 변경                                              |
| !BREAKING CHANGE | 커다란 API 변경의 경우                                                    |
| !HOTFIX          | 코드 포맷 변경, 세미 콜론 누락, 코드 수정이 없는 경우                     |
| refactor         | 프로덕션 코드 리팩토링업                                                  |
| comment          | 필요한 주석 추가 및 변경                                                  |
| docs             | 문서 수정                                                                 |
| test             | 테스트 추가, 테스트 리팩토링(프로덕션 코드 변경 X)                        |
| setting          | 패키지 설치, 개발 설정                                                    |
| chore            | 빌드 테스트 업데이트, 패키지 매니저를 설정하는 경우(프로덕션 코드 변경 X) |
| rename           | 파일 혹은 폴더명을 수정하거나 옮기는 작업만인 경우                        |
| remove           | 파일을 삭제하는 작업만 수행한 경우                                        |


### 🤝 Commit Convention Detail
<div markdown="1">

- `<타입>`: `<제목> (<이슈번호>)` 의 형식으로 제목을 아래 공백줄에 작성
- 제목은 50자 이내 / 변경사항이 "무엇"인지 명확히 작성 / 끝에 마침표 금지
- 예) Feat: 로그인 기능 구현 (#5)


</div>
