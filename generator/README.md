# LoFi Music Generator

Generate lofi music tracks programmatically using the trained ML models or the server API.

## Overview

This generator provides two approaches:

1. **Python Generator** (`src/generator.py`) - Directly uses the trained ML models
2. **Node.js API Client** (`src/generator.ts`) - Calls the Flask server API

## Setup

### Prerequisites

- Node.js 14+ (for Node.js generator)
- Python 3.8+ (for Python generator)
- PyTorch

### Installation

```bash
# Install Node.js dependencies
npm install

# Compile TypeScript (for Node.js generator)
npm run build

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

### Python Generator (Direct Model Access)

Generate tracks directly using the ML models:

```bash
# Generate a single random track
python src/generator.py --random 1

# Generate 5 random tracks
python src/generator.py --random 5

# Generate from lyrics
python src/generator.py --lyrics "rainy day in the city"

# Generate from latent vector (100 comma-separated values)
python src/generator.py --latent "0.5,0.3,0.1,..."

# Use GPU (if available)
python src/generator.py --device cuda --random 10
```

### Node.js API Client

Generate tracks by calling the Flask server API:

```bash
# Make sure server is running first
python ../server/app.py

# Generate a single random track
npm run generate

# Generate 10 random tracks
npm run generate -- batch 10

# Generate from lyrics
npm run generate -- lyrics "sad rainy day"

# Generate from latent vector
npm run generate -- decode "0.5,0.3,0.1,..."

# List all generated tracks
npm run generate -- list
```

### Environment Variables

```bash
# For Node.js generator
export LOFI_SERVER_URL=http://localhost:5000

# For Python generator
export DEVICE=cuda  # or 'cpu' (default)
```

## Output

Generated tracks are saved to the `output/` directory:

```
output/
├── manifest.json              # Index of all generated tracks
├── lofi_lyrics_*.json        # Generated from lyrics
├── lofi_latent_*.json        # Generated from latent vectors
└── lofi_*.json               # Random generation outputs
```

### Output File Format

Each JSON file contains:

```json
{
  "id": "abc123",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "type": "api",
  "params": {
    "title": "LoFi track in G ionian",
    "key": 8,
    "mode": 1,
    "bpm": 85,
    "energy": 0.45,
    "valence": 0.62,
    "chords": [1, 5, 6, 3, ...],
    "melodies": [[4, 5, 6, 7, ...], ...]
  },
  "filename": "lofi_2024-01-15T10-30-00_abc123"
}
```

## Architecture

### Python Generator Flow

1. Load pre-trained models from checkpoints
2. Generate latent vectors or get lyrics
3. Pass through Lyrics2LoFi or LoFi2LoFi models
4. Extract OutputParams with musical parameters
5. Save metadata to JSON files

### Node.js Generator Flow

1. Initialize API client pointing to Flask server
2. Call `/generate`, `/decode`, or `/predict` endpoints
3. Parse returned OutputParams
4. Save parameters and metadata to JSON files

## Using Generated Parameters

The output parameters can be used with the client to synthesize audio:

### In the Client

```typescript
import { Producer } from './producer';
import { Player } from './player';

// Load generated parameters
const params = JSON.parse(fs.readFileSync('output/lofi_*.json'));

// Produce track
const producer = new Producer();
const track = producer.produce(params.params);

// Play and record
const player = new Player();
player.addTrack(track);
player.play();
player.startRecording();
```

### Via API

```bash
# Get parameters then decode them
curl "http://localhost:5000/decode?input=[1,5,6,3,...]"
```

## Models Used

### Lyrics2LoFi
- Converts natural language lyrics into musical parameters
- Model: `checkpoints/lyrics2lofi.pth`
- Input: Text string (lyrics)
- Output: OutputParams (key, mode, bpm, chords, melodies, etc.)

### LoFi2LoFi (Decoder)
- Generates variations from a latent vector
- Model: `checkpoints/lofi2lofi_decoder.pth`
- Input: 100-dimensional latent vector
- Output: OutputParams

## Troubleshooting

### Python Generator Issues

```
ImportError: No module named 'server'
→ Run generator from the Lofi root directory, not from generator/src

ModuleNotFoundError: No module named 'torch'
→ pip install torch torchvision torchaudio

FileNotFoundError: checkpoints/lofi2lofi_decoder.pth
→ Make sure checkpoints are in the root Lofi/checkpoints directory
```

### Node.js Generator Issues

```
Server not running at http://localhost:5000
→ Start the server: cd ../server && python app.py

Connection refused
→ Check server is running and accessible at the configured URL

CORS errors
→ Server should have CORS headers, check Flask app.py
```

## Integration Examples

### Generate and Synthesize

```bash
# Generate parameters
python src/generator.py --random 5

# Use the parameters in client to synthesize
# (Open client/dist/index.html and load the generated params)
```

### Batch Generation Pipeline

```bash
#!/bin/bash
# Generate 100 random tracks
python generator/src/generator.py --random 100

# Process them with client (via browser automation)
# Or send to further processing pipeline
```

## Performance

- **Python Generator**: ~5-10 seconds per track (CPU), ~1-2 seconds (GPU)
- **Node.js Generator**: ~1 second per track (API call + JSON serialization)

## API Reference

### Python Generator Methods

- `generate_random(count)` - Generate N random tracks
- `generate_from_lyrics(lyrics)` - Generate from text
- `generate_from_latent(vector)` - Generate from latent vector

### Node.js Generator Methods

- `generateRandom()` - Generate a random track
- `generateBatch(count)` - Generate N tracks
- `predictFromLyrics(lyrics)` - Generate from lyrics
- `decodeLatent(vector)` - Generate from latent vector
- `listGenerated()` - List all previously generated tracks

## Related Files

- `../client/` - Web client for synthesis and playback
- `../server/` - Flask API server
- `../model/` - ML model definitions and training scripts
- `output/` - Generated track parameters and metadata

## Next Steps

1. Generate tracks with this tool
2. Load the JSON parameters into the client
3. Synthesize audio using Tone.js in the browser
4. Export as MP3/WAV using the browser recorder

Or use the server's model generation endpoints directly for headless audio synthesis.
