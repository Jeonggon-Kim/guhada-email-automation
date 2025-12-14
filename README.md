# K Glowing - Outlook Email Automation

Outlook 이메일을 자동으로 처리하여 Gemini API로 답변을 생성하고 임시보관함에 저장하는 시스템입니다.

## 🏗️ 아키텍처

### PoC (로컬 테스트)
```
Outlook Webhook → Flask (로컬) → Gemini API → Outlook Draft
```

### 프로덕션 (AWS Lambda)
```
Outlook Webhook → API Gateway → Lambda → Gemini API → Outlook Draft
                                    ↓
                                CloudWatch Logs
```

## 📋 프로젝트 구조

```
email_automation/
├── server.py              # Flask 서버 (PoC용)
├── lambda_function.py     # AWS Lambda 함수 (프로덕션용)
├── auth_provider.py       # Microsoft OAuth 인증
├── graph_client.py        # Microsoft Graph API 클라이언트
├── llm_service.py         # Gemini API 서비스
├── email_processor.py     # 이메일 처리 로직
├── setup_webhook.py       # 웹훅 구독 설정
├── config.py              # 설정 파일
├── requirements.txt       # Python 패키지
├── deploy_lambda.sh       # Lambda 배포 스크립트
└── .env                   # 환경 변수
```

---

## 🚀 Phase 1: PoC (로컬 테스트)

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 생성:

```env
# Microsoft Azure
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
TENANT_ID=common

# Webhook URL (ngrok)
WEBHOOK_URL=https://your-ngrok-url.ngrok.io
PORT=5000

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash

# User Email
USER_EMAIL=your_email@outlook.com
```

### 3. Azure App 등록

1. [Azure Portal](https://portal.azure.com) 접속
2. **Azure Active Directory** → **App registrations** → **New registration**
3. Redirect URI: `http://localhost:5000/auth/callback`
4. **API permissions** 추가:
   - `Mail.ReadWrite`
   - `Mail.Send`
   - `User.Read`
5. Client ID, Client Secret 복사

### 4. Gemini API 키 발급

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. **Create API Key** 클릭
3. API 키 복사하여 `.env`에 입력

### 5. ngrok 실행

```bash
ngrok http 5000
```

ngrok URL을 `.env`의 `WEBHOOK_URL`에 입력

### 6. 서버 실행

```bash
python server.py
```

브라우저에서 `http://localhost:5000` 접속하여 로그인

### 7. 웹훅 구독

```bash
python setup_webhook.py
```

### 8. 테스트

Outlook으로 이메일을 받으면 자동으로 답장 임시보관함이 생성됩니다!

---

## 🚀 Phase 2: 프로덕션 (AWS Lambda)

### 1. Lambda 배포 패키지 생성

```bash
bash deploy_lambda.sh
```

### 2. AWS Lambda 함수 생성

1. [AWS Lambda Console](https://console.aws.amazon.com/lambda) 접속
2. **Create function** 클릭
3. 설정:
   - Runtime: Python 3.11
   - Architecture: x86_64
   - Timeout: 60초
   - Memory: 512MB

### 3. 코드 업로드

`lambda_function.zip` 파일을 Lambda에 업로드

### 4. 환경 변수 설정

Lambda 함수의 **Configuration** → **Environment variables**:

```
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
TENANT_ID=common
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
```

### 5. API Gateway 생성

1. **API Gateway** 콘솔 접속
2. **HTTP API** 생성
3. Integration: Lambda 함수 선택
4. Routes:
   - `POST /webhook`
   - `GET /webhook` (validation용)
5. Deploy

### 6. 웹훅 URL 업데이트

API Gateway URL을 복사하여 `setup_webhook.py`에서 사용:

```python
WEBHOOK_URL = "https://your-api-gateway-url/webhook"
```

### 7. 웹훅 구독 생성

```bash
python setup_webhook.py
```

---

## 💰 비용 예상 (프로덕션)

### AWS Lambda
- **무료 티어**: 월 100만 요청, 40만 GB-초
- **예상**: 하루 1000개 이메일 = 월 30,000 요청 → **무료**

### API Gateway
- **무료 티어**: 월 100만 요청
- **예상**: 월 30,000 요청 → **무료**

### Google Gemini API
- **gemini-1.5-flash**: 무료 티어 (분당 15 요청)
- **초과 시**: $0.075 / 1M tokens (입력), $0.30 / 1M tokens (출력)
- **예상**: 하루 1000개 × 30일 = 월 30,000개
  - 이메일당 평균 500 tokens → **무료 또는 월 $5 이하**

### CloudWatch Logs
- **무료 티어**: 5GB
- **예상**: 월 1GB 미만 → **무료**

**총 예상 비용: 월 $0 ~ $5** ✅

---

## 📊 모니터링

### CloudWatch Logs 확인

```bash
# AWS CLI로 로그 확인
aws logs tail /aws/lambda/your-function-name --follow
```

### 로그 검색

Lambda 함수는 다음 형식으로 로그를 남깁니다:

```
✓ Webhook validation request
📧 New email: message_id
From: sender@example.com | Subject: Test
✓ Draft created: draft_id
```

---

## 🔧 문제 해결

### 웹훅이 작동하지 않음
- API Gateway URL이 올바른지 확인
- Lambda 함수가 실행되는지 CloudWatch 확인
- 웹훅 구독이 만료되지 않았는지 확인 (3일마다 갱신)

### Gemini API 오류
- API 키가 유효한지 확인
- 무료 티어 제한(분당 15 요청)을 초과하지 않았는지 확인

### Microsoft Graph API 오류
- Client ID/Secret이 올바른지 확인
- API 권한이 부여되었는지 확인

---

## 🎯 다음 단계 (선택사항)

### 1. 이메일 필터링
특정 발신자나 제목만 처리하도록 필터 추가

### 2. 자동 발송
임시보관함 대신 바로 발송하는 옵션 추가

### 3. 다국어 지원
Gemini에게 언어 감지 및 해당 언어로 답장 생성 요청

### 4. 대시보드
처리된 이메일 통계를 보여주는 웹 대시보드 추가

---

## 📝 라이선스

MIT License

---

## 🤝 지원

문제가 있으시면 이슈를 등록해주세요!
