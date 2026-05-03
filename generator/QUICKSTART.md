# Quick Start Guide

Get started generating lofi music tracks in 2 minutes!

## Option 1: Python Generator (Recommended)

Generates tracks directly using the trained ML models.

### Setup (First time only)

```bash
cd generator

# Install Python dependencies
pip install torch
pip install -r requirements.txt
```

### Generate Tracks

```bash
# Generate 1 random track
python src/generator.py --random 1

# Generate 5 random tracks
python src/generator.py --random 5

# Generate from lyrics
python src/generator.py --lyrics "rainy sad night"

# Check outputs
ls output/
```

**✓ Done!** Check `generator/output/` for your generated track parameters.

## Option 2: Node.js API Client

Generates tracks by calling the Flask server.

### Setup

```bash
cd generator

# Install dependencies
npm install

# Build TypeScript
npm run build

# Start server in another terminal
cd ../server
python app.py
```

### Generate Tracks

```bash
# Back in generator directory
npm run generate -- batch 5
npm run generate -- lyrics "happy sunny day"
npm run generate -- list
```

**✓ Done!** Check `generator/output/manifest.json` for your tracks.

## Using Windows

```bash
cd generator

# Using the helper script
.\generate.bat random 5
.\generate.bat lyrics "your lyrics here"
.\generate.bat server
```

## Using Linux/Mac

```bash
cd generator

# Make script executable
chmod +x generate.sh

# Run generator
./generate.sh random 5
./generate.sh lyrics "your lyrics here"
./generate.sh server
```

## Next Steps

### Synthesize Audio in Browser

1. Open `client/` and build the web app:
   ```bash
   cd ../client
   npm install
   npm run build
   ```

2. Open `client/dist/index.html` in a browser

3. Load your generated parameters:
   ```javascript
   // In browser console
   const params = await fetch('generator/output/lofi_*.json').then(r => r.json());
   window.loadParams(params.params);
   ```

4. The synthesizer will create the audio and you can download it!

### What You Get

Generated files in `generator/output/`:
- `*.json` - Musical parameters (key, mode, BPM, chords, melodies, energy, valence)
- `manifest.json` - Index of all generated tracks

### Example Generated Parameters

```json
{
  "title": "LoFi track in G ionian",
  "key": 8,
  "mode": 1,
  "bpm": 85,
  "energy": 0.45,
  "valence": 0.62,
  "chords": [1, 5, 6, 3, 4, 1, 4, 5],
  "melodies": [[4, 5, 6, 7], [1, 2, 3, 4], ...]
}
```

## Troubleshooting

### ImportError when running Python script
```bash
# Make sure you're in the Lofi root directory, then run:
python -m generator.src.generator --random 1
```

### Server not running
```bash
# Start it from the Lofi root directory:
python server/app.py
```

### Port already in use
```bash
# Use different port:
FLASK_PORT=5001 python server/app.py
```

## Tips

- **Batch generation**: Generate 50 tracks overnight and pick your favorites
- **Lyrics-based**: More deterministic, good for specific moods
- **Random**: Quick variety, explore the latent space
- **GPU**: Use `--device cuda` for 5-10x faster generation

## Full Documentation

See [README.md](./README.md) for complete documentation and all available options.

Happy generating! 🎶
