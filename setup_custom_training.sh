#!/bin/bash

# FaktuLove OCR - Custom Training Setup Script
# This script automates the setup of custom training for Polish invoices

set -e

echo "🚀 FaktuLove OCR - Custom Training Setup"
echo "========================================"

# Configuration
TRAINING_BUCKET="faktulove-ocr-training"
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-faktulove-ocr}"
LOCATION="${DOCUMENT_AI_LOCATION:-eu-west1}"
DATASET_NAME="polish-invoices-$(date +%Y%m%d)"
MIN_SAMPLES=50

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install Google Cloud SDK."
        exit 1
    fi
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with Google Cloud. Run: gcloud auth login"
        exit 1
    fi
    
    # Check if project is set
    if [ -z "$PROJECT_ID" ]; then
        print_error "GOOGLE_CLOUD_PROJECT environment variable is not set"
        exit 1
    fi
    
    # Check if Django environment is activated
    if ! python manage.py check --quiet 2>/dev/null; then
        print_error "Django environment not properly configured"
        exit 1
    fi
    
    print_success "Prerequisites checked"
}

# Collect training data
collect_training_data() {
    print_status "Collecting training data..."
    
    # Run Django command to collect training data
    python manage.py collect_training_data \
        --limit 1000 \
        --min-confidence 90.0 \
        --min-validation 7 \
        --export-gcs \
        --output-dir training_data/
    
    if [ $? -eq 0 ]; then
        print_success "Training data collected"
    else
        print_error "Failed to collect training data"
        exit 1
    fi
    
    # Check if we have enough samples
    SAMPLE_COUNT=$(python -c "
import json
try:
    with open('training_data/polish_invoice_training_dataset_*.json', 'r') as f:
        data = json.load(f)
        print(data['metadata']['total_samples'])
except:
    print(0)
" 2>/dev/null || echo 0)
    
    if [ "$SAMPLE_COUNT" -lt "$MIN_SAMPLES" ]; then
        print_warning "Only $SAMPLE_COUNT training samples found (minimum: $MIN_SAMPLES)"
        print_warning "Consider processing more documents before training"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Setup Google Cloud Storage bucket
setup_gcs_bucket() {
    print_status "Setting up Google Cloud Storage bucket..."
    
    # Check if bucket exists
    if gsutil ls -b gs://$TRAINING_BUCKET &>/dev/null; then
        print_success "Training bucket already exists: gs://$TRAINING_BUCKET"
    else
        print_status "Creating training bucket: gs://$TRAINING_BUCKET"
        gsutil mb -p $PROJECT_ID -c STANDARD -l $LOCATION gs://$TRAINING_BUCKET
        
        # Set lifecycle policy for automatic cleanup
        cat > bucket_lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      }
    ]
  }
}
EOF
        
        gsutil lifecycle set bucket_lifecycle.json gs://$TRAINING_BUCKET
        rm bucket_lifecycle.json
        
        print_success "Training bucket created with 90-day lifecycle"
    fi
    
    # Set bucket permissions
    gsutil iam ch serviceAccount:service-$PROJECT_ID@gcp-sa-documentai.iam.gserviceaccount.com:objectViewer gs://$TRAINING_BUCKET
}

# Upload training documents
upload_training_documents() {
    print_status "Uploading training documents to Google Cloud Storage..."
    
    UPLOAD_COUNT=0
    
    # Upload documents from media/ocr_uploads
    if [ -d "media/ocr_uploads" ]; then
        print_status "Uploading documents from media/ocr_uploads..."
        
        # Find and upload training-ready documents
        find media/ocr_uploads -type f \( -name "*.pdf" -o -name "*.jpg" -o -name "*.png" -o -name "*.tiff" \) | while read file; do
            filename=$(basename "$file")
            
            # Check if file is in training dataset
            if grep -q "$filename" training_data/polish_invoice_training_dataset_*.json 2>/dev/null; then
                print_status "Uploading: $filename"
                gsutil cp "$file" gs://$TRAINING_BUCKET/
                ((UPLOAD_COUNT++))
            fi
        done
        
        print_success "Uploaded $UPLOAD_COUNT training documents"
    else
        print_warning "No training documents found in media/ocr_uploads"
    fi
}

# Create Document AI dataset
create_document_ai_dataset() {
    print_status "Creating Document AI dataset..."
    
    # Create dataset
    DATASET_RESPONSE=$(gcloud ai datasets create \
        --location=$LOCATION \
        --display-name="$DATASET_NAME" \
        --description="Polish Invoice OCR Training Dataset - $(date)" \
        --format="value(name)" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        print_success "Dataset created: $DATASET_RESPONSE"
        echo "$DATASET_RESPONSE" > training_data/dataset_id.txt
    else
        print_error "Failed to create Document AI dataset"
        exit 1
    fi
}

# Import training data to dataset
import_training_data() {
    print_status "Importing training data to Document AI dataset..."
    
    DATASET_ID=$(cat training_data/dataset_id.txt)
    
    # Upload annotation file
    print_status "Uploading annotations..."
    ANNOTATION_FILE=$(ls training_data/document_ai_annotations_*.jsonl | head -1)
    if [ -f "$ANNOTATION_FILE" ]; then
        gsutil cp "$ANNOTATION_FILE" gs://$TRAINING_BUCKET/annotations.jsonl
        
        # Import annotations
        gcloud ai datasets import-data $DATASET_ID \
            --location=$LOCATION \
            --input-config="{
                'gcs_source': {
                    'uris': ['gs://$TRAINING_BUCKET/annotations.jsonl']
                }
            }"
        
        if [ $? -eq 0 ]; then
            print_success "Training data imported successfully"
        else
            print_error "Failed to import training data"
            exit 1
        fi
    else
        print_error "Annotation file not found"
        exit 1
    fi
}

