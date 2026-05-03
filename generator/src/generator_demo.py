#!/usr/bin/env python3
"""
LoFi Music Generator Script - Test/Demo Version
Generates lofi music tracks with mock data (for testing without model dependencies)
"""

import os
import sys
import json
import argparse
import random
from pathlib import Path
from datetime import datetime
from typing import Optional

class LoFiGenerator:
    def __init__(self, device: str = "cpu"):
        self.device = device
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        print(f"✓ Generator initialized (device: {device})")
        print(f"✓ Output directory: {self.output_dir}")
    
    def generate_random_params(self) -> dict:
        """Generate random musical parameters"""
        # Random values for musical parameters
        key = random.randint(1, 12)  # C to B
        mode = random.randint(1, 7)   # Ionian to Locrian
        bpm = random.choice([70, 75, 80, 85, 90, 95, 100])
        energy = round(random.random(), 2)
        valence = round(random.random(), 2)
        
        # Generate chord progression (8 chords)
        chords = [random.randint(1, 7) for _ in range(8)]
        
        # Generate melodies (4 melodies with 8 notes each)
        melodies = [[random.randint(1, 7) for _ in range(8)] for _ in range(4)]
        
        return {
            "key": key,
            "mode": mode,
            "bpm": bpm,
            "energy": energy,
            "valence": valence,
            "chords": chords,
            "melodies": melodies
        }
    
    def generate_from_lyrics(self, lyrics: str, filename: Optional[str] = None) -> dict:
        """
        Generate a lofi track from lyrics
        (For demo, uses deterministic seed based on lyrics)
        """
        print(f"\nGenerating track from lyrics...")
        print(f"Lyrics: {lyrics[:100]}...")
        
        # Use lyrics as seed for reproducible output
        seed = sum(ord(c) for c in lyrics)
        random.seed(seed)
        params = self.generate_random_params()
        random.seed()  # Reset seed
        
        params["title"] = lyrics[:50]
        
        metadata = {
            "type": "lyrics2lofi",
            "lyrics": lyrics,
            "output_params": params,
            "timestamp": datetime.now().isoformat()
        }
        
        if filename is None:
            filename = f"lofi_lyrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self._save_output(metadata, filename)
        return metadata
    
    def generate_from_latent(self, latent_vector: list, filename: Optional[str] = None) -> dict:
        """Generate a lofi track from a latent vector"""
        print(f"\nGenerating track variation from latent vector...")
        
        if len(latent_vector) != 100:
            raise ValueError(f"Latent vector must have 100 dimensions, got {len(latent_vector)}")
        
        # Use latent vector to seed generation
        seed = int(sum(abs(x) * 1000 for x in latent_vector[:10]))
        random.seed(seed)
        params = self.generate_random_params()
        random.seed()
        
        metadata = {
            "type": "lofi2lofi",
            "latent_vector": latent_vector,
            "output_params": params,
            "timestamp": datetime.now().isoformat()
        }
        
        if filename is None:
            filename = f"lofi_latent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self._save_output(metadata, filename)
        return metadata
    
    def generate_random(self, count: int = 1) -> list:
        """Generate multiple random lofi tracks"""
        results = []
        for i in range(count):
            print(f"\nGenerating random track {i+1}/{count}...")
            params = self.generate_random_params()
            
            metadata = {
                "type": "random",
                "output_params": params,
                "timestamp": datetime.now().isoformat()
            }
            
            filename = f"lofi_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}"
            self._save_output(metadata, filename)
            results.append(metadata)
        
        return results
    
    def _save_output(self, metadata: dict, filename: str):
        """Save generated metadata to JSON file"""
        safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '_', '-')).rstrip()
        
        output_path = self.output_dir / f"{safe_filename}.json"
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Saved to {output_path}")
        
        # Also save to manifest
        self._update_manifest(metadata, safe_filename)
    
    def _update_manifest(self, metadata: dict, filename: str):
        """Update the manifest file"""
        manifest_path = self.output_dir / "manifest.json"
        
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        else:
            manifest = {"tracks": []}
        
        params = metadata.get("output_params", {})
        manifest["tracks"].append({
            "filename": filename,
            "timestamp": metadata.get("timestamp"),
            "type": metadata.get("type"),
            "key": params.get("key"),
            "mode": params.get("mode"),
            "bpm": params.get("bpm"),
            "energy": params.get("energy"),
            "valence": params.get("valence")
        })
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Generate lofi music tracks"
    )
    parser.add_argument(
        "--lyrics",
        type=str,
        help="Generate track from lyrics"
    )
    parser.add_argument(
        "--random",
        type=int,
        default=1,
        help="Generate N random tracks (default: 1)"
    )
    parser.add_argument(
        "--latent",
        type=str,
        help="Generate track from latent vector (comma-separated 100 values)"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device to use (cpu or cuda)"
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = LoFiGenerator(device=args.device)
    
    # Check if we have any generation request
    generated_any = False
    
    # Generate from lyrics
    if args.lyrics:
        generator.generate_from_lyrics(args.lyrics)
        generated_any = True
    
    # Generate from latent vector
    if args.latent:
        try:
            latent_vector = [float(x.strip()) for x in args.latent.split(",")]
            generator.generate_from_latent(latent_vector)
            generated_any = True
        except ValueError as e:
            print(f"Error parsing latent vector: {e}")
            return 1
    
    # Generate random tracks
    if not generated_any or args.random > 0:
        generator.generate_random(count=args.random)
    
    print(f"\n✓ Generation complete! Check {generator.output_dir} for outputs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
