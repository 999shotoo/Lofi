#!/usr/bin/env python3
"""
LoFi Music Synthesizer - Fast WAV generation (10 seconds)
"""

import os
import sys
import json
import argparse
import wave
import struct
import math
from pathlib import Path

class FastLoFiSynthesizer:
    def __init__(self, duration_seconds: float = 10):
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        self.sample_rate = 44100
        self.duration = duration_seconds
        
        print(f"✓ Fast Synthesizer: {duration_seconds}s audio @ {self.sample_rate}Hz")
    
    def load_json(self, filename: str) -> dict:
        """Load JSON track parameters"""
        json_path = self.output_dir / filename
        if not json_path.exists():
            raise FileNotFoundError(f"Track not found: {filename}")
        with open(json_path, 'r') as f:
            return json.load(f)
    
    def get_notes(self, scale_degree: int, key: int = 1) -> float:
        """Get frequency for scale degree"""
        base_notes = [16.35, 18.35, 20.60, 21.83, 24.50, 27.50, 30.87]  # C to B
        scale_intervals = [0, 2, 4, 5, 7, 9, 11]  # Major scale semitones
        
        # Ensure values are within valid ranges (1-7)
        scale_degree = max(1, min(7, scale_degree))
        key = max(1, min(7, key))
        
        base_freq = base_notes[key - 1]
        semitones = scale_intervals[scale_degree - 1]
        freq = base_freq * (2 ** (semitones / 12)) * 8  # Octave 3
        return freq
    
    def generate_wave(self, frequency: float, duration_ms: int) -> list:
        """Generate sine wave"""
        samples = []
        duration_sec = duration_ms / 1000.0
        num_samples = int(self.sample_rate * duration_sec)
        
        for i in range(num_samples):
            t = i / self.sample_rate
            # Add envelope
            envelope = 1.0
            if i < int(0.02 * self.sample_rate):  # Attack
                envelope = i / int(0.02 * self.sample_rate)
            elif i > num_samples - int(0.1 * self.sample_rate):  # Release
                envelope = (num_samples - i) / int(0.1 * self.sample_rate)
            
            sample = 0.3 * math.sin(2 * math.pi * frequency * t) * envelope
            samples.append(sample)
        
        return samples
    
    def synthesize(self, params: dict) -> bytes:
        """Quick synthesis"""
        bpm = params.get('bpm', 80)
        key = params.get('key', 1)
        # Clamp key to valid range
        key = max(1, min(7, key))
        chords = params.get('chords', [1, 5, 6, 3])
        
        total_samples = int(self.sample_rate * self.duration)
        audio = [0.0] * total_samples
        
        # Generate bass
        bass_duration_ms = int((60 / bpm) * 1000 * 2)
        position = 0
        
        for chord in chords:
            # Ensure chord value is valid (1-7)
            chord = max(1, min(7, chord))
            if position >= total_samples:
                break
            freq = self.get_notes(chord, key) / 2
            bass_samples = self.generate_wave(freq, bass_duration_ms)
            for j, s in enumerate(bass_samples):
                if position + j < total_samples:
                    audio[position + j] += s
            position += len(bass_samples)
        
        # Normalize
        max_val = max(abs(s) for s in audio) if audio else 1
        if max_val > 0.95:
            audio = [s * (0.95 / max_val) for s in audio]
        
        # Convert to 16-bit
        pcm = b''
        for s in audio:
            s = max(-1, min(1, s))
            pcm += struct.pack('<h', int(s * 32767))
        
        return pcm
    
    def save_wav(self, wav_data: bytes, filename: str) -> float:
        """Save WAV file"""
        wav_path = self.output_dir / filename
        with wave.open(str(wav_path), 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(self.sample_rate)
            f.writeframes(wav_data)
        
        return os.path.getsize(wav_path) / 1024 / 1024
    
    def generate_wav(self, json_filename: str) -> str:
        """Generate one WAV file"""
        track_data = self.load_json(json_filename)
        params = track_data.get('output_params', {})
        
        wav_data = self.synthesize(params)
        base_name = json_filename.replace('.json', '')
        wav_filename = f"{base_name}.wav"
        size = self.save_wav(wav_data, wav_filename)
        
        print(f"  ✓ {wav_filename} ({size:.2f}MB)")
        return str(self.output_dir / wav_filename)
    
    def batch_generate(self, count: int = None) -> int:
        """Generate multiple WAV files"""
        json_files = sorted([
            f for f in os.listdir(self.output_dir)
            if f.endswith('.json') and f != 'manifest.json'
        ])
        
        if count:
            json_files = json_files[:count]
        
        print(f"\n🎵 Generating {len(json_files)} WAV files ({self.duration}s each)...\n")
        
        for json_file in json_files:
            try:
                self.generate_wav(json_file)
            except Exception as e:
                print(f"  ✗ Error: {e}")
        
        return len(json_files)


def main():
    parser = argparse.ArgumentParser(description="Fast LoFi WAV synthesis")
    parser.add_argument('command', nargs='?', default='help', choices=['single', 'batch', 'help'])
    parser.add_argument('--file', help='JSON file to synthesize')
    parser.add_argument('--count', type=int, help='Batch count')
    parser.add_argument('--duration', type=float, default=10, help='Audio duration in seconds')
    
    args = parser.parse_args()
    synth = FastLoFiSynthesizer(duration_seconds=args.duration)
    
    try:
        if args.command == 'single':
            if not args.file:
                print("Usage: python synthesizer_fast.py single --file lofi_*.json")
                sys.exit(1)
            synth.generate_wav(args.file)
        
        elif args.command == 'batch':
            count = synth.batch_generate(args.count)
            print(f"\n✓ Generated {count} WAV files in output/")
        
        else:
            print("""
🎵 Fast LoFi Synthesizer

Generates 10-second WAV files from JSON parameters (fast!).

Usage:
  python synthesizer_fast.py single --file lofi_*.json
  python synthesizer_fast.py batch [--count 10]
  python synthesizer_fast.py batch --duration 30            # Custom length

Output: WAV files in output/ directory
            """)
    
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
