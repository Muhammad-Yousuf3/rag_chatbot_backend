# Dockerfile for RAG Chatbot Frontend
# T092 - Frontend container configuration for Docusaurus integration

FROM node:20-alpine

# Set work directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy application code
COPY . .

# Build for production (optional - can be skipped for development)
# RUN npm run build

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Run development server (use npm run build && npm run serve for production)
CMD ["npm", "run", "start"]
