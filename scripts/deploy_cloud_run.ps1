param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [string]$Region = "europe-west1",
    [string]$Service = "setwatch",
    [string]$Secret = "setwatch-parallel-api-key"
)

$ErrorActionPreference = "Stop"

function Invoke-Gcloud {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & gcloud @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "gcloud failed: $($Arguments -join ' ')"
    }
}

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    throw "Google Cloud CLI is not installed or is not on PATH."
}

$activeAccount = & gcloud auth list --filter=status:ACTIVE --format="value(account)"
if (-not $activeAccount) {
    throw "No active Google Cloud login. Run: gcloud auth login"
}

Invoke-Gcloud config set project $ProjectId
Invoke-Gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com secretmanager.googleapis.com iam.googleapis.com

& gcloud secrets describe $Secret --project $ProjectId *> $null
if ($LASTEXITCODE -ne 0) {
    Invoke-Gcloud secrets create $Secret --replication-policy=automatic --project $ProjectId
}

$secureKey = Read-Host "Parallel API key (input is hidden)" -AsSecureString
$keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
try {
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer)
    $plainKey | & gcloud secrets versions add $Secret --data-file=- --project $ProjectId
    if ($LASTEXITCODE -ne 0) { throw "Failed to add the Parallel secret version." }
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer)
    $plainKey = $null
}

$serviceAccountName = "setwatch-runtime"
$serviceAccountEmail = "$serviceAccountName@$ProjectId.iam.gserviceaccount.com"
& gcloud iam service-accounts describe $serviceAccountEmail --project $ProjectId *> $null
if ($LASTEXITCODE -ne 0) {
    Invoke-Gcloud iam service-accounts create $serviceAccountName --display-name="SetWatch runtime" --project $ProjectId
}

Invoke-Gcloud projects add-iam-policy-binding $ProjectId --member="serviceAccount:$serviceAccountEmail" --role="roles/aiplatform.user" --quiet
Invoke-Gcloud secrets add-iam-policy-binding $Secret --member="serviceAccount:$serviceAccountEmail" --role="roles/secretmanager.secretAccessor" --project $ProjectId --quiet

Invoke-Gcloud run deploy $Service --source . --region $Region --project $ProjectId --allow-unauthenticated --service-account $serviceAccountEmail --set-env-vars="GOOGLE_CLOUD_PROJECT=$ProjectId,GOOGLE_CLOUD_LOCATION=global,GOOGLE_GENAI_USE_VERTEXAI=true,GEMINI_MODEL=gemini-2.5-flash,SETWATCH_DEMO_MODE=false" --set-secrets="PARALLEL_API_KEY=${Secret}:latest"

$serviceUrl = & gcloud run services describe $Service --region $Region --project $ProjectId --format="value(status.url)"
Write-Host "SetWatch deployed: $serviceUrl"
Write-Host "Health check: $serviceUrl/health"
