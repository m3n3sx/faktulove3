#!/bin/bash

# ============================================================================
# Google Cloud Document AI Setup Script for FaktuLove
# ============================================================================
# This script automates the setup of Google Cloud Document AI for invoice OCR
# Author: FaktuLove Development Team
# Date: $(date +%Y-%m-%d)
# ============================================================================

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
PROJECT_ID="faktulove-ocr"
PROJECT_NAME="FaktuLove OCR"
BILLING_ACCOUNT_ID=""  # To be set by user
LOCATION="eu"  # Europe for GDPR compliance
SERVICE_ACCOUNT_NAME="faktulove-ocr-service"
PROCESSOR_DISPLAY_NAME="FaktuLove Invoice Parser"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[STATUS]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first:"
        echo "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "gcloud CLI is installed"
}

# Function to authenticate with Google Cloud
authenticate_gcloud() {
    print_status "Authenticating with Google Cloud..."
    gcloud auth login
    print_success "Authentication successful"
}

# Function to create project
create_project() {
    print_status "Creating Google Cloud project: $PROJECT_ID..."
    
    # Check if project already exists
    if gcloud projects describe $PROJECT_ID &>/dev/null; then
        print_warning "Project $PROJECT_ID already exists"
    else
        gcloud projects create $PROJECT_ID --name="$PROJECT_NAME"
        print_success "Project created: $PROJECT_ID"
    fi
    
    # Set active project
    gcloud config set project $PROJECT_ID
    print_success "Active project set to: $PROJECT_ID"
}

# Function to link billing account
link_billing() {
    print_status "Linking billing account..."
    
    # List available billing accounts
    echo "Available billing accounts:"
    gcloud billing accounts list
    
    echo ""
    read -p "Enter the billing account ID to link: " BILLING_ACCOUNT_ID
    
    if [ -n "$BILLING_ACCOUNT_ID" ]; then
        gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID
        print_success "Billing account linked"
    else
        print_warning "No billing account provided. Some features may be limited."
    fi
}

# Function to enable required APIs
enable_apis() {
    print_status "Enabling required APIs..."
    
    APIS=(
        "documentai.googleapis.com"
        "storage.googleapis.com"
        "cloudresourcemanager.googleapis.com"
        "iam.googleapis.com"
        "compute.googleapis.com"
    )
    
    for api in "${APIS[@]}"; do
        print_status "Enabling $api..."
        gcloud services enable $api --project=$PROJECT_ID
    done
    
    print_success "All required APIs enabled"
}

# Function to create service account
create_service_account() {
    print_status "Creating service account..."
    
    # Check if service account exists
    if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com &>/dev/null; then
        print_warning "Service account already exists"
    else
        gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
            --display-name="FaktuLove OCR Service Account" \
            --description="Service account for Document AI OCR processing"
        print_success "Service account created"
    fi
    
    # Grant necessary roles
    print_status "Granting roles to service account..."
    
    ROLES=(
        "roles/documentai.apiUser"
        "roles/storage.objectViewer"
        "roles/storage.objectCreator"
        "roles/logging.logWriter"
    )
    
    for role in "${ROLES[@]}"; do
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
            --role="$role"
    done
    
    print_success "Service account roles configured"
}

# Function to create and download service account key
create_service_key() {
    print_status "Creating service account key..."
    
    KEY_FILE="service-account-key.json"
    
    gcloud iam service-accounts keys create $KEY_FILE \
        --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
    
    print_success "Service account key created: $KEY_FILE"
    print_warning "Keep this key secure! Add it to .gitignore"
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        touch .env
    fi
    
    # Add Google Cloud credentials to .env
    echo "" >> .env
    echo "# Google Cloud Configuration" >> .env
    echo "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" >> .env
    echo "GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/$KEY_FILE" >> .env
}

