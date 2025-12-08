FROM node:20-alpine

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

# Expose Vite port
EXPOSE 5173

# Host 0.0.0.0 needed for Docker
CMD ["npm", "run", "dev", "--", "--host"]
