@echo off
REM LoFi Generator - Windows Helper Script

setlocal enabledelayedexpansion

if "%1"=="" (
    echo.
    echo LoFi Music Generator
    echo Usage: generate.bat [command] [args]
    echo.
    echo Commands:
    echo   random [count]      Generate N random tracks
    echo   lyrics [text]       Generate from lyrics
    echo   server              Start the Flask server
    echo   help                Show this help
    echo.
    goto end
)

if "%1"=="random" (
    set count=%2
    if "!count!"=="" set count=1
    echo Generating !count! random tracks...
    python src/generator.py --random !count!
    goto end
)

if "%1"=="lyrics" (
    set lyrics=%2 %3 %4 %5 %6 %7 %8 %9
    if "!lyrics!"==" " (
        echo Please provide lyrics as arguments
        goto end
    )
    echo Generating from lyrics: !lyrics!
    python src/generator.py --lyrics "!lyrics!"
    goto end
)

if "%1"=="server" (
    echo Starting Flask server...
    cd ..
    python server/app.py
    goto end
)

if "%1"=="help" (
    goto :help
)

echo Unknown command: %1
echo Run "generate.bat help" for usage information

:end
endlocal
exit /b 0

:help
echo.
echo LoFi Music Generator
echo Usage: generate.bat [command] [args]
echo.
echo Commands:
echo   random [count]      Generate N random tracks (default: 1)
echo   lyrics [text]       Generate track from lyrics
echo   server              Start the Flask server
echo   help                Show this help
echo.
echo Output directory: .\output\
echo.
goto end
