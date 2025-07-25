# Standard Cube.js Dockerfile with golden versions (avoid Alpine for native extensions)
FROM node:18

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code and schema
COPY . .

# Expose standard Cube.js port
EXPOSE 4000

# Use standard Cube.js dev server
CMD ["npm", "run", "dev"]