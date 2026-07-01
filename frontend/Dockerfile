# Берем Node.js-образ, чтобы собрать Vue-приложение.
FROM node:24-slim AS build

# Рабочая папка внутри контейнера frontend-сборки.
WORKDIR /app

# Копируем package.json и package-lock.json отдельно для кеширования npm install.
COPY package*.json ./

# Устанавливаем зависимости frontend-а.
RUN npm ci

# Копируем исходники Vue-приложения.
COPY . .

# Собираем production-версию frontend-а в папку dist.
RUN npm run build