# ESP32 Dispenser Test Script
# Quick testing without physical hardware - watch Serial Monitor for output!

# Configuration - CHANGE THIS TO YOUR ESP32 IP
$ESP32_IP = "192.168.1.100"

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "ESP32 Cigarette Dispenser Tester" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "ESP32 IP: $ESP32_IP" -ForegroundColor Yellow
Write-Host "Make sure Serial Monitor is open at 115200 baud!" -ForegroundColor Yellow
Write-Host ""

# Function to test endpoint
function Test-ESP32 {
    param($Name, $Endpoint, $Body = $null)
    
    Write-Host "[$Name]" -ForegroundColor Green
    Write-Host "Sending request to http://${ESP32_IP}${Endpoint}" -ForegroundColor Gray
    
    try {
        if ($Body) {
            $response = Invoke-RestMethod -Uri "http://${ESP32_IP}${Endpoint}" `
                -Method POST `
                -ContentType "application/json" `
                -Body $Body `
                -TimeoutSec 30
        } else {
            $response = Invoke-RestMethod -Uri "http://${ESP32_IP}${Endpoint}" `
                -Method GET `
                -TimeoutSec 5
        }
        
        Write-Host "✅ Success!" -ForegroundColor Green
        Write-Host ($response | ConvertTo-Json -Depth 3) -ForegroundColor White
        Write-Host ""
        return $true
    }
    catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
        Write-Host ""
        return $false
    }
}

# Menu
function Show-Menu {
    Write-Host "Choose a test:" -ForegroundColor Cyan
    Write-Host "1. Check ESP32 Status" -ForegroundColor White
    Write-Host "2. Test Single Solenoid (Cigarette 1)" -ForegroundColor White
    Write-Host "3. Test 2x Cigarette 1 (Same solenoid twice)" -ForegroundColor White
    Write-Host "4. Test 2x Cigarette 1 + 3x Cigarette 2" -ForegroundColor White
    Write-Host "5. Test 1 of each (Cigarettes 1-16)" -ForegroundColor White
    Write-Host "6. Custom Test" -ForegroundColor White
    Write-Host "7. Change ESP32 IP" -ForegroundColor White
    Write-Host "Q. Quit" -ForegroundColor White
    Write-Host ""
}

while ($true) {
    Show-Menu
    $choice = Read-Host "Enter choice"
    Write-Host ""
    
    switch ($choice) {
        "1" {
            Test-ESP32 -Name "Status Check" -Endpoint "/status"
            Start-Sleep -Seconds 1
        }
        
        "2" {
            Write-Host "Testing single push of Solenoid 1..." -ForegroundColor Yellow
            Write-Host "Watch Serial Monitor for:" -ForegroundColor Yellow
            Write-Host "  - 🚬 PUSHING SOLENOID 1 (Cigarette 1)" -ForegroundColor Gray
            Write-Host "  - ✅ Solenoid 1 PUSHED" -ForegroundColor Gray
            Write-Host ""
            $body = '{"solenoid_id": 1}'
            Test-ESP32 -Name "Single Solenoid Test" -Endpoint "/test" -Body $body
            Start-Sleep -Seconds 2
        }
        
        "3" {
            Write-Host "Testing 2 pushes of SAME Solenoid 1..." -ForegroundColor Yellow
            Write-Host "Watch Serial Monitor for:" -ForegroundColor Yellow
            Write-Host "  - 🚬 PUSHING SOLENOID 1 (Push 1 of 2)" -ForegroundColor Gray
            Write-Host "  - ⏳ Waiting 1000ms..." -ForegroundColor Gray
            Write-Host "  - 🚬 PUSHING SOLENOID 1 (Push 2 of 2)" -ForegroundColor Gray
            Write-Host ""
            $body = '{"items": [{"id": 1, "quantity": 2}]}'
            Test-ESP32 -Name "2x Cigarette 1" -Endpoint "/dispense" -Body $body
            Start-Sleep -Seconds 3
        }
        
        "4" {
            Write-Host "Testing sequential dispensing..." -ForegroundColor Yellow
            Write-Host "Order: 2x Cigarette 1, 3x Cigarette 2" -ForegroundColor Yellow
            Write-Host "Watch Serial Monitor for 5 total pushes!" -ForegroundColor Yellow
            Write-Host ""
            $body = '{"items": [{"id": 1, "quantity": 2}, {"id": 2, "quantity": 3}]}'
            Test-ESP32 -Name "Multiple Items" -Endpoint "/dispense" -Body $body
            Start-Sleep -Seconds 5
        }
        
        "5" {
            Write-Host "Testing all 16 solenoids (1 push each)..." -ForegroundColor Yellow
            Write-Host "This will take ~24 seconds (16 pushes × 1.5s)" -ForegroundColor Yellow
            Write-Host ""
            $items = 1..16 | ForEach-Object { @{id=$_; quantity=1} }
            $body = @{items=$items} | ConvertTo-Json -Depth 3 -Compress
            Test-ESP32 -Name "All Solenoids Test" -Endpoint "/dispense" -Body $body
            Start-Sleep -Seconds 2
        }
        
        "6" {
            Write-Host "Custom Test" -ForegroundColor Cyan
            $cig1 = Read-Host "Cigarette 1 quantity (0-10)"
            $cig2 = Read-Host "Cigarette 2 quantity (0-10)"
            
            $items = @()
            if ([int]$cig1 -gt 0) { $items += @{id=1; quantity=[int]$cig1} }
            if ([int]$cig2 -gt 0) { $items += @{id=2; quantity=[int]$cig2} }
            
            if ($items.Count -gt 0) {
                $body = @{items=$items} | ConvertTo-Json -Depth 3 -Compress
                Write-Host "Sending: $body" -ForegroundColor Gray
                Test-ESP32 -Name "Custom Order" -Endpoint "/dispense" -Body $body
                Start-Sleep -Seconds 2
            } else {
                Write-Host "No items to dispense!" -ForegroundColor Red
            }
        }
        
        "7" {
            $newIP = Read-Host "Enter new ESP32 IP address"
            $ESP32_IP = $newIP
            Write-Host "ESP32 IP updated to: $ESP32_IP" -ForegroundColor Green
            Write-Host ""
        }
        
        "Q" {
            Write-Host "Goodbye!" -ForegroundColor Cyan
            break
        }
        
        default {
            Write-Host "Invalid choice!" -ForegroundColor Red
            Write-Host ""
        }
    }
}
