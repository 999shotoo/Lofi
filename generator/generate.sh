#!/bin/bash

# LoFi Generator - Unix Helper Script

if [ $# -eq 0 ] || [ "$1" = "help" ]; then
    cat << EOF

LoFi Music Generator
Usage: ./generate.sh [command] [args]

Commands:
  random [count]      Generate N random tracks (default: 1)
  lyrics [text]       Generate track from lyrics
  batch [count]       Generate N tracks using API (default: 10)
  server              Start the Flask server
  help                Show this help

Output directory: ./output/

Examples:
  ./generate.sh random 5
  ./generate.sh lyrics "sad rainy day"
  ./generate.sh batch 20
  ./generate.sh server

EOF
    exit 0
fi

command=$1
shift

case $command in
    random)
        count=${1:-1}
        echo "Generating $count random tracks..."
        python src/generator.py --random "$count"
        ;;
    lyrics)
        lyrics="$@"
        if [ -z "$lyrics" ]; then
            echo "Please provide lyrics as arguments"
            exit 1
        fi
        echo "Generating from lyrics: $lyrics"
        python src/generator.py --lyrics "$lyrics"
        ;;
    batch)
        count=${1:-10}
        echo "Generating $count tracks via API..."
        npm run build > /dev/null 2>&1
        LOFI_SERVER_URL=http://localhost:5000 node dist/generator.js batch "$count"
        ;;
    server)
        echo "Starting Flask server..."
        cd ..
        python server/app.py
        ;;
    *)
        echo "Unknown command: $command"
        echo "Run './generate.sh help' for usage information"
        exit 1
        ;;
esac
