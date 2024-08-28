# Mosaic Matcher

## Overview

This project is an **Image Mosaic Generator**. It processes input images by dividing them into blocks and replacing each block with a small image from a dataset that closely matches the mean color of the block. The final output is an image where each block is a smaller image from the dataset, giving a mosaic effect.

## What it does

- **Image Mosaic Creation**: Convert any input image into a mosaic where each block is replaced by the closest matching image from a dataset based on mean color.
- **Progress Tracking**: Displays real-time progress and estimated completion time during image processing.
- **CSV Caching**: Caches the mean colors of images in a CSV file for faster reloading in future runs.

## Setup

1. **Install dependencies**:

   ```bash
   pip install numpy pillow asyncio
   ```

2. **Prepare Datasets**:
   Create a dataset folder inside the `datasets/` directory. Place images that will be used for mosaic creation inside this folder. For example:

   ```
   datasets/
   └── custom_dataset/
       ├── image1.jpg
       ├── image2.png
       └── image3.jpeg
   ```
   There is already a dataset with flower images for testing. I'd recommend going to https://www.kaggle.com/datasets to find datasets.

3. **Prepare Input Images**:
   Place the images you want to process in the `inputs/` directory.

## Usage

1. **Run the Script**:

   ```bash
   python main.py
   ```

2. **Enter Dataset Name**:
   After starting the script, you will be prompted to enter the dataset name (e.g., `custom_dataset`). Ensure that the dataset folder exists under the `datasets/` directory.

3. **Mosaic Creation**:
   The script will process all images in the `inputs/` directory and save the mosaic versions in the `outputs/` directory. Progress will be displayed in the terminal during processing.

## Configuration

- **Block Size**: You can modify the block size by changing the `block_size` variable in the script. This determines the size of the blocks in the mosaic. The smaller the number, the more detailed the output image will be BUT the longer it will take to process.

## Example
An example exists using a picture from gravity falls, with the input image being `image.png` and the output `dypju.jpg`
