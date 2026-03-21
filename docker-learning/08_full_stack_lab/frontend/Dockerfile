# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
# ■ 파일명: Dockerfile
# ■ 목적: 프론트엔드 정적 파일을 Nginx로 서빙
# ■ 설명: 실제 React 빌드 대신 간단한 HTML을 Nginx로 제공
# ■ 빌드: docker build -t fullstack-frontend .
# ■ 날짜: 2026-03-21
# ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

# 간단한 정적 파일 서빙용 이미지
# 실제 프로젝트에서는 Node.js로 빌드 후 결과물만 복사해
FROM nginx:1.27-alpine

# 정적 파일 복사
COPY . /usr/share/nginx/html

# Nginx 포그라운드 실행
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
