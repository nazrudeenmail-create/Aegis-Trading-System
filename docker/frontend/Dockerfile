# Aegis Trading System — Frontend Dockerfile
#
# Base: node:20-alpine (minimal footprint)
# Mode: Development (npm run dev with --host for container access)
#
# Production notes (Phase 12):
#   - Use multi-stage build: npm run build → nginx serve dist/

FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files first (layer caching — npm install only re-runs if package*.json changes)
COPY package*.json ./

# Install all dependencies
RUN npm install

# Copy application source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run Vite dev server accessible from outside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
