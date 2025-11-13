# Frontend Dockerfile para EvoLL Coach Generic
FROM node:18-alpine as build

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm install --legacy-peer-deps

# Copiar el código fuente
COPY . .

# Build de la aplicación React
RUN npm run build

# Etapa de producción con nginx
FROM nginx:alpine

# Copiar el build al directorio de nginx
COPY --from=build /app/build /usr/share/nginx/html

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto 3000
EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
