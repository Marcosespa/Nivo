# Script de pruebas de webhooks - Nivo
# Ejecutar: .\test_webhooks.ps1

param(
    [string]$API = "http://localhost:8000",
    [string]$WompiSecret = $env:WOMPI_INTEGRITY_SECRET,
    [switch]$SkipTruora = $false
)

Write-Host "Pruebas de webhooks fallidos contra: $API" -ForegroundColor Green
if ($WompiSecret) {
    Write-Host "   Wompi Secret: configurado" -ForegroundColor Green
}
else {
    Write-Host "   ADVERTENCIA: Wompi Secret no configurado" -ForegroundColor Yellow
}
Write-Host ""

# Test 1: Firma invalida
Write-Host "TEST 1: Firma invalida -> WEBHOOK_INVALID_SIGNATURE alert" -ForegroundColor Cyan

for ($i = 1; $i -le 3; $i++) {
    Write-Host "  Request $i/3..."

    $payload = @{
        data = @{
            transaction = @{
                id = "bad-sig-test-$i"
                status = "APPROVED"
                amount_in_cents = 100000
            }
        }
        event = "nivo.transaction_status_update"
        environment = "production"
        signature = @{
            properties = "id,amount_in_cents"
            integrity_hash = "BADHASH$i"
        }
    } | ConvertTo-Json -Depth 10

    $response = curl -s -X POST "$API/api/v1/topup/webhook" `
        -H "Content-Type: application/json" `
        -H "X-Event: nivo.transaction_status_update" `
        -d $payload

    Write-Host "  Response: $response" -ForegroundColor Gray
}

Write-Host "OK: Verifica Slack #alertas-criticas (3er request debe disparar alerta)" -ForegroundColor Yellow
Write-Host ""

# Test 2: Wompi DECLINED
Write-Host "TEST 2: Wompi DECLINED -> transaction.status = 'failed'" -ForegroundColor Cyan

$txId = "test-declined-$(Get-Date -UFormat %s)"
$amount = 50000
$currency = "COP"

if ($WompiSecret) {
    # Calcular HMAC-SHA256
    $stringToHash = "${txId}${amount}${currency}DECLINED${WompiSecret}"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($stringToHash)
    $hmac = New-Object System.Security.Cryptography.HMACSHA256
    $hmac.Key = [System.Text.Encoding]::UTF8.GetBytes($WompiSecret)
    $hash = ($hmac.ComputeHash($bytes) | ForEach-Object { "{0:x2}" -f $_ }) -join ""

    Write-Host "  TX_ID: $txId"
    Write-Host "  Signature: $($hash.Substring(0, 16))..."

    $payload = @{
        data = @{
            transaction = @{
                id = $txId
                status = "DECLINED"
                amount_in_cents = $amount
                currency = $currency
                reference = "ref-$txId"
            }
        }
        event = "nivo.transaction_status_update"
        environment = "production"
        signature = @{
            properties = "data.transaction.id,data.transaction.amount_in_cents,data.transaction.currency,data.transaction.status"
            integrity_hash = $hash
        }
    } | ConvertTo-Json -Depth 10

    $response = curl -s -X POST "$API/api/v1/topup/webhook" `
        -H "Content-Type: application/json" `
        -d $payload

    Write-Host "  Response: $response" -ForegroundColor Gray
    Write-Host "OK: Verifica en BD: SELECT status FROM transactions WHERE id='$txId';" -ForegroundColor Yellow
}
else {
    Write-Host "  SALTADO: Sin WOMPI_INTEGRITY_SECRET" -ForegroundColor Yellow
}
Write-Host ""

# Test 3: Truora KYC rechazado (MOCK)
Write-Host "TEST 3: Truora KYC_RESULT rejected (MOCK) -> funnel tracking" -ForegroundColor Cyan

if ($SkipTruora) {
    Write-Host "  SALTADO: --SkipTruora activado" -ForegroundColor Yellow
}
else {
    $checkId = "truora-mock-$(Get-Date -UFormat %s)"

    $payload_obj = @{
        check_id = $checkId
        account_id = "test-account-$checkId"
        status = "declined"
        score = 0.15
        rejection_reason = "liveness_fail"
    }

    $payload = $payload_obj | ConvertTo-Json -Depth 10

    Write-Host "  CHECK_ID: $checkId"
    Write-Host "  Payload (mock, sin firma validada):" -ForegroundColor DarkGray
    Write-Host "  $payload" -ForegroundColor DarkGray

    $response = curl -s -X POST "$API/api/v1/kyc/webhook" `
        -H "Content-Type: application/json" `
        -d $payload

    Write-Host "  Response: $response" -ForegroundColor Gray
    Write-Host "OK: En DEVELOPMENT mode, firma no se valida" -ForegroundColor Yellow
    Write-Host "OK: Verifica en BD: SELECT step, result, failure_reason FROM kyc_funnel_events WHERE check_id LIKE '%mock%';" -ForegroundColor Yellow
}
Write-Host ""

# Test 4: Idempotencia
Write-Host "TEST 4: Idempotencia (mismo event dos veces)" -ForegroundColor Cyan

$idempotentId = "idempotent-test-$(Get-Date -UFormat %s)"
$payload = @{
    data = @{
        transaction = @{
            id = $idempotentId
            status = "APPROVED"
            amount_in_cents = 25000
        }
    }
    event = "test"
    signature = @{
        integrity_hash = "test"
    }
} | ConvertTo-Json -Depth 10

Write-Host "  Enviando request 1..."
$r1 = curl -s -X POST "$API/api/v1/topup/webhook" `
    -H "Content-Type: application/json" `
    -d $payload

Write-Host "  Response 1: $r1" -ForegroundColor Gray

Write-Host "  Enviando request 2 (debe ignorarse por idempotencia)..."
$r2 = curl -s -X POST "$API/api/v1/topup/webhook" `
    -H "Content-Type: application/json" `
    -d $payload

Write-Host "  Response 2: $r2" -ForegroundColor Gray

$query = "SELECT COUNT(*) FROM webhook_event_logs WHERE provider_event_id='$idempotentId';"
Write-Host "OK: Verifica en BD: $query" -ForegroundColor Yellow
Write-Host "    (debe ser 1, no 2)" -ForegroundColor Yellow
Write-Host ""

Write-Host "COMPLETO: Pruebas finalizadas." -ForegroundColor Green
Write-Host ""
Write-Host "Proximos pasos:" -ForegroundColor Cyan
Write-Host "  1. Ver Slack #alertas-criticas (si esta configurado)" -ForegroundColor White
Write-Host "  2. Revisar logs: cd backend && tail -f logs/app.log" -ForegroundColor White
Write-Host "  3. Ejecutar queries SQL de verificacion (ver arriba)" -ForegroundColor White
