FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install --production=false

# Copy source files
COPY . .

# Create public directory if it doesn't exist
RUN mkdir -p public

# Set build-time variables
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production
ENV NEXT_PUBLIC_API_URL=http://localhost:8000

# Build application
RUN npm run build

# Start the application
CMD ["npm", "start"]