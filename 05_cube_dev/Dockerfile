FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . /app/05_cube_dev/

# Expose port
EXPOSE 4000

# Start Cube
CMD ["npm", "run", "dev"]
