import os
import io
import time
import base64  
import requests
import argparse
from PIL import Image
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

# ===== CONFIGURATION =====
DEFAULT_OUTPUT_DIR = '/home/adam/Documents/GitHub/datasets/Graz_dataset'  # Change this to your preferred output directory
DEFAULT_MAX_IMAGES = 100           # Default number of images to download
MIN_IMAGE_WIDTH = 256            # Minimum image width in pixels (for full mode)
MIN_IMAGE_HEIGHT = 256            # Minimum image height in pixels (for full mode)
MIN_THUMB_WIDTH = 256             # Minimum width for thumbnail mode
MIN_THUMB_HEIGHT = 256            # Minimum height for thumbnail mode
# =========================

def scrape_google_images(query, max_images=DEFAULT_MAX_IMAGES, output_dir=DEFAULT_OUTPUT_DIR, full_size=False):
    """
    Scrape Google Images and download specified number of images.
    
    Args:
        query: Search query string
        max_images: Maximum number of images to download
        output_dir: Base directory for downloads
        full_size: If True, click thumbnails for full images (slower). If False, use thumbnails (faster)
    """
    # Convert the query into URL format
    query_url = quote(query)
    
    # Create subfolder with query name
    folder_name = os.path.join(output_dir, query.replace(' ', '_').replace('/', '_'))
    
    try:
        # Create the folder if it doesn't exist
        os.makedirs(folder_name, exist_ok=True)
        print(f"Saving images to: {folder_name}")
    except Exception as e:
        print(f"An error occurred creating folder: {str(e)}")
        return
    
    # Initialize Firefox with headless option (set to False if you want to see the browser)
    firefox_options = Options()
    # firefox_options.add_argument('--headless')  # Uncomment to run without GUI
    
    try:
        driver = webdriver.Firefox(options=firefox_options)
    except Exception as e:
        print(f"Error initializing Firefox driver: {str(e)}")
        print("Make sure Firefox and geckodriver are installed.")
        print("Install geckodriver: sudo apt install firefox-geckodriver")
        return
    
    try:
        # URL for Google Images search
        url = f"https://www.google.com/search?q={query_url}&tbm=isch"
        
        # Open the URL in the web browser
        driver.get(url)
        mode_text = "full-size (slow)" if full_size else "thumbnail (fast)"
        print(f"Searching for: {query} [{mode_text} mode]")
        time.sleep(1)
        
        images_downloaded = 0
        
        if full_size:
            # FULL-SIZE MODE: Click thumbnails to get original images (slower but better quality)
            min_w, min_h = MIN_IMAGE_WIDTH, MIN_IMAGE_HEIGHT
            images_processed = 0
            last_height = 0
            
            while images_downloaded < max_images:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                
                thumbnails = driver.find_elements(By.CSS_SELECTOR, 'img.rg_i, img.YQ4gaf, img.Q4LuWd')
                
                for idx in range(images_processed, len(thumbnails)):
                    if images_downloaded >= max_images:
                        break
                        
                    try:
                        thumbnail = thumbnails[idx]
                        driver.execute_script("arguments[0].scrollIntoView(true);", thumbnail)
                        time.sleep(0.3)
                        thumbnail.click()
                        time.sleep(1)
                        
                        # Find the full-size image
                        full_image_url = None
                        
                        try:
                            actual_images = driver.find_elements(By.CSS_SELECTOR, 'img.n3VNCb, img.sFlh5c, img.iPVvYb')
                            for actual_img in actual_images:
                                src = actual_img.get_attribute('src')
                                if src and src.startswith('http') and 'gstatic' not in src:
                                    full_image_url = src
                                    break
                        except:
                            pass
                        
                        if not full_image_url:
                            try:
                                img_elements = driver.find_elements(By.CSS_SELECTOR, 'img[src^="http"]')
                                for img_elem in img_elements:
                                    src = img_elem.get_attribute('src')
                                    if src and 'gstatic' not in src and 'google.com/images' not in src:
                                        try:
                                            width = img_elem.get_attribute('naturalWidth')
                                            if width and int(width) > 100:
                                                full_image_url = src
                                                break
                                        except:
                                            pass
                            except:
                                pass
                        
                        if full_image_url:
                            try:
                                img_response = requests.get(full_image_url, timeout=10)
                                img_check = Image.open(io.BytesIO(img_response.content))
                                width, height = img_check.size
                                
                                if width >= min_w and height >= min_h:
                                    img_name = f"{images_downloaded + 1}.jpg"
                                    img_path = os.path.join(folder_name, img_name)
                                    
                                    if img_check.mode in ('RGBA', 'LA', 'P'):
                                        img_check = img_check.convert('RGB')
                                    
                                    img_check.save(img_path, 'JPEG', quality=95)
                                    images_downloaded += 1
                                    print(f"✓ Downloaded {images_downloaded}/{max_images} ({width}x{height})")
                                else:
                                    print(f"✗ Skipped small ({width}x{height})")
                            except Exception as e:
                                print(f"✗ Error saving: {str(e)}")
                        else:
                            print(f"✗ No full-size URL found")
                    
                    except Exception as e:
                        continue
                    
                    images_processed = idx + 1
                
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height and len(thumbnails) <= images_processed:
                    break
                last_height = new_height
        
        else:
            # THUMBNAIL MODE: Fast download of thumbnail images
            min_w, min_h = MIN_THUMB_WIDTH, MIN_THUMB_HEIGHT
            scroll_pause = 0
            
            while images_downloaded < max_images:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                scroll_pause += 1
                
                img_elements = driver.find_elements(By.CSS_SELECTOR, 'img.rg_i, img.YQ4gaf, img.Q4LuWd')
                
                for img in img_elements:
                    if images_downloaded >= max_images:
                        break
                    
                    try:
                        img_url = img.get_attribute("src")
                        
                        if img_url and img_url.startswith('http'):
                            img_response = requests.get(img_url, timeout=5)
                            img_check = Image.open(io.BytesIO(img_response.content))
                            width, height = img_check.size
                            
                            if width >= min_w and height >= min_h:
                                img_name = f"{images_downloaded + 1}.jpg"
                                img_path = os.path.join(folder_name, img_name)
                                
                                if img_check.mode in ('RGBA', 'LA', 'P'):
                                    img_check = img_check.convert('RGB')
                                
                                img_check.save(img_path, 'JPEG', quality=90)
                                images_downloaded += 1
                                print(f"✓ Downloaded {images_downloaded}/{max_images} ({width}x{height})")
                            else:
                                print(f"✗ Skipped small ({width}x{height})")
                        
                        elif img_url and 'base64' in img_url:
                            img_data = img_url.split('base64,')[1]
                            img_check = Image.open(io.BytesIO(base64.b64decode(img_data)))
                            width, height = img_check.size
                            
                            if width >= min_w and height >= min_h:
                                img_name = f"{images_downloaded + 1}.jpg"
                                img_path = os.path.join(folder_name, img_name)
                                
                                if img_check.mode in ('RGBA', 'LA', 'P'):
                                    img_check = img_check.convert('RGB')
                                
                                img_check.save(img_path, 'JPEG', quality=90)
                                images_downloaded += 1
                                print(f"✓ Downloaded {images_downloaded}/{max_images} ({width}x{height})")
                            else:
                                print(f"✗ Skipped small ({width}x{height})")
                    
                    except:
                        continue
                
                # Stop if we've scrolled too much without progress
                if scroll_pause > 30:
                    break
        
        if images_downloaded >= max_images:
            print(f"\n✓ Successfully downloaded {images_downloaded} images!")
        else:
            print(f"\n⚠ Only found {images_downloaded} images (requested {max_images})")
        
        print(f"Images saved in: {folder_name}")
        
    finally:
        # Close the web browser
        driver.quit()

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Scrape images from Google Images')
    parser.add_argument('query', type=str, help='Search query for images')
    parser.add_argument('-n', '--num-images', type=int, default=DEFAULT_MAX_IMAGES, 
                        help=f'Maximum number of images to download (default: {DEFAULT_MAX_IMAGES})')
    parser.add_argument('-o', '--output-dir', type=str, default=DEFAULT_OUTPUT_DIR,
                        help=f'Output directory for downloaded images (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('-f', '--full', action='store_true',
                        help='Download full-size images by clicking thumbnails (slower but better quality)')
    
    args = parser.parse_args()
    
    scrape_google_images(args.query, args.num_images, args.output_dir, args.full)
