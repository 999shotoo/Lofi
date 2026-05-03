@echo off
REM LoFi Generator - Quick Demo Script
REM This script demonstrates how to use the generator

setlocal enabledelayedexpansion

echo.
echo ============================================
echo  LoFi Music Generator - Test Demo
echo ============================================
echo.

cd %~dp0

REM Test 1: Generate 3 random tracks
echo [1/3] Generating 3 random tracks...
python src/generator_demo.py --random 3
if errorlevel 1 (
    echo ERROR: Failed to generate random tracks
    goto error
)

REM Test 2: Generate from lyrics
echo.
echo [2/3] Generating from lyrics...
python src/generator_demo.py --lyrics "sunny morning beach vibes"
if errorlevel 1 (
    echo ERROR: Failed to generate from lyrics
    goto error
)

REM Test 3: Generate from latent vector
echo.
echo [3/3] Generating from latent vector...
python src/generator_demo.py --latent "0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0"
if errorlevel 1 (
    echo ERROR: Failed to generate from latent vector
    goto error
)

echo.
echo ============================================
echo  ✓ All tests completed successfully!
echo ============================================
echo.
echo Generated files are in: output\
echo View manifest.json for all tracks
echo.
echo Try these commands:
echo   python src/generator_demo.py --random 10
echo   python src/generator_demo.py --lyrics "sad rainy night"
echo.
goto end

:error
echo.
echo ============================================
echo  ✗ Test failed!
echo ============================================
exit /b 1

:end
endlocal
