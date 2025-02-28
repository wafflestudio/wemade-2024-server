# Getting started
```
git clone git@github.com:wafflestudio/wemade-2024-server.git
cd wemade-2024-server
```
이후 virtual environment 설정, dependency 설치 필요
```
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
아래 환경 변수, DB 및 초기 설정 먼저 수행 이후 서버 실행:

```
python manage.py runserver
```

## Environment variables:
- DB_HOST: PostgreSQL 서버 주소 (로컬에 설치했다면 localhost)
- DB_PASSWORD: DB 비밀번호
- DB_USER: DB 사용자명 (postgres)
- SECRET_KEY: (임의의 256B 이상의 문자열)
- DEBUG: 0 또는 1
- GOOGLE_OAUTH_CALLBACK_URL_BACKEND: http://localhost:8080/api/v1/auth/google/callback
- GOOGLE_OAUTH_CALLBACK_URL_DEV: https://(frontend dev url)/auth/callback
- GOOGLE_OAUTH_CALLBACK_URL_PROD: https://(frontend prod url)/auth/callback
- GOOGLE_OAUTH_CLIENT_ID: Google Cloud Console에서 API 및 서비스 -> Oauth 동의 화면 및 Oauth 2.0 클라이언트 ID 생성, 승인된 도메인에 backend 및 frontend url 추가, 승인된 리디렉션 URI에 위 callback url들을 추가
- GOOGLE_OAUTH_CLIENT_SECRET: 위 과정 수행하면 나오는 client secret

## DB 설정
PostgreSQL을 로컬 환경 또는 서버에 설치하고, wemade-2024-server-database 라는 데이터베이스를 생성, 이후 DB 구조 마이그레이션
```
psql -U postgres
CREATE DATABASE 'wemade-2024-server-database';
exit
python manage.py makemigrations
python manage.py migrate
```

## 초기 설정
personal_info 테이블에 회원가입 가능 유저인지 판단하기 위한 개인 정보가 필요

`fixture.json` 예시:
```
[
  {
    "model": "person.PersonalInfo",
    "pk": 1,
    "fields": {
      "name": "홍길동",
      "emails": [
        "gildong@wemade.com",
        ...
      ],
      "main_phone_number": "010-1234-5678",
      "birthday": "2004-01-01"
    }
  },
    ...
]
```
이후 fixture.json을 DB에 저장:
`python manage.py fixture.json`

참고사항: 서버에 처음 로그인하는 사용자는 마스터 권한을 기본적으로 가지고 있으므로 이를 이용해 최초 법인 및 hr팀 등록이 가능