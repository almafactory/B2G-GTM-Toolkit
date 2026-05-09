---
name: aiwf:spec-driven-development
description: Use when starting new features, building applications from scratch, or needing structured development workflow - provides standalone specification-first methodology without external dependencies, generates specs, plans, tasks directly, with superpowers integration for execution
---

# Spec-Driven Development (SDD) - Standalone

## Overview

**명세가 코드를 생성하는 개발 방법론.** 별도 설치 없이 Codex가 직접 워크플로우를 실행한다.

**핵심 원칙:** 명세(WHAT & WHY) → 계획(HOW) → 태스크(실행 단위) → 구현(코드)

## When to Use

**사용 시점:**
- 새 프로젝트/기능 개발 시작
- 체계적인 요구사항 관리 필요
- 외부 도구 설치 없이 SDD 적용

**사용하지 말 것:**
- 간단한 버그 수정, 한 줄 변경

## Quick Reference

| 단계 | 명령 | 출력 |
|------|------|------|
| 1. 명세 | "specify: [기능 설명]" | `.sdd/specs/NNN-feature/spec.md` |
| 2. 계획 | "plan: [기술 스택]" | `plan.md`, `data-model.md` |
| 3. 태스크 | "tasks" | `tasks.md` |
| 4. 구현 | "implement" | 소스 코드 |

## Core Workflow

사용자가 다음 키워드로 요청하면 해당 단계를 실행한다:

```
"specify: 사진 앨범 정리 앱" → 명세 생성
"plan: React + SQLite"      → 계획 생성
"tasks"                     → 태스크 분해
"implement"                 → 구현 실행
```

## Phase 1: Specify (명세 작성)

**트리거:** `specify:` 또는 "명세 작성", "기능 정의"

### 실행 절차

1. `.sdd/specs/` 디렉토리 확인/생성
2. 기존 specs 스캔하여 다음 번호 결정 (001, 002, ...)
3. 기능명에서 branch-name 생성 (예: "photo-albums")
4. 디렉토리 생성: `.sdd/specs/NNN-feature-name/`
5. `spec.md` 작성 (템플릿 참조: @templates/spec-template.md)

### 핵심 규칙

- **WHAT(무엇)과 WHY(왜)만** 기술
- **HOW(어떻게)는 금지** - 기술 스택, API 구조, 구현 방식 언급 안함
- 각 User Story는 **독립적으로 테스트 가능**해야 함
- **우선순위 필수**: P1(핵심) → P2 → P3...

### 출력 구조

```
.sdd/specs/001-photo-albums/
├── spec.md           # 기능 명세
└── checklists/
    └── requirements.md
```

### spec.md 필수 섹션

```markdown
# Feature Specification: [기능명]

## User Scenarios & Testing
### User Story 1 - [제목] (Priority: P1)
- 설명, 우선순위 이유
- Independent Test: 독립 테스트 방법
- Acceptance Scenarios: Given-When-Then

## Requirements
### Functional Requirements
- FR-001: System MUST [구체적 기능]
- [NEEDS CLARIFICATION: 불명확한 부분]

## Success Criteria
- SC-001: [측정 가능한 지표]
```

## Phase 2: Plan (계획 수립)

**트리거:** `plan:` 또는 "계획 수립", "기술 설계"

### 실행 절차

1. 현재 feature의 `spec.md` 읽기
2. 사용자 입력에서 기술 스택 추출
3. `plan.md` 작성 (템플릿 참조: @templates/plan-template.md)
4. `data-model.md` 생성 (엔티티, 관계)
5. `contracts/` 디렉토리에 API 명세 (필요시)

### 출력 구조

```
.sdd/specs/001-photo-albums/
├── spec.md
├── plan.md           # 구현 계획
├── data-model.md     # 데이터 모델
├── research.md       # 기술 조사 (선택)
└── contracts/
    └── api-spec.json
```

### plan.md 필수 섹션

```markdown
# Implementation Plan: [기능명]

## Summary
[spec에서 추출한 요구사항 + 기술 접근법]

## Technical Context
- Language/Version: [예: Python 3.11]
- Primary Dependencies: [예: FastAPI]
- Storage: [예: SQLite]
- Testing: [예: pytest]

## Project Structure
src/
├── models/
├── services/
└── api/
tests/
└── ...
```

