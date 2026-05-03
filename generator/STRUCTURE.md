# Generator Project Structure

```
generator/
├── output/                      # Generated tracks (auto-created)
│   ├── manifest.json           # Index of all tracks
│   ├── lofi_*.json             # Generated track parameters
│   └── (your generated files)
│
├── src/
│   ├── generator.py            # Python generator (ML models)
│   └── generator.ts            # Node.js generator (API client)
│
├── dist/                        # Compiled JavaScript (after npm run build)
│   ├── generator.js
│   ├── generator.d.ts
│   └── ...
│
├── package.json                 # Node.js dependencies
├── tsconfig.json                # TypeScript configuration
├── requirements.txt             # Python dependencies (torch, etc.)
│
├── generate.bat                 # Windows helper script
├── generate.sh                  # Linux/Mac helper script
│
├── README.md                    # Full documentation
├── QUICKSTART.md                # Quick start guide
├── STRUCTURE.md                 # This file
└── .gitignore                   # Git ignore rules
```

## File Descriptions

### Core Generators

**src/generator.py** - Python Generator
- Uses trained ML models directly
- `Lyrics2LoFi`: converts lyrics → musical parameters
- `LoFi2LoFi`: generates variations from latent vectors
- Saves outputs as JSON with metadata
- Command: `python src/generator.py [options]`

**src/generator.ts** - Node.js API Client
- Calls Flask server endpoints
- `/generate` - random track generation
- `/predict` - lyrics to parameters
- `/decode` - latent vector to parameters
- Command: `node dist/generator.js [command]`

### Configuration

**package.json**
- Node.js dependencies
- Scripts: build, generate, generate:single, generate:batch
- Dependencies: tone, @tonaljs/tonal, axios, pako

**tsconfig.json**
- TypeScript compiler options
- Target: ES2020, CommonJS modules
- Output: dist/ directory

**requirements.txt**
- Python dependencies
- PyTorch versions matching server requirements

### Helper Scripts

**generate.bat** (Windows)
```
generate.bat random 5          # Generate 5 random tracks
generate.bat lyrics "sad day"  # Generate from lyrics
generate.bat server            # Start Flask server
```

**generate.sh** (Linux/Mac)
```
./generate.sh random 5
./generate.sh lyrics "happy day"
./generate.sh batch 10         # Use API client
```

### Documentation

**README.md**
- Complete documentation
- All command options
- Architecture overview
- Troubleshooting guide
- API reference

**QUICKSTART.md**
- 2-minute setup
- Basic usage examples
- Common tasks
- Tips and tricks

**STRUCTURE.md** (this file)
- Project organization
- File descriptions
- Integration points

## Output Format

Each generated track produces a JSON file:

```json
{
  "id": "abc123",                    // Unique identifier
  "timestamp": "2024-01-15T...",    // Generation time
  "type": "api" | "direct",         // Generator type
  "params": {                         // Musical parameters
    "title": "LoFi in G major",
    "key": 8,                        // 1-12 (C to B)
    "mode": 1,                       // 1-7 (Ionian to Locrian)
    "bpm": 85,                       // 70-100
    "energy": 0.45,                  // 0-1 (less to very energetic)
    "valence": 0.62,                 // 0-1 (sad to cheerful)
    "chords": [1, 5, 6, 3, ...],    // Chord progression
    "melodies": [[4, 5, 6, ...], ...] // Melodic sequences
  },
  "filename": "lofi_2024-01-15T10-30-00_abc123"
}
```

## Integration Points

### With Client

The generated parameters can be used in the web client:

```typescript
// client/src/index.ts
import { Producer } from './producer';
import { Player } from './player';

const params = loadFromJson('generator/output/lofi_*.json');
const track = producer.produce(params);
player.addTrack(track);
player.play();
```

### With Server

The Flask server provides RESTful endpoints:

```bash
# Get random parameters
curl http://localhost:5000/generate

# Decode latent vector
curl "http://localhost:5000/decode?input=[1,5,6,...]"

# Generate from lyrics
curl "http://localhost:5000/predict?input=rainy%20day"
```

### With Models

Direct access to trained models:

```python
from model.lofi2lofi_model import Decoder
from model.lyrics2lofi_model import Lyrics2LofiModel

decoder = Decoder(device='cpu')
decoder.load_state_dict(torch.load('checkpoints/lofi2lofi_decoder.pth'))

latent = torch.randn(100)
output = decoder(latent)
```

## Workflow Examples

### Example 1: Generate 50 Tracks for Collection

```bash
cd generator
python src/generator.py --random 50
# Check output/manifest.json for all 50 tracks
```

### Example 2: Generate from User Lyrics

```bash
python src/generator.py --lyrics "morning sunrise hope"
# Creates output/lofi_lyrics_*.json
```

### Example 3: Batch API Generation

```bash
npm run build
npm run generate -- batch 20
# Uses API endpoints for network-based generation
```

### Example 4: Full Audio Synthesis

```bash
# 1. Generate parameters
python src/generator.py --random 1

# 2. Open client web app
cd ../client && npm run serve

# 3. Load parameters in browser
# 4. Synthesize using Tone.js
# 5. Download as MP3/WAV
```

## Adding Features

### New Generator Type

1. Add method to `ApiLoFiGenerator` class in `src/generator.ts`
2. Add command handling in `main()` function
3. Update README and QUICKSTART

### New Output Format

1. Modify `_save_output()` in `src/generator.py`
2. Add export functionality to `ApiLoFiGenerator`
3. Support additional audio file types

### Integration with Tools

```python
# Add support for SoX, FFmpeg, etc.
import subprocess

def export_wav(params, filename):
    # Synthesize with server
    # Export using external tool
    pass
```

## Performance Characteristics

| Operation | Time | Device |
|-----------|------|--------|
| Generate (Python) | 5-10s | CPU |
| Generate (Python) | 1-2s | GPU |
| Generate (API) | ~1s | Network |
| Synthesize (Tone.js) | ~10s | Browser |

## Maintenance

- Check `output/manifest.json` to see all generated tracks
- Delete old output files to save space
- Backup interesting tracks before cleanup
- Keep generated parameters for reference
- Update models from checkpoints as they improve

## Related Components

- **Client** (`../client/`) - Web interface, Tone.js synthesis
- **Server** (`../server/`) - Flask API, model serving
- **Models** (`../model/`) - PyTorch model definitions
- **Checkpoints** (`../checkpoints/`) - Pre-trained weights

See main [README.md](../README.md) for project-wide documentation.
