FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build assets
RUN npm run build

# Expose port
EXPOSE 3000

# Default command
CMD ["npm", "run", "dev"]