## Phase 3: Tasks (태스크 분해)

**트리거:** `tasks` 또는 "태스크 생성", "작업 분해"

### 실행 절차

1. `spec.md`에서 User Stories 추출 (우선순위 포함)
2. `plan.md`에서 기술 구조 추출
3. `data-model.md`에서 엔티티 추출 (있으면)
4. User Story별로 태스크 그룹화
5. `tasks.md` 생성 (템플릿 참조: @templates/tasks-template.md)

### 태스크 형식

```markdown
- [ ] T001 프로젝트 구조 생성
- [ ] T002 [P] 의존성 설치
- [ ] T003 [P] [US1] User 모델 생성 in src/models/user.py
- [ ] T004 [US1] UserService 구현 in src/services/user.py
```

- `[P]`: 병렬 실행 가능
- `[US1]`: User Story 1 소속

### Phase 구조

```markdown
## Phase 1: Setup
## Phase 2: Foundational (모든 User Story 전제조건)
## Phase 3: User Story 1 (P1) 🎯 MVP
## Phase 4: User Story 2 (P2)
## Phase N: Polish & Cross-Cutting
```

## Phase 4: Implement (구현)

**트리거:** `implement` 또는 "구현 시작"

### 실행 절차

1. `tasks.md` 읽기
2. Phase 순서대로 실행
3. 각 태스크 완료 시 `[X]`로 표시
4. 체크포인트에서 검증

## Superpowers 연동

### tasks.md → Superpowers Plan 변환

`tasks` 단계 완료 후 다음 옵션 제시:

```
✅ tasks.md가 생성되었습니다.

다음 단계를 선택하세요:
┌─────────────────────────────────────────────────────────────┐
│ A) 직접 구현 시작 (implement)                               │
│ B) Superpowers Plan으로 변환 후 /execute-plan 실행 (권장)   │
│ C) 계획만 저장하고 나중에 실행                               │
└─────────────────────────────────────────────────────────────┘
```

### B 선택 시 변환

`docs/plans/YYYY-MM-DD-feature-implementation.md` 생성:

```markdown
# Implementation Plan: [Feature Name]

## Overview
[spec.md에서 추출한 기능 요약]

## Tasks

### Batch 1: Setup
- [ ] T001: 프로젝트 구조 생성
- [ ] T002: 의존성 설치

### Batch 2: Core (User Story 1)
- [ ] T003: [P] User 모델 생성
- [ ] T004: UserService 구현

## Review Checkpoints
- Batch 1 완료 후: 프로젝트 빌드 확인
- Batch 2 완료 후: US1 독립 테스트 통과 확인
```

그 후 안내:
```
📋 Superpowers plan이 생성되었습니다:
   docs/plans/YYYY-MM-DD-feature-implementation.md

실행하려면: /superpowers:execute-plan
```

## Directory Structure

```
project/
├── .sdd/                     # SDD 워킹 디렉토리
│   └── specs/
│       └── 001-feature/
│           ├── spec.md
│           ├── plan.md
│           ├── tasks.md
│           ├── data-model.md
│           └── contracts/
├── docs/plans/               # Superpowers plans
├── src/                      # 소스 코드
└── tests/                    # 테스트
```

## Common Mistakes

| 실수 | 해결책 |
|------|--------|
| specify에 기술 언급 | WHAT/WHY만, 기술은 plan에서 |
| User Story 독립성 없음 | 각 Story는 단독 테스트 가능해야 |
| tasks 없이 implement | 반드시 tasks → implement 순서 |
| 우선순위 없는 Story | P1, P2, P3 필수 지정 |

## Integration Workflow

### Superpowers와 함께 사용 (권장)

```
1. /superpowers:brainstorm   →  아이디어 정제
           ↓
2. specify: [기능 설명]      →  명세 작성
           ↓
3. plan: [기술 스택]         →  계획 수립
           ↓
4. tasks (→ B 선택)          →  Superpowers plan 변환
           ↓
5. /superpowers:execute-plan →  배치별 실행 + 리뷰
```

## File References

템플릿 파일 (필요시 참조):
- @templates/spec-template.md
- @templates/plan-template.md
- @templates/tasks-template.md
