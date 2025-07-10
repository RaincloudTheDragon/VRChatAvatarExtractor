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

def test_avatar_fetch(avatar_id):
    """Test fetching one avatar with detailed debugging"""
    url = f"https://vrchat.com/home/avatar/{avatar_id}"
    
    print(f"\n🧪 TESTING: {url}")
    
    try:
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print("📡 Making request...")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📏 Content Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Debug: Print the title to see what page we got
            title = soup.find('title')
            if title:
                print(f"📄 Page Title: {title.get_text(strip=True)}")
            
            # Look for the avatar name in the h2 element
            name_element = soup.find('h2', class_='tw-mb-0 tw-text-truncate tw-line-clamp-1 tw-break-all tw-leading-[1.25] tw-flex-grow')
            
            if name_element:
                name = name_element.get_text(strip=True)
                print(f"✅ Found avatar name: {name}")
                return name
            else:
                print("❌ Avatar name element not found")
                # Debug: Look for any h2 elements
                h2_elements = soup.find_all('h2')
                print(f"🔍 Found {len(h2_elements)} h2 elements:")
                for i, h2 in enumerate(h2_elements[:3]):  # Show first 3
                    print(f"  {i+1}: {h2.get_text(strip=True)[:50]}...")
                
                # Check if we're being redirected to login
                if "login" in response.url.lower() or "sign" in response.url.lower():
                    print("🔒 Looks like we're being redirected to login page")
                
                return "Name not found - may require login"
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return f"HTTP Error: {response.status_code}"
            
    except Exception as e:
        print(f"💥 Exception: {str(e)}")
        return f"Error: {str(e)}"

# Test with just the first avatar
if found_avatars:
    first_avatar_id = list(found_avatars.keys())[0]
    first_folder = found_avatars[first_avatar_id]
    
    print(f"\n🧪 TESTING WITH FIRST AVATAR:")
    print(f"Avatar ID: {first_avatar_id}")
    print(f"Cache Folder: {first_folder}")
    
    test_result = test_avatar_fetch(first_avatar_id)
    
    print(f"\n📋 TEST RESULT: {test_result}")
    
    # Ask user if they want to continue
    print(f"\n❓ The test {'succeeded' if 'Error' not in test_result and 'not found' not in test_result else 'failed'}.")
    print(f"There are {len(found_avatars)} total avatars to process.")
    print("Would you like to continue with all avatars? (This will take several minutes)")
    
    # For now, let's just create a simple output file without names
    print("\n📄 Creating simple output file without web scraping...")
    with open("vrchat_avatars_simple.txt", "w", encoding="utf-8") as f:
        f.write("VRChat Avatar URLs and Cache Folders\n")
        f.write("=" * 50 + "\n\n")
        
        for avatar_id, folder_name in found_avatars.items():
            url = f"https://vrchat.com/home/avatar/{avatar_id}"
            f.write(f"URL: {url}\n")
            f.write(f"Cache Folder: {folder_name}\n")
            f.write("-" * 40 + "\n\n")
    
    print(f"✅ Simple list saved to 'vrchat_avatars_simple.txt'")
    print(f"🔗 You can manually check the test URL to see if it works in your browser")
else:
    print("❌ No avatars found to test with") 