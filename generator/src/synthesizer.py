#!/usr/bin/env python3
"""
LoFi Music Synthesizer - Generates MP3 from JSON parameters
Uses pydub and simpleaudio for audio synthesis
"""

import os
import sys
import json
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime

try:
    from pydub import AudioSegment
    from pydub.generators import Sine
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False
    print("Warning: pydub not installed. Install with: pip install pydub simpleaudio")

# Musical note frequencies
NOTES = {
    'C': 16.35, 'C#': 17.32, 'D': 18.35, 'D#': 19.45,
    'E': 20.60, 'F': 21.83, 'F#': 23.12, 'G': 24.50,
    'G#': 25.96, 'A': 27.50, 'A#': 29.14, 'B': 30.87
}

class LoFiSynthesizer:
    def __init__(self):
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        if not HAS_PYDUB:
            print("ERROR: pydub is required for MP3 synthesis")
            print("Install with: pip install pydub simpleaudio")
            sys.exit(1)
        
        print("✓ LoFi Synthesizer initialized")
    
    def load_json(self, filename: str) -> dict:
        """Load JSON track parameters"""
        json_path = self.output_dir / filename
        if not json_path.exists():
            raise FileNotFoundError(f"Track not found: {filename}")
        
        with open(json_path, 'r') as f:
            return json.load(f)
    
    def get_frequency(self, note_number: int, key: int = 1) -> float:
        """
        Convert note number to frequency (Hz)
        note_number: 1-7 (scale degree)
        key: 1-12 (chromatic root)
        """
        # Simple mapping - in real implementation would use proper music theory
        base_freq = list(NOTES.values())[key - 1]
        # Scale degrees: 1=root, 2=major 2nd, 3=major 3rd, etc.
        # Approximate using semitone multiplier: 2^(semitones/12)
        semitones = [0, 2, 4, 5, 7, 9, 11][note_number - 1]  # Major scale
        return base_freq * (2 ** (semitones / 12)) * 4  # Octave up for melody
    
    def synthesize_track(self, params: dict, duration_seconds: float = 120) -> bytes:
        """
        Synthesize audio from JSON parameters
        Returns WAV bytes
        """
        bpm = params.get('bpm', 80)
        key = params.get('key', 1)
        chords = params.get('chords', [1, 5, 6, 3])
        melodies = params.get('melodies', [[1, 2, 3, 4]])
        
        # Calculate timing
        quarter_note_ms = int((60 / bpm) * 1000)
        eighth_note_ms = quarter_note_ms // 2
        
        print(f"  Synthesizing: BPM={bpm}, Key={key}, Duration={duration_seconds}s")
        
        # Create empty audio
        audio = AudioSegment.empty()
        
        # Generate bass line (chords)
        bass_freq = self.get_frequency(chords[0], key) / 4
        bass_duration = quarter_note_ms * 2
        for chord in chords:
            freq = self.get_frequency(chord, key) / 4
            bass_sound = Sine(freq).to_audio_segment(duration=bass_duration).apply_gain(-20)
            audio += bass_sound
        
        # Generate melody
        if melodies:
            melody_audio = AudioSegment.empty()
            for melody_notes in melodies:
                for note in melody_notes:
                    freq = self.get_frequency(note, key)
                    note_sound = Sine(freq).to_audio_segment(duration=eighth_note_ms).apply_gain(-15)
                    melody_audio += note_sound
        
            # Mix melody with bass (repeat to fill duration)
            while len(melody_audio) < duration_seconds * 1000:
                melody_audio += melody_audio[:len(melody_audio)]
        
            audio = audio.overlay(melody_audio[:duration_seconds * 1000], position=0)
        
        # Pad to duration
        if len(audio) < duration_seconds * 1000:
            silence = AudioSegment.silent(duration=duration_seconds * 1000 - len(audio))
            audio += silence
        else:
            audio = audio[:int(duration_seconds * 1000)]
        
        # Add fade out
        audio = audio.fade_out(duration=3000)
        
        return audio.export(format="mp3").read()
    
    def generate_mp3(self, json_filename: str, custom_name: str = None) -> str:
        """
        Generate MP3 from JSON track file
        Returns path to generated MP3
        """
        print(f"\n📍 Processing: {json_filename}")
        
        # Load parameters
        track_data = self.load_json(json_filename)
        params = track_data.get('output_params', {})
        
        # Generate MP3
        mp3_data = self.synthesize_track(params)
        
        # Save MP3
        base_name = custom_name or json_filename.replace('.json', '')
        mp3_path = self.output_dir / f"{base_name}.mp3"
        
        with open(mp3_path, 'wb') as f:
            f.write(mp3_data)
        
        file_size_mb = os.path.getsize(mp3_path) / (1024 * 1024)
        print(f"✓ Generated: {mp3_path.name} ({file_size_mb:.2f}MB)")
        
        return str(mp3_path)
    
    def batch_generate(self, count: int = None) -> list:
        """
        Generate MP3s from all or N JSON files
        """
        json_files = sorted([
            f for f in os.listdir(self.output_dir)
            if f.endswith('.json') and f != 'manifest.json'
        ])
        
        if count:
            json_files = json_files[:count]
        
        print(f"\n🎵 Batch generating {len(json_files)} MP3 files...")
        
        results = []
        for i, json_file in enumerate(json_files, 1):
            try:
                print(f"\n[{i}/{len(json_files)}] {json_file}")
                mp3_path = self.generate_mp3(json_file)
                results.append(mp3_path)
            except Exception as e:
                print(f"✗ Error: {e}")
        
        return results
    
    def list_tracks(self) -> list:
        """List all generated JSON tracks"""
        json_files = [
            f for f in os.listdir(self.output_dir)
            if f.endswith('.json') and f != 'manifest.json'
        ]
        return sorted(json_files)


def main():
    parser = argparse.ArgumentParser(description="Synthesize MP3 from LoFi parameters")
    parser.add_argument('command', nargs='?', default='help',
                       choices=['single', 'batch', 'list', 'help'])
    parser.add_argument('--file', help='JSON filename for single synthesis')
    parser.add_argument('--count', type=int, help='Number of files for batch')
    parser.add_argument('--name', help='Custom output name')
    
    args = parser.parse_args()
    
    try:
        synth = LoFiSynthesizer()
        
        if args.command == 'single':
            if not args.file:
                print("ERROR: Please specify --file")
                print("Usage: python src/synthesizer.py single --file lofi_*.json")
                sys.exit(1)
            synth.generate_mp3(args.file, args.name)
        
        elif args.command == 'batch':
            results = synth.batch_generate(args.count)
            print(f"\n✓ Generated {len(results)} MP3 files")
        
        elif args.command == 'list':
            tracks = synth.list_tracks()
            print(f"\nAvailable tracks ({len(tracks)}):")
            for track in tracks:
                print(f"  - {track}")
        
        else:
            print("""
LoFi Music Synthesizer

Converts JSON track parameters to MP3 audio files.

Usage:
  python src/synthesizer.py single --file lofi_*.json              # Synthesize one
  python src/synthesizer.py batch [--count 10]                    # Synthesize all or N
  python src/synthesizer.py list                                  # List available tracks

Prerequisites:
  pip install pydub simpleaudio

Output:
  MP3 files saved to output/ directory

Examples:
  python src/synthesizer.py single --file lofi_20260503_151844_1.json
  python src/synthesizer.py batch --count 5
  python src/synthesizer.py list
            """)
    
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