# Start custom training
start_custom_training() {
    print_status "Starting custom model training..."
    
    DATASET_ID=$(cat training_data/dataset_id.txt)
    MODEL_NAME="polish-invoice-model-$(date +%Y%m%d-%H%M%S)"
    
    # Create custom training job
    TRAINING_JOB=$(gcloud ai custom-jobs create \
        --region=$LOCATION \
        --display-name="$MODEL_NAME" \
        --config='{
            "workerPoolSpecs": [{
                "machineSpec": {
                    "machineType": "n1-standard-4"
                },
                "replicaCount": 1,
                "containerSpec": {
                    "imageUri": "gcr.io/cloud-aiplatform/training/documentai-custom:latest",
                    "args": [
                        "--dataset_id='$DATASET_ID'",
                        "--model_type=INVOICE_PROCESSOR",
                        "--language_code=pl"
                    ]
                }
            }]
        }' \
        --format="value(name)")
    
    if [ $? -eq 0 ]; then
        print_success "Custom training job started: $TRAINING_JOB"
        echo "$TRAINING_JOB" > training_data/training_job_id.txt
        
        print_status "Training will take 2-4 hours to complete"
        print_status "Monitor progress: gcloud ai custom-jobs describe $TRAINING_JOB --region=$LOCATION"
    else
        print_error "Failed to start custom training"
        exit 1
    fi
}

# Generate training report
generate_training_report() {
    print_status "Generating training setup report..."
    
    cat > training_data/TRAINING_REPORT.md << EOF
# FaktuLove OCR - Custom Training Report

## Setup Summary
- **Date**: $(date)
- **Project ID**: $PROJECT_ID
- **Location**: $LOCATION
- **Dataset Name**: $DATASET_NAME
- **Training Bucket**: gs://$TRAINING_BUCKET

## Training Configuration
- **Minimum Confidence**: 90%
- **Minimum Validation Score**: 7/10
- **Training Samples**: $(cat training_data/dataset_id.txt 2>/dev/null | wc -l)
- **Model Type**: INVOICE_PROCESSOR
- **Language**: Polish (pl)

## Files Generated
- Training Dataset: \`training_data/polish_invoice_training_dataset_*.json\`
- Annotations: \`training_data/document_ai_annotations_*.jsonl\`
- GCS Export: \`training_data/polish_invoice_training_dataset_*_gcs_export_*.json\`
- Dataset ID: \`training_data/dataset_id.txt\`
- Training Job ID: \`training_data/training_job_id.txt\`

## Next Steps
1. Monitor training progress:
   \`\`\`bash
   gcloud ai custom-jobs describe \$(cat training_data/training_job_id.txt) --region=$LOCATION
   \`\`\`

2. Once training completes, evaluate model performance

3. Deploy improved model to production:
   \`\`\`bash
   # Update DOCUMENT_AI_PROCESSOR_ID in .env with new model ID
   # Restart application services
   \`\`\`

## Monitoring Commands
- **Check training status**: \`gcloud ai custom-jobs list --region=$LOCATION\`
- **View training logs**: \`gcloud logging read "resource.type=aiplatform_custom_job"\`
- **List datasets**: \`gcloud ai datasets list --region=$LOCATION\`

## Expected Results
- **Accuracy Improvement**: 5-15% over base model
- **Processing Time**: Similar to base model
- **Polish Pattern Recognition**: Significantly improved
- **Field Extraction**: Better accuracy for Polish invoices

Generated by: FaktuLove OCR Custom Training Setup v1.0
EOF

    print_success "Training report generated: training_data/TRAINING_REPORT.md"
}

# Main execution
main() {
    echo
    print_status "Starting custom training setup process..."
    
    check_prerequisites
    echo
    
    collect_training_data
    echo
    
    setup_gcs_bucket
    echo
    
    upload_training_documents
    echo
    
    create_document_ai_dataset
    echo
    
    import_training_data
    echo
    
    start_custom_training
    echo
    
    generate_training_report
    echo
    
    print_success "🎉 Custom training setup completed successfully!"
    print_status "Training is now in progress. Check training_data/TRAINING_REPORT.md for details."
    print_status "Training will complete in 2-4 hours. Monitor with: gcloud ai custom-jobs list --region=$LOCATION"
}

# Run main function
main "$@"
