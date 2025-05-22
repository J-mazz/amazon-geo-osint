#!/bin/bash

# Project root name
PROJECT_NAME="amazon-geo-osint"

# Create folder structure
mkdir -p $PROJECT_NAME/{data/{raw,processed},notebooks,src/{ingest,preprocess,analysis},models,outputs,docs}

# Create essential files
touch $PROJECT_NAME/requirements.txt
touch $PROJECT_NAME/.gitignore
touch $PROJECT_NAME/README.md

# Starter README content
cat <<EOL > $PROJECT_NAME/README.md
# Amazon Geo-OSINT

An open-source geospatial intelligence project using satellite and aerial imagery to uncover pre-European settlements hidden in the Amazon rainforest. Leveraging AI and ML to process, analyze, and visualize dense canopy data for archaeological insights.

## Structure
- **data/**: Raw and processed imagery
- **src/**: Modular Python scripts (ingest, preprocess, ML analysis)
- **notebooks/**: Jupyter prototyping
- **models/**: Trained model weights
- **outputs/**: Resulting maps, annotations, etc.

## Getting Started
Install dependencies:
\`\`\`
pip install -r requirements.txt
\`\`\`

To run data download:
\`\`\`
python src/ingest/sentinel_downloader.py
\`\`\`
EOL

# Git ignore template
cat <<EOL > $PROJECT_NAME/.gitignore
__pycache__/
*.pyc
.env
*.tif
*.zip
data/raw/
models/
outputs/
EOL

echo "Project structure for '$PROJECT_NAME' created successfully."
