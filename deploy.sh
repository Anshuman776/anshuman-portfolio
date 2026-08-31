#!/bin/bash

# Production Deploy Script for Anshuman Maurya's Portfolio
# Usage: ./deploy.sh [start|stop|restart|logs|health|build]

set -e

COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="anshuman-portfolio"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "Docker and Docker Compose are installed"
}

# Check environment variables
check_env() {
    if [ ! -f ".env" ]; then
        log_error ".env file not found!"
        log_info "Creating .env from .env.example..."
        cp .env.example .env
        log_warning "Please edit .env with your configuration and run deploy.sh again"
        exit 1
    fi
    log_success ".env file found"
}

# Build Docker image
build() {
    log_info "Building Docker image..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    log_success "Docker image built successfully"
}

# Start services
start() {
    log_info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    sleep 2
    log_success "Services started"
    
    # Wait for health check
    log_info "Waiting for health checks..."
    sleep 5
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Portfolio app is healthy"
    else
        log_warning "Portfolio app health check failed. Check logs with: ./deploy.sh logs"
    fi
}

# Stop services
stop() {
    log_info "Stopping services..."
    docker-compose -f "$COMPOSE_FILE" down
    log_success "Services stopped"
}

# Restart services
restart() {
    log_info "Restarting services..."
    stop
    sleep 2
    start
}

# View logs
view_logs() {
    log_info "Showing logs (Press Ctrl+C to exit)..."
    docker-compose -f "$COMPOSE_FILE" logs -f
}

# Health check
health_check() {
    log_info "Running health checks..."
    
    # App health
    if curl -s http://localhost:8000/health > /dev/null; then
        log_success "Portfolio App: HEALTHY"
    else
        log_error "Portfolio App: UNHEALTHY"
        return 1
    fi
    
    # Container status
    docker-compose -f "$COMPOSE_FILE" ps
}

# Show usage
usage() {
    cat <<EOF
${BLUE}Anshuman's Portfolio - Production Deploy Script${NC}

Usage: ./deploy.sh [COMMAND]

Commands:
    start       - Start all services
    stop        - Stop all services
    restart     - Restart all services
    logs        - View live logs
    health      - Run health checks
    build       - Build Docker image
    status      - Show container status

Examples:
    ./deploy.sh start      # Start the portfolio
    ./deploy.sh logs       # View logs
    ./deploy.sh health     # Check health
    ./deploy.sh restart    # Restart services

Environment Variables:
    - Load from .env file
    - Copy from .env.example if .env doesn't exist

For detailed information, see: PRODUCTION_DEPLOYMENT.md

EOF
}

# Main script logic
main() {
    case "${1:-help}" in
        start)
            check_docker
            check_env
            start
            ;;
        stop)
            check_docker
            stop
            ;;
        restart)
            check_docker
            check_env
            restart
            ;;
        logs)
            check_docker
            view_logs
            ;;
        health)
            check_docker
            health_check
            ;;
        build)
            check_docker
            check_env
            build
            ;;
        status)
            check_docker
            docker-compose -f "$COMPOSE_FILE" ps
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: $1"
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
