$env:Path = $env:Path + ';C:\Program Files\Google\Chrome\Application'
$userDataDir = "$env:TEMP\chrome-debug"
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "--remote-debugging-port=9222", "--no-first-run", "--no-default-browser-check", "--user-data-dir=$userDataDir"
