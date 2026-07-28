# 타임라인 스케줄러 (Django 기반)

HTML5 Canvas를 사용한 드래그 앤 드롭 타임라인 스케줄러 애플리케이션입니다.

## 기능

- HTML5 Canvas를 사용한 수직 타임라인 표시
- 드래그 앤 드롭으로 일정 추가
- 시간 단위로 자동 스냅
- 다양한 길이의 일정 지원 (1시간, 2시간, 3시간)
- 과목 및 범위 관리 기능

## 설치 방법

1. Python 가상환경을 생성하고 활성화합니다:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 필요한 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

3. 데이터베이스 마이그레이션을 실행합니다:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 실행 방법

1. Django 개발 서버를 실행합니다:
```bash
python manage.py runserver 8000
```

2. 웹 브라우저에서 http://localhost:8000 에 접속합니다.