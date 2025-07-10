import os
import re
import requests
from bs4 import BeautifulSoup
import time

# Change this to your actual cache path
cache_dir = r"Cache-WindowsPlayer"  # Relative path to cache in current directory

print(f"Searching for avatar IDs in: {cache_dir}")
print("=" * 50)

if not os.path.exists(cache_dir):
    print(f"Error: Directory {cache_dir} does not exist!")
    exit(1)

print("Directory exists, starting search...")

# Pattern to match VRChat avatar IDs (avtr_ followed by UUID format)
avatar_pattern = re.compile(rb'avtr_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

found_avatars = {}  # Use dict to store avatar_id -> folder_name mapping
files_processed = 0

print("Searching through cache files...")

for root, dirs, files in os.walk(cache_dir):
    for file in files:
        if file == "__data":
            files_processed += 1
            
            if files_processed % 50 == 0:
                print(f"Processed {files_processed} files...")
            
            try:
                with open(os.path.join(root, file), 'rb') as f:
                    content = f.read()
                    
                    matches = avatar_pattern.findall(content)
                    for match in matches:
                        avatar_id = match.decode('utf-8')
                        # Get the cache folder name (first folder after Cache-WindowsPlayer)
                        path_parts = root.split(os.sep)
                        cache_folder = None
                        for i, part in enumerate(path_parts):
                            if part == "Cache-WindowsPlayer" and i + 1 < len(path_parts):
                                cache_folder = path_parts[i + 1]
                                break
                        
                        if cache_folder:
                            found_avatars[avatar_id] = cache_folder
                            print(f"🎯 Found avatar: {avatar_id} in folder {cache_folder}")
                        
            except Exception as e:
                # Silently skip files that can't be read
                pass

print(f"\nSearch complete! Processed {files_processed} files.")
print(f"Found {len(found_avatars)} unique avatars.")

def get_avatar_name(avatar_id):
    """Fetch avatar name from VRChat website"""
    url = f"https://vrchat.com/home/avatar/{avatar_id}"
    
    try:
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for the avatar name in the h2 element
        name_element = soup.find('h2', class_='tw-mb-0 tw-text-truncate tw-line-clamp-1 tw-break-all tw-leading-[1.25] tw-flex-grow')
        
        if name_element:
            return name_element.get_text(strip=True)
        else:
            return "Name not found"
            
    except Exception as e:
        return f"Error fetching name: {str(e)}"

# Write results to file with names
print("\nFetching avatar names from VRChat...")
with open("vrchat_avatars.txt", "w", encoding="utf-8") as f:
    f.write("VRChat Avatar URLs with Names and Cache Folders\n")
    f.write("=" * 60 + "\n\n")
    
    for i, (avatar_id, folder_name) in enumerate(found_avatars.items(), 1):
        url = f"https://vrchat.com/home/avatar/{avatar_id}"
        
        # Show progress
        print(f"Fetching name for avatar {i}/{len(found_avatars)}: {avatar_id}")
        
        # Get the avatar name
        avatar_name = get_avatar_name(avatar_id)
        
        # Write to file
        f.write(f"Avatar: {avatar_name}\n")
        f.write(f"URL: {url}\n")
        f.write(f"Cache Folder: {folder_name}\n")
        f.write("-" * 40 + "\n\n")
        
        # Add a small delay to be respectful to the server
        time.sleep(0.5)

print(f"\nResults saved to 'vrchat_avatars.txt'")
print(f"Found {len(found_avatars)} unique avatars with names and cache folder locations!") 