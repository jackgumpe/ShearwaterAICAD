# PowerShell Shortcut: /inb
# Usage: inb [list|watch|claude|gemini]

param(
    [Parameter(Position=0)]
    [string]$Action = "list"
)

$CLAUDE_INBOX = "C:/Users/user/ShearwaterAICAD/communication/claude_code_inbox"
$GEMINI_INBOX = "C:/Users/user/ShearwaterAICAD/communication/gemini_cli_inbox"

function Show-InboxList {
    Write-Host ""
    Write-Host "======================== INBOX MESSAGE LIST ========================" -ForegroundColor Cyan

    Write-Host ""
    Write-Host "[CLAUDE CODE INBOX] - 5 most recent:" -ForegroundColor Yellow
    $claude_files = Get-ChildItem $CLAUDE_INBOX -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5
    foreach ($file in $claude_files) {
        Write-Host "  [FILE] $($file.Name)" -ForegroundColor White
    }

    Write-Host ""
    Write-Host "[GEMINI CLI INBOX] - 5 most recent:" -ForegroundColor Magenta
    $gemini_files = Get-ChildItem $GEMINI_INBOX -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5
    foreach ($file in $gemini_files) {
        Write-Host "  [FILE] $($file.Name)" -ForegroundColor White
    }
    Write-Host ""
}

function Show-LatestMessage {
    param([string]$Inbox)

    $files = Get-ChildItem $Inbox -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1

    if ($files) {
        $content = Get-Content $files.FullName | ConvertFrom-Json

        Write-Host ""
        Write-Host "======================= LATEST MESSAGE =======================" -ForegroundColor Green
        Write-Host "File: $($files.Name)" -ForegroundColor Cyan
        Write-Host "From: $($content.from)" -ForegroundColor Yellow
        Write-Host "Subject: $($content.subject)" -ForegroundColor Yellow
        Write-Host "Message: $($content.message)" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "No messages in this inbox." -ForegroundColor Red
    }
}

function Start-InboxWatcher {
    Write-Host ""
    Write-Host "[STARTING INBOX WATCHER]" -ForegroundColor Green
    Write-Host "Monitoring both inboxes for new messages..." -ForegroundColor Cyan
    Write-Host ""

    & python "C:\Users\user\ShearwaterAICAD\src\utilities\inbox_watcher.py"
}

# Execute based on action
switch ($Action.ToLower()) {
    "list" {
        Show-InboxList
    }
    "watch" {
        Start-InboxWatcher
    }
    "claude" {
        Write-Host ""
        Write-Host "[CLAUDE CODE INBOX - LATEST MESSAGE]" -ForegroundColor Cyan
        Show-LatestMessage $CLAUDE_INBOX
    }
    "gemini" {
        Write-Host ""
        Write-Host "[GEMINI CLI INBOX - LATEST MESSAGE]" -ForegroundColor Magenta
        Show-LatestMessage $GEMINI_INBOX
    }
    default {
        Write-Host "Usage:" -ForegroundColor Yellow
        Write-Host "  inb list   - List 5 most recent messages from both inboxes" -ForegroundColor White
        Write-Host "  inb claude - Show latest message from Claude inbox" -ForegroundColor White
        Write-Host "  inb gemini - Show latest message from Gemini inbox" -ForegroundColor White
        Write-Host "  inb watch  - Start watching inboxes for new messages" -ForegroundColor White
    }
}
