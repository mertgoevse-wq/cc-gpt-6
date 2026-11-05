# cc-gpt-6

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-65%20통과-brightgreen.svg)](tests/)

개인 도구: Chrome에서 **이미 로그인한 ChatGPT 세션**을 사용하여 Anthropic 호환 로컬 프록시를 노출함으로써 **Claude Code**를 실행합니다.

> ⚠️ **자신의 계정으로만 사용하세요.** ChatGPT 웹 UI 자동화는 OpenAI 서비스 약관을 위반할 수 있습니다. 이는 개인 연구 도구입니다.

## 🌐 언어

- [English](README.md)
- [Deutsch](README.de.md)
- [中文](README.zh.md)
- [Español](README.es.md)
- [Français](README.fr.md)
- [日本語](README.ja.md)
- [한국어](README.ko.md) (이 파일)

---

## 작동 원리

1. `cc-gpt-6 start`가 chatgpt.com에 대한 Chrome의 쿠키 저장소(Windows에서 DPAPI)를 읽고 세션 토큰을 자동으로 추출합니다.
2. `127.0.0.1:8787`에서 로컬 FastAPI 프록시를 시작하며, **Anthropic Messages API**를 구사하고 ChatGPT 백엔드로 전달합니다.
3. `claude`(Claude Code)를 `ANTHROPIC_BASE_URL`이 프록시를 가리키도록 실행하므로, Claude Code는 Anthropic과 통신한다고 생각합니다.
4. **GPT-6 / o3-mini / o1 / GPT-4o** 추론을 Claude Code 인터페이스를 통해 사용할 수 있습니다!

## ✨ 기능

- 🔐 **자동 토큰 추출** - Chrome 쿠키에서 (Windows DPAPI + AES-GCM)
- 🔄 **자동 재연결 및 토큰 갱신** - 401/403/만료 감지 시 쿠키 자동 재추출
- 🧠 **추론 노력 제어** - low/medium/high (ChatGPT의 reasoning_effort에 매핑)
- 🌍 **다국어 지원** - 영어, 독일어, 중국어, 스페인어, 프랑스어, 일본어, 한국어
- ⚙️ **영구 설정** - 언어, 모델, 추론 노력, 포트가 `~/.config/cc-gpt-6/`에 저장됨
- 🔌 **Anthropic API 호환** - Anthropic API 형식을 기대하는 모든 도구와 작동
- 📦 **모델 지원** - gpt-6, gpt-5.6, o3-mini, o1, gpt-4o

## 📋 요구 사항