# Function to create Document AI processor
create_document_ai_processor() {
    print_status "Creating Document AI processor..."
    
    # Install gcloud beta components if needed
    gcloud components install beta --quiet
    
    # Create processor
    PROCESSOR_RESPONSE=$(gcloud beta ai document-processors create \
        --location=$LOCATION \
        --display-name="$PROCESSOR_DISPLAY_NAME" \
        --type=INVOICE_PROCESSOR \
        --project=$PROJECT_ID \
        --format=json 2>/dev/null || echo "{}")
    
    if [ "$PROCESSOR_RESPONSE" != "{}" ]; then
        PROCESSOR_ID=$(echo $PROCESSOR_RESPONSE | jq -r '.name' | awk -F'/' '{print $NF}')
        print_success "Document AI processor created: $PROCESSOR_ID"
        
        # Add processor ID to .env
        echo "DOCUMENT_AI_PROCESSOR_ID=$PROCESSOR_ID" >> .env
    else
        print_warning "Could not create processor automatically. Manual creation may be required."
        echo "Visit: https://console.cloud.google.com/ai/document-ai"
    fi
}

# Function to create Cloud Storage bucket
create_storage_bucket() {
    print_status "Creating Cloud Storage bucket for documents..."
    
    BUCKET_NAME="${PROJECT_ID}-documents"
    
    # Check if bucket exists
    if gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
        print_warning "Bucket already exists: gs://$BUCKET_NAME"
    else
        gsutil mb -p $PROJECT_ID -c STANDARD -l $LOCATION gs://$BUCKET_NAME
        
        # Set lifecycle rule to delete files after 30 days
        cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 30,
          "matchesPrefix": ["ocr-uploads/"]
        }
      }
    ]
  }
}
EOF
        
        gsutil lifecycle set lifecycle.json gs://$BUCKET_NAME
        rm lifecycle.json
        
        print_success "Storage bucket created: gs://$BUCKET_NAME"
    fi
}

# Function to set up monitoring
setup_monitoring() {
    print_status "Setting up monitoring alerts..."
    
    # Enable Cloud Monitoring API
    gcloud services enable monitoring.googleapis.com --project=$PROJECT_ID
    
    print_success "Monitoring setup complete"
}

# Function to display summary
display_summary() {
    echo ""
    echo "============================================================================"
    echo "                    GOOGLE CLOUD SETUP COMPLETE!"
    echo "============================================================================"
    echo ""
    echo "Project ID: $PROJECT_ID"
    echo "Location: $LOCATION"
    echo "Service Account: ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    echo ""
    echo "Next Steps:"
    echo "1. Review and secure the service-account-key.json file"
    echo "2. Add service-account-key.json to .gitignore"
    echo "3. Update your Django settings with the environment variables"
    echo "4. Test the Document AI integration with sample invoices"
    echo ""
    echo "Useful Commands:"
    echo "- View project: gcloud config get-value project"
    echo "- List processors: gcloud beta ai document-processors list --location=$LOCATION"
    echo "- View logs: gcloud logging read 'resource.type=document_ai_processor'"
    echo ""
    echo "Documentation:"
    echo "- Document AI: https://cloud.google.com/document-ai/docs"
    echo "- Invoice Parser: https://cloud.google.com/document-ai/docs/processors-list#processor_invoice-processor"
    echo ""
    echo "============================================================================"
}

# Main execution flow
main() {
    echo "============================================================================"
    echo "           GOOGLE CLOUD DOCUMENT AI SETUP FOR FAKTULOVE"
    echo "============================================================================"
    echo ""
    
    # Check prerequisites
    check_gcloud
    
    # Authenticate
    authenticate_gcloud
    
    # Create and configure project
    create_project
    link_billing
    enable_apis
    
    # Set up service account
    create_service_account
    create_service_key
    
    # Create Document AI resources
    create_document_ai_processor
    create_storage_bucket
    
    # Set up monitoring
    setup_monitoring
    
    # Display summary
    display_summary
}

# Run main function
main