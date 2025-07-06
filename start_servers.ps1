# AI Recommendation Engine Startup Script (PowerShell)
Write-Host "🎬 AI Recommendation Engine Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "📦 Starting Flask API Server..." -ForegroundColor Yellow
$flaskJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    python app.py
} -ArgumentList $projectDir

Write-Host "⏳ Waiting for Flask API to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "🚀 Starting React Frontend..." -ForegroundColor Yellow
$frontendDir = Join-Path $projectDir "recommendation-frontend"
$reactJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    npm start
} -ArgumentList $frontendDir

Write-Host ""
Write-Host "✅ Both servers are starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access the application at:" -ForegroundColor Magenta
Write-Host "  - Flask API: http://localhost:5000" -ForegroundColor White
Write-Host "  - React Frontend: http://localhost:3001" -ForegroundColor White
Write-Host ""
Write-Host "📚 API Documentation: http://localhost:5000/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers..." -ForegroundColor Red

try {
    while ($true) {
        if ($flaskJob.State -eq "Failed" -or $reactJob.State -eq "Failed") {
            Write-Host "❌ One of the servers failed to start!" -ForegroundColor Red
            break
        }
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "🛑 Stopping servers..." -ForegroundColor Yellow
    Stop-Job $flaskJob, $reactJob -ErrorAction SilentlyContinue
    Remove-Job $flaskJob, $reactJob -ErrorAction SilentlyContinue
    Write-Host "✅ Servers stopped." -ForegroundColor Green
}
