#!/usr/bin/env python3
"""
LoFi Music Generator Script
Generates lofi music tracks using the existing ML models
"""

import os
import sys
import json
import argparse
import torch
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.lofi2lofi_generate import decode as lofi2lofi_decode
from server.lyrics2lofi_predict import predict as lyrics2lofi_predict
from model.lofi2lofi_model import Decoder as Lofi2LofiDecoder
from model.lyrics2lofi_model import Lyrics2LofiModel

class LoFiGenerator:
    def __init__(self, device: str = "cpu"):
        self.device = device
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize models
        print("Loading models...")
        self._load_models()
    
    def _load_models(self):
        """Load the lofi2lofi and lyrics2lofi models"""
        # LoFi2LoFi model
        lofi2lofi_checkpoint = Path(__file__).parent.parent / "checkpoints" / "lofi2lofi_decoder.pth"
        print(f"Loading lofi2lofi model from {lofi2lofi_checkpoint}...", end=" ")
        self.lofi2lofi_model = Lofi2LofiDecoder(device=self.device)
        
        if lofi2lofi_checkpoint.exists():
            self.lofi2lofi_model.load_state_dict(
                torch.load(lofi2lofi_checkpoint, map_location=self.device)
            )
            print("✓ Loaded")
        else:
            print(f"✗ Not found at {lofi2lofi_checkpoint}")
        
        self.lofi2lofi_model.to(self.device)
        self.lofi2lofi_model.eval()
        
        # Lyrics2LoFi model
        lyrics2lofi_checkpoint = Path(__file__).parent.parent / "checkpoints" / "lyrics2lofi.pth"
        print(f"Loading lyrics2lofi model from {lyrics2lofi_checkpoint}...", end=" ")
        self.lyrics2lofi_model = Lyrics2LofiModel(device=self.device)
        
        if lyrics2lofi_checkpoint.exists():
            self.lyrics2lofi_model.load_state_dict(
                torch.load(lyrics2lofi_checkpoint, map_location=self.device)
            )
            print("✓ Loaded")
        else:
            print(f"✗ Not found at {lyrics2lofi_checkpoint}")
        
        self.lyrics2lofi_model.to(self.device)
        self.lyrics2lofi_model.eval()
    
    def generate_from_lyrics(self, lyrics: str, filename: Optional[str] = None) -> dict:
        """
        Generate a lofi track from lyrics using the lyrics2lofi model
        
        Args:
            lyrics: The input lyrics text
            filename: Optional custom filename (without extension)
        
        Returns:
            Dictionary with generation metadata
        """
        print(f"\nGenerating track from lyrics...")
        print(f"Lyrics: {lyrics[:100]}...")
        
        # Get model output
        with torch.no_grad():
            output = lyrics2lofi_predict(self.lyrics2lofi_model, lyrics)
        
        # Create metadata
        metadata = {
            "type": "lyrics2lofi",
            "lyrics": lyrics,
            "output_params": output,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save metadata
        if filename is None:
            filename = f"lofi_lyrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self._save_output(metadata, filename)
        return metadata
    
    def generate_from_latent(self, latent_vector: list, filename: Optional[str] = None) -> dict:
        """
        Generate a lofi track variation from a latent vector using lofi2lofi model
        
        Args:
            latent_vector: List of 100 float values (latent space vector)
            filename: Optional custom filename (without extension)
        
        Returns:
            Dictionary with generation metadata
        """
        print(f"\nGenerating track variation from latent vector...")
        
        if len(latent_vector) != 100:
            raise ValueError(f"Latent vector must have 100 dimensions, got {len(latent_vector)}")
        
        # Get model output
        with torch.no_grad():
            latent_tensor = torch.tensor([latent_vector]).float().to(self.device)
            output = lofi2lofi_decode(self.lofi2lofi_model, latent_tensor)
        
        # Create metadata
        metadata = {
            "type": "lofi2lofi",
            "latent_vector": latent_vector,
            "output_params": output,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save metadata
        if filename is None:
            filename = f"lofi_latent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self._save_output(metadata, filename)
        return metadata
    
    def generate_random(self, count: int = 1) -> list:
        """
        Generate multiple random lofi tracks
        
        Args:
            count: Number of tracks to generate
        
        Returns:
            List of generation metadata dictionaries
        """
        results = []
        for i in range(count):
            print(f"\nGenerating random track {i+1}/{count}...")
            # Generate random latent vector
            latent_vector = torch.randn(100).tolist()
            metadata = self.generate_from_latent(latent_vector)
            results.append(metadata)
        
        return results
    
    def _save_output(self, metadata: dict, filename: str):
        """
        Save generated metadata to JSON file
        
        Args:
            metadata: The metadata dictionary
            filename: Base filename (without extension)
        """
        # Ensure filename is clean
        safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '_', '-')).rstrip()
        
        # Save as JSON
        output_path = self.output_dir / f"{safe_filename}.json"
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Saved to {output_path}")
        
        # Also save to a manifest
        self._update_manifest(metadata, safe_filename)
    
    def _update_manifest(self, metadata: dict, filename: str):
        """Update the manifest file with the new generation"""
        manifest_path = self.output_dir / "manifest.json"
        
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        else:
            manifest = {"tracks": []}
        
        # Add entry
        manifest["tracks"].append({
            "filename": filename,
            "timestamp": metadata.get("timestamp"),
            "type": metadata.get("type"),
            "title": metadata.get("output_params", {}).get("title", "Untitled")
        })
        
        # Save updated manifest
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Generate lofi music tracks using ML models"
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
