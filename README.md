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
```
pip install -r requirements.txt
```

To run data download:
```
python src/ingest/sentinel_downloader.py
```
