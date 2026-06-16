FROM node:20-alpine

WORKDIR /app

# Copia package.json e package-lock.json
COPY package*.json ./

# Instala dependências
RUN npm install

# Copia resto da aplicação
COPY . .

# Expõe porta 3000
EXPOSE 3000

# Comando para rodar em desenvolvimento
CMD ["npm", "start"]
