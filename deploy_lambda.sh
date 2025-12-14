#!/bin/bash
# Lambda 배포 스크립트

echo "📦 Lambda 배포 패키지 생성 중..."

# 임시 디렉토리 생성
rm -rf lambda_package
mkdir lambda_package

# Python 패키지 설치 (boto3는 Lambda에 내장되어 있어서 제외)
# requirements.txt에서 boto3 줄을 뺀 임시 파일 생성
grep -v "boto3" requirements.txt > requirements_lambda.txt
pip install -r requirements_lambda.txt -t lambda_package/
rm requirements_lambda.txt

# 소스 코드 복사
cp lambda_function.py lambda_package/
cp auth_provider_aws.py lambda_package/
cp graph_client.py lambda_package/
cp email_processor.py lambda_package/
cp llm_service.py lambda_package/
cp config.py lambda_package/
# .env는 복사하지 않음 (환경변수로 설정해야 함)

# ZIP 파일 생성
cd lambda_package
zip -r ../lambda_function.zip .
cd ..

echo "✓ lambda_function.zip 생성 완료!"
echo ""
echo "다음 단계:"
echo "1. AWS Lambda 콘솔에서 함수 생성"
echo "2. lambda_function.zip 업로드"
echo "3. 환경 변수 설정:"
echo "   - CLIENT_ID"
echo "   - CLIENT_SECRET"
echo "   - TENANT_ID"
echo "   - GEMINI_API_KEY"
echo "4. API Gateway 연결"
