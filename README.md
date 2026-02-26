# Google Image Scraper

## Description
This Python script allows you to scrape images from Google Images based on a specified search query and save them to your local machine. It utilizes Selenium and Firefox to automate the image retrieval process.

**Purpose:** The primary goal of this project is to create a dataset for training machine learning and artificial intelligence models in an automated manner.

## Installation

### 1. Clone this repository to your local machine:
```bash
git clone https://github.com/mahmutovichana/Google-Image-Scraper.git
```

### 2. Navigate to the project folder:
```bash
cd Google-Image-Scraper
```

### 3. Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Install Firefox and geckodriver (Linux):
```bash
# Install Firefox (if not already installed)
sudo apt update
sudo apt install firefox

# Install geckodriver
sudo apt install firefox-geckodriver
```

For other operating systems, download geckodriver from:
https://github.com/mozilla/geckodriver/releases

## Usage

Run the script with a search query:
```bash
python googleImageScraper.py "your search query"
```

### Command-line Options:

- **Query** (required): The search term for images
- **-n, --num-images**: Number of images to download (default: 10)
- **-o, --output-dir**: Output directory for downloads (default: downloads)
- **-f, --full**: Download full-size original images (slower) instead of thumbnails (default: thumbnails/fast mode)

### Examples:

Download 10 thumbnail images of cats (default - FAST):
```bash
python googleImageScraper.py "cats"
```

Download 20 full-size images of mountains (slower but higher quality):
```bash
python googleImageScraper.py "mountains" -n 20 --full
```

Download 50 thumbnail images of cars to a custom directory:
```bash
python googleImageScraper.py "sports cars" -n 50 -o my_images
```

### Speed vs Quality:

- **Default (Fast)**: Downloads thumbnails quickly (~200x200 to 400x400 pixels), great for datasets
- **Full Mode (-f)**: Clicks each thumbnail to get original images (larger, better quality, but much slower)

Choose thumbnail mode for speed or full mode (`-f`) when you need high-resolution images.

### Output Structure:

Images will be saved in subfolders named after the query:
```
downloads/
├── cats/
│   ├── 1.jpg
│   ├── 2.jpg
│   └── ...
└── mountains/
    ├── 1.jpg
    ├── 2.jpg
    └── ...
```

## Features

- ✓ Uses Firefox browser (Linux-compatible)
- ✓ Fast thumbnail mode (default) or full-size image mode (--full flag)
- ✓ Specify number of images to download
- ✓ Automatic subfolder creation for each query
- ✓ Minimum resolution filtering
- ✓ Stops when max number of images is reached
- ✓ Command-line interface for easy use
- ✓ Progress tracking during download

## Dependencies:
- Python 3.x
- Selenium
- Pillow (PIL)
- Requests
- Firefox browser
- geckodriver (Firefox WebDriver)
