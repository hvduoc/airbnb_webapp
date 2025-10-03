# Google Service Account Credentials Placeholder
# 
# TO SET UP GOOGLE SHEETS INTEGRATION:
# 
# 1. Go to Google Cloud Console: https://console.cloud.google.com/
# 2. Create a new project or select existing one
# 3. Enable Google Sheets API and Google Drive API
# 4. Create Service Account:
#    - Go to IAM & Admin > Service Accounts  
#    - Click "Create Service Account"
#    - Name: "payment-ledger-service"
#    - Download JSON credentials file
# 5. Rename the downloaded file to "service-account.json"
# 6. Place it in this credentials/ directory
# 7. Share your Google Spreadsheet with the service account email
#    (found in the JSON file under "client_email")
# 8. Copy your spreadsheet ID from the URL and add to .env:
#    GOOGLE_SPREADSHEET_ID=1your_spreadsheet_id_here
#
# Your service-account.json should look like:
# {
#   "type": "service_account",
#   "project_id": "your-project-id",
#   "private_key_id": "...",
#   "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
#   "client_email": "payment-ledger-service@your-project.iam.gserviceaccount.com",
#   "client_id": "...",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "..."
# }

# This file is ignored by git for security
# Never commit actual credentials to version control!