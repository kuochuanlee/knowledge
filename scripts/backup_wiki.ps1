# 備份 Wiki 知識庫至 Google Drive
# 此腳本將同步 wiki 目錄至雲端硬碟備份路徑

# 獲取專案根目錄（腳本位於 scripts 目錄下）
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$SourcePath = Join-Path $ProjectRoot "wiki"
$DestinationPath = "H:\我的雲端硬碟\DriveSyncFiles\wiki_book"

# 檢查來源目錄是否存在
if (-not (Test-Path $SourcePath)) {
    Write-Error "錯誤：找不到來源目錄 $SourcePath"
    exit 1
}

# 確保目的地父目錄存在
$DestParent = Split-Path -Parent $DestinationPath
if (-not (Test-Path $DestParent)) {
    Write-Warning "警告：目的地磁碟或路徑 $DestParent 未掛載或不存在。"
    exit 1
}

Write-Host "開始同步 Wiki 知識庫..." -ForegroundColor Cyan
Write-Host "來源：$SourcePath"
Write-Host "目的地：$DestinationPath"

# 使用 robocopy 進行高效同步
# /MIR: 鏡像目錄（包含刪除目的地多餘檔案）
# /XD: 排除目錄（排除 .git）
# /R:3 /W:5: 失敗重試 3 次，每次間隔 5 秒
robocopy $SourcePath $DestinationPath /MIR /XD .git /R:3 /W:5

# Robocopy 的 Exit Code 0-7 代表成功或有部分更新，8 以上代表錯誤
if ($LASTEXITCODE -le 7) {
    Write-Host "備份成功完成！" -ForegroundColor Green
} else {
    Write-Error "備份失敗，Robocopy 錯誤碼：$LASTEXITCODE"
}
