#!/bin/bash

# Smart startup script for Divvy
# Automatically detects if local PostgreSQL is needed

# Change to the project root directory
cd "$(dirname "$0")/.." || exit 1

echo "🚀 Starting Divvy..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "📋 Copying .env.example to .env..."
    cp .env.example .env
    echo "✏️  Please edit .env with your configuration and run this script again."
    exit 1
fi

# Check if DATABASE_URL is set in .env (check for neon.tech or aws.neon.tech, with or without quotes)
if grep -E "^DATABASE_URL=.*neon\.tech" .env >/dev/null 2>&1; then
    echo "🌐 Using remote database (Neon detected)"
    echo "📦 Starting backend and frontend only..."
    docker compose up "$@"
elif grep -E "^DATABASE_URL=['\"]?postgresql://.+@.+" .env >/dev/null 2>&1; then
    # DATABASE_URL is set to some other remote database
    echo "🌐 Using remote database"
    echo "📦 Starting backend and frontend only..."
    docker compose up "$@"
else
    echo "💾 No remote database detected"
    echo "📦 Starting with local PostgreSQL database..."
    docker compose --profile local-db up "$@"
fi
