import os
import html
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def download_olipop_svg_images():
    url = "https://drinkolipop.com/collections/shop-9g-fiber"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Target class configuration string
    target_class = "tw-pointer-events-none tw-absolute tw-inset-0 tw-z-[2] tw-hidden lg:tw-block"
    output_dir = "olipop_images_fixed"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Fetching page: {url}...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Connection error: {e}")
        return

    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find your specific target containers
    containers = soup.find_all("div", class_=target_class)
    print(f"Found {len(containers)} matching container elements.")
    
    download_count = 0
    
    for index, container in enumerate(containers):
        # Target the SVG <image> element instead of a standard <img> element
        svg_image_tag = container.find("image")
        
        if not svg_image_tag:
            continue
            
        # Extract the URL from either 'href' or 'xlink:href' attributes
        img_url = svg_image_tag.get("href") or svg_image_tag.get("xlink:href")
        
        if not img_url:
            continue
            
        # 1. Correctly unescape HTML entities (converts &amp; back into &)
        img_url = html.unescape(img_url)
        
        # 2. Fix protocol-relative URLs (//cdn... -> https://cdn...)
        if img_url.startswith("//"):
            img_url = f"https:{img_url}"
            
        # 3. Create absolute path structure if necessary
        img_url = urljoin(url, img_url)
        
        # 4. Generate a clean filename based on the asset name in the URL
        url_path_file = img_url.split("/")[-1].split("?")[0]
        if url_path_file:
            filename = f"{index + 1}_{url_path_file}"
        else:
            filename = f"olipop_img_{index + 1}.webp"
            
        file_path = os.path.join(output_dir, filename)
        
        # Download and write the data stream
        try:
            print(f"Downloading [{index + 1}/{len(containers)}]: {img_url}")
            img_data = requests.get(img_url, headers=headers).content
            with open(file_path, 'wb') as handler:
                handler.write(img_data)
            download_count += 1
        except Exception as e:
            print(f"Failed downloading {img_url}: {e}")

    print(f"\nFinished! Successfully downloaded {download_count} SVG embedded images into '{output_dir}'.")

if __name__ == "__main__":
    download_olipop_svg_images()
