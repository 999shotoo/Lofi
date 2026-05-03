#!/usr/bin/env python3
"""
LoFi Music Synthesizer - Generates WAV/MP3 from JSON parameters
Minimal dependencies version
"""

import os
import sys
import json
import argparse
import wave
import struct
import math
from pathlib import Path
from datetime import datetime

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
        self.sample_rate = 44100
        
        print("✓ LoFi Synthesizer initialized")
        print(f"✓ Sample rate: {self.sample_rate}Hz")
    
    def load_json(self, filename: str) -> dict:
        """Load JSON track parameters"""
        json_path = self.output_dir / filename
        if not json_path.exists():
            raise FileNotFoundError(f"Track not found: {filename}")
        
        with open(json_path, 'r') as f:
            return json.load(f)
    
    def generate_sine_wave(self, frequency: float, duration_ms: int, amplitude: float = 0.3) -> list:
        """Generate sine wave samples"""
        duration_sec = duration_ms / 1000.0
        num_samples = int(self.sample_rate * duration_sec)
        samples = []
        
        for i in range(num_samples):
            t = i / self.sample_rate
            sample = amplitude * math.sin(2 * math.pi * frequency * t)
            samples.append(sample)
        
        return samples
    
    def apply_envelope(self, samples: list, attack_ms: int = 10, release_ms: int = 100) -> list:
        """Apply ADSR-like envelope"""
        attack_samples = int(self.sample_rate * attack_ms / 1000)
        release_samples = int(self.sample_rate * release_ms / 1000)
        total_samples = len(samples)
        
        result = []
        for i, sample in enumerate(samples):
            # Attack
            if i < attack_samples:
                envelope = i / attack_samples
            # Release
            elif i > total_samples - release_samples:
                envelope = (total_samples - i) / release_samples
            # Sustain
            else:
                envelope = 1.0
            
            result.append(sample * envelope)
        
        return result
    
    def get_frequency(self, note_number: int, key: int = 1, octave: int = 4) -> float:
        """
        Convert note number to frequency
        note_number: 1-7 (scale degree)
        key: 1-12 (chromatic root)
        octave: 1-8
        """
        base_freq = list(NOTES.values())[key - 1]
        # Major scale intervals (semitones): 0, 2, 4, 5, 7, 9, 11
        semitones = [0, 2, 4, 5, 7, 9, 11][note_number - 1]
        frequency = base_freq * (2 ** (semitones / 12)) * (2 ** (octave - 1))
        return frequency
    
    def synthesize_track(self, params: dict, duration_seconds: float = 60) -> bytes:
        """
        Synthesize WAV audio from JSON parameters
        Returns WAV bytes
        """
        bpm = params.get('bpm', 80)
        key = params.get('key', 1)
        chords = params.get('chords', [1, 5, 6, 3])
        melodies = params.get('melodies', [[1, 2, 3, 4]])
        
        # Calculate timing
        quarter_note_ms = int((60 / bpm) * 1000)
        eighth_note_ms = quarter_note_ms // 2
        
        print(f"  🎵 Synthesizing: BPM={bpm}, Key={key}, Duration={duration_seconds}s")
        
        # Initialize audio
        total_samples = int(self.sample_rate * duration_seconds)
        audio = [0.0] * total_samples
        
        # Generate bass line
        bass_position = 0
        for i, chord in enumerate(chords):
            if bass_position >= total_samples:
                break
            
            freq = self.get_frequency(chord, key, octave=2)
            bass_samples = self.generate_sine_wave(freq, quarter_note_ms * 2, amplitude=0.2)
            bass_samples = self.apply_envelope(bass_samples, attack_ms=20, release_ms=200)
            
            for j, sample in enumerate(bass_samples):
                if bass_position + j < total_samples:
                    audio[bass_position + j] += sample
            
            bass_position += len(bass_samples)
        
        # Generate melody
        if melodies:
            melody_position = 0
            for melody_notes in melodies:
                for note in melody_notes:
                    if melody_position >= total_samples:
                        break
                    
                    freq = self.get_frequency(note, key, octave=4)
                    note_samples = self.generate_sine_wave(freq, eighth_note_ms, amplitude=0.15)
                    note_samples = self.apply_envelope(note_samples, attack_ms=5, release_ms=50)
                    
                    for j, sample in enumerate(note_samples):
                        if melody_position + j < total_samples:
                            audio[melody_position + j] += sample
                    
                    melody_position += len(note_samples)
        
        # Normalize audio (prevent clipping)
        max_sample = max(abs(s) for s in audio) if audio else 1.0
        if max_sample > 0.95:
            audio = [s * (0.95 / max_sample) for s in audio]
        
        # Convert to 16-bit PCM
        pcm_data = b''
        for sample in audio:
            # Clamp to [-1, 1]
            sample = max(-1.0, min(1.0, sample))
            # Convert to 16-bit integer
            pcm_int = int(sample * 32767)
            pcm_data += struct.pack('<h', pcm_int)
        
        return pcm_data
    
    def save_wav(self, wav_data: bytes, filename: str) -> str:
        """Save WAV data to file"""
        wav_path = self.output_dir / filename
        
        # Create WAV file header
        channels = 1
        sample_width = 2  # 16-bit
        frame_rate = self.sample_rate
        num_frames = len(wav_data) // (channels * sample_width)
        
        with wave.open(str(wav_path), 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(frame_rate)
            wav_file.writeframes(wav_data)
        
        file_size_kb = os.path.getsize(wav_path) / 1024
        return str(wav_path), file_size_kb
    
    def generate_wav(self, json_filename: str) -> str:
        """
        Generate WAV from JSON track file
        Returns path to generated WAV
        """
        print(f"\n📍 Processing: {json_filename}")
        
        # Load parameters
        track_data = self.load_json(json_filename)
        params = track_data.get('output_params', {})
        
        # Generate WAV
        wav_data = self.synthesize_track(params, duration_seconds=60)
        
        # Save WAV
        base_name = json_filename.replace('.json', '')
        wav_filename = f"{base_name}.wav"
        wav_path, file_size = self.save_wav(wav_data, wav_filename)
        
        print(f"✓ Generated: {wav_filename} ({file_size:.1f}KB)")
        
        return wav_path
    
    def batch_generate(self, count: int = None) -> list:
        """
        Generate WAV files from all or N JSON files
        """
        json_files = sorted([
            f for f in os.listdir(self.output_dir)
            if f.endswith('.json') and f != 'manifest.json'
        ])
        
        if count:
            json_files = json_files[:count]
        
        print(f"\n🎵 Batch generating {len(json_files)} WAV files...")
        
        results = []
        for i, json_file in enumerate(json_files, 1):
            try:
                print(f"\n[{i}/{len(json_files)}]")
                wav_path = self.generate_wav(json_file)
                results.append(wav_path)
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
    
    def get_stats(self) -> dict:
        """Get directory statistics"""
        json_files = [f for f in os.listdir(self.output_dir) if f.endswith('.json') and f != 'manifest.json']
        wav_files = [f for f in os.listdir(self.output_dir) if f.endswith('.wav')]
        
        return {
            'json_count': len(json_files),
            'wav_count': len(wav_files),
            'output_dir': str(self.output_dir)
        }


def main():
    parser = argparse.ArgumentParser(description="Synthesize WAV from LoFi parameters")
    parser.add_argument('command', nargs='?', default='help',
                       choices=['single', 'batch', 'list', 'stats', 'help'])
    parser.add_argument('--file', help='JSON filename for single synthesis')
    parser.add_argument('--count', type=int, help='Number of files for batch')
    
    args = parser.parse_args()
    
    try:
        synth = LoFiSynthesizer()
        
        if args.command == 'single':
            if not args.file:
                print("ERROR: Please specify --file")
                print("Usage: python src/synthesizer.py single --file lofi_*.json")
                sys.exit(1)
            synth.generate_wav(args.file)
        
        elif args.command == 'batch':
            results = synth.batch_generate(args.count)
            print(f"\n✓ Generated {len(results)} WAV files")
        
        elif args.command == 'list':
            tracks = synth.list_tracks()
            print(f"\nAvailable tracks ({len(tracks)}):")
            for track in tracks:
                print(f"  ▫ {track}")
        
        elif args.command == 'stats':
            stats = synth.get_stats()
            print(f"\nGenerator Statistics:")
            print(f"  JSON files: {stats['json_count']}")
            print(f"  WAV files:  {stats['wav_count']}")
            print(f"  Output dir: {stats['output_dir']}")
        
        else:
            print("""
🎵 LoFi Music Synthesizer

Converts JSON track parameters to WAV audio files.

Usage:
  python src/synthesizer.py single --file lofi_*.json    # Synthesize one
  python src/synthesizer.py batch [--count 10]           # Synthesize all or N
  python src/synthesizer.py list                         # List available tracks
  python src/synthesizer.py stats                        # Show statistics

No external dependencies required!

Output:
  WAV files saved to output/ directory

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