- **Python 3.12+**
- **Google Chrome** (https://chatgpt.com에 로그인됨)
- **Claude Code** 설치됨 (`claude` 명령어가 PATH에 있음)
- **Windows** (DPAPI 쿠키 복호화용) - Linux/macOS 지원 예정

## 🚀 설치

```bash
# 저장소 복제
git clone https://github.com/yourusername/cc-gpt-6.git
cd cc-gpt-6

# 개발 모드로 설치
pip install -e .

# 또는 pipx 사용 (CLI 도구에 권장)
pipx install -e .
```

## 🎯 사용법

### 첫 실행 - 대화형 설정

```bash
cc-gpt-6 start
```

첫 실행 시 언어를 선택하라는 메시지가 표시됩니다:
```
cc-gpt-6에 오신 것을 환영합니다!

언어 선택 / Select your language / Wählen Sie Ihre Sprache:
  en: English *
  de: Deutsch
  zh: 中文
  es: Español
  fr: Français
  ja: 日本語
  ko: 한국어

Enter language code (e.g., en, de, zh): ko
```

### 명령어

| 명령어 | 설명 |
|--------|------|
| `cc-gpt-6 start` | 토큰 추출, 프록시 시작, Claude Code 실행 |
| `cc-gpt-6 start --no-claude` | 프록시만 시작 (Claude Code 실행 안 함) |
| `cc-gpt-6 proxy` | 프록시 서버만 실행 |
| `cc-gpt-6 extract-token` | 추출된 ChatGPT 세션 토큰 표시 |
| `cc-gpt-6 config` | 대화형 설정 |
| `cc-gpt-6 config --show` | 현재 설정 표시 |
| `cc-gpt-6 config --language ko` | 언어를 한국어로 설정 |
| `cc-gpt-6 config --model gpt-6` | 기본 모델 설정 |
| `cc-gpt-6 config --reasoning high` | 추론 노력 설정 |
| `cc-gpt-6 config --port 9999` | 프록시 포트 설정 |

### 워크플로 예시

```bash
# 1. Chrome에서 ChatGPT에 로그인되어 있는지 확인
# 2. cc-gpt-6 실행
cc-gpt-6 start

# 3. Claude Code가 시작되어 내 ChatGPT 세션에 연결됨!
#    이제 GPT-6 / o3-mini / o1 추론을 Claude Code로 사용 가능
```

### 수동 프록시 사용

```bash
# 터미널 1: 프록시 시작
cc-gpt-6 proxy

# 터미널 2: Anthropic 호환 도구로 사용
export ANTHROPIC_BASE_URL=http://127.0.0.1:8787
export ANTHROPIC_API_KEY=cc-gpt-6-dummy
claude  # 또는 다른 Anthropic API 클라이언트
```

## ⚙️ 설정

설정은 `~/.config/cc-gpt-6/config.json`에 저장됩니다:

```json
{
  "language": "ko",
  "model": "o3-mini",
  "reasoning_effort": "high",
  "port": 8787,
  "auto_launch_claude": true
}
```

### 지원 모델

| 모델 | 설명 |
|------|------|
| `gpt-6` | GPT-6 (사용 가능한 경우) |
| `gpt-5.6` | GPT-5.6 (사용 가능한 경우) |
| `o3-mini` | o3-mini 추론 모델 (기본값) |
| `o1` | o1 추론 모델 |
| `gpt-4o` | GPT-4o |

### 추론 노력 레벨

| 레벨 | 설명 |
|------|------|
| `low` | 빠름, 최소 추론 |
| `medium` | 균형 잡힌 추론 |
| `high` | 깊은 추론 (기본값) |

## 🔧 문제 해결

### "Chrome cookie database locked"
**모든** Chrome 창을 완전히 닫고 다시 시도하세요. Chrome 실행 중에는 쿠키 데이터베이스가 잠깁니다.

### "No active ChatGPT session found"
1. Chrome 열기
2. https://chatgpt.com 접속
3. 계정 로그인
4. `cc-gpt-6` 다시 실행

### "Claude Code not found"
Claude Code 설치: https://claude.ai/code

### 사용 중 토큰 만료
프록시에는 **자동 재연결 가디언**이 있어, 401/403/만료 세션 감지 시 Chrome에서 자동으로 쿠키를 재추출합니다. 계속 작업하세요!

## 🏗️ 아키텍처

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Claude     │────▶│  cc-gpt-6    │────▶│  ChatGPT        │
│  Code       │     │  Proxy       │     │  Backend API    │
│  (Anthropic │     │  :8787       │     │  (conversation) │
│   API)      │     │              │     │                 │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Chrome      │
                    │  Cookies     │
                    │  (DPAPI)     │
                    └──────────────┘
```

## ⚠️ 면책 조항

이는 **개인 연구 도구**입니다. 책임감 있게 사용하세요:
- 자신의 ChatGPT 계정으로만 사용
- OpenAI 서비스 약관 준수
- ChatGPT가 API를 변경하면 작동하지 않을 수 있음
- 보증이나 지원 없음

## 📄 라이선스

MIT 라이선스 - 자세한 내용은 [LICENSE](LICENSE) 참조.

## 🤝 기여

기여를 환영합니다! 다음 단계를 따라주세요:
1. 저장소 포크
2. 기능 브랜치 생성
3. 새 기능에 대한 테스트 추가
4. 모든 테스트 통과 확인 (`pytest tests/ -v`)
5. PR 제출

---

**AI 코딩 커뮤니티를 위해 ❤️ 로 제작**