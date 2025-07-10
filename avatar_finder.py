import os
import re
import requests
from bs4 import BeautifulSoup
import time
import argparse

# Try to import browser_cookie3 for cookie extraction
try:
    import browser_cookie3
    BROWSER_COOKIES_AVAILABLE = True
except ImportError:
    BROWSER_COOKIES_AVAILABLE = False

# Parse command line arguments
parser = argparse.ArgumentParser(description='Extract VRChat avatar IDs from cache')
parser.add_argument('--test', action='store_true', help='Test mode: only process first 5 folders')
parser.add_argument('--cookies-from-browser', choices=['firefox', 'chrome', 'edge', 'safari'], 
                    help='Extract cookies from browser for authentication')
args = parser.parse_args()

# Change this to your actual cache path
cache_dir = r"Cache-WindowsPlayer"  # Relative path to cache in current directory

# Set processing limit based on test mode
MAX_FOLDERS_TO_PROCESS = 5 if args.test else None

if args.test:
    print(f"🧪 TEST MODE: Processing only first {MAX_FOLDERS_TO_PROCESS} folders")
    
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
folders_processed = 0

print("Searching through cache files...")

# Get list of cache folders and optionally limit them for testing
if MAX_FOLDERS_TO_PROCESS:
    cache_folders = [d for d in os.listdir(cache_dir) if os.path.isdir(os.path.join(cache_dir, d))]
    limited_folders = cache_folders[:MAX_FOLDERS_TO_PROCESS]
    print(f"📊 Total cache folders found: {len(cache_folders)}")
    print(f"🚀 Processing folders: {limited_folders}")
    
    for folder_name in limited_folders:
        folders_processed += 1
        folder_path = os.path.join(cache_dir, folder_name)
        
        if args.test:
            print(f"\n📂 [{folders_processed}/{MAX_FOLDERS_TO_PROCESS}] Processing folder: {folder_name}")
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file == "__data":
                    files_processed += 1
                    
                    if files_processed % 50 == 0 and not args.test:
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
                                    if args.test:
                                        print(f"  🎯 Found avatar: {avatar_id}")
                                    else:
                                        print(f"🎯 Found avatar: {avatar_id} in folder {cache_folder}")
                                
                    except Exception as e:
                        # Silently skip files that can't be read
                        pass
else:
    # Original full processing code
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

def get_browser_cookies():
    """Extract cookies from specified browser"""
    if not args.cookies_from_browser:
        return None
    
    if not BROWSER_COOKIES_AVAILABLE:
        print("❌ browser_cookie3 not installed. Install with: pip install browser_cookie3")
        return None
    
    try:
        print(f"🍪 Extracting cookies from {args.cookies_from_browser}...")
        
        if args.cookies_from_browser == 'firefox':
            cookies = browser_cookie3.firefox(domain_name='vrchat.com')
        elif args.cookies_from_browser == 'chrome':
            cookies = browser_cookie3.chrome(domain_name='vrchat.com')
        elif args.cookies_from_browser == 'edge':
            cookies = browser_cookie3.edge(domain_name='vrchat.com')
        elif args.cookies_from_browser == 'safari':
            cookies = browser_cookie3.safari(domain_name='vrchat.com')
        else:
            return None
        
        # Convert to requests-compatible format
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie.name] = cookie.value
        
        print(f"✅ Extracted {len(cookie_dict)} cookies from {args.cookies_from_browser}")
        return cookie_dict
        
    except Exception as e:
        print(f"❌ Failed to extract cookies from {args.cookies_from_browser}: {e}")
        print("💡 Make sure the browser is closed and you're logged into VRChat")
        return None

def test_avatar_fetch(avatar_id, cookies=None):
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
        if cookies:
            print(f"🍪 Using {len(cookies)} cookies for authentication")
            response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        else:
            print("🔓 Making unauthenticated request")
            response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📏 Content Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Debug: Print the title to see what page we got
            title = soup.find('title')
            if title:
                print(f"📄 Page Title: {title.get_text(strip=True)}")
            
            # Look for avatar name in meta tags (Twitter/OpenGraph)
            # VRChat uses SPA so the name is in meta tags, not rendered HTML
            twitter_title = soup.find('meta', property='twitter:title') or soup.find('meta', attrs={'name': 'twitter:title'})
            og_title = soup.find('meta', property='og:title') or soup.find('meta', attrs={'property': 'og:title'})
            
            avatar_name = None
            if twitter_title and twitter_title.get('content'):
                avatar_name = twitter_title.get('content').strip()
                print(f"✅ Found avatar name in Twitter meta: {avatar_name}")
            elif og_title and og_title.get('content'):
                avatar_name = og_title.get('content').strip()
                print(f"✅ Found avatar name in OpenGraph meta: {avatar_name}")
            
            if avatar_name:
                return avatar_name
            else:
                print("❌ Avatar name not found in meta tags")
                
                # Check if we're being redirected to login
                if "login" in response.url.lower() or "sign" in response.url.lower():
                    print("🔒 Redirected to login page")
                    return "Redirected to login"
                
                # Check if the page contains the avatar ID (indicates avatar exists)
                page_text = soup.get_text()
                if avatar_id in page_text:
                    print(f"⚠️  Avatar exists but name not found in meta tags")
                    return "Avatar exists - name not accessible"
                else:
                    print(f"❌ Avatar {avatar_id} not found - may not exist")
                    return "Avatar not found"
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
    
    # Extract cookies if requested
    cookies = get_browser_cookies()
    
    print(f"\n🧪 TESTING WITH FIRST AVATAR:")
    print(f"Avatar ID: {first_avatar_id}")
    print(f"Cache Folder: {first_folder}")
    
    test_result = test_avatar_fetch(first_avatar_id, cookies)
    
    print(f"\n📋 TEST RESULT: {test_result}")
    test_success = 'Error' not in test_result and 'not found' not in test_result and 'Redirected' not in test_result
    
    if args.test:
        # Test mode - just create simple output
        print(f"\n❓ The test {'succeeded' if test_success else 'failed'}.")
        print(f"There are {len(found_avatars)} total avatars to process.")
        
        print("\n📄 Creating test output file...")
        with open("vrchat_avatars_test.txt", "w", encoding="utf-8") as f:
            f.write(f"VRChat Avatar URLs and Cache Folders (TEST - First 5 folders only)\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Test Result: {test_result}\n\n")
            
            for avatar_id, folder_name in found_avatars.items():
                url = f"https://vrchat.com/home/avatar/{avatar_id}"
                f.write(f"URL: {url}\n")
                f.write(f"Cache Folder: {folder_name}\n")
                f.write("-" * 40 + "\n\n")
        
        print(f"✅ Test results saved to 'vrchat_avatars_test.txt'")
    else:
        # Full mode - fetch names for all avatars
        if test_success and cookies:
            print(f"\n🚀 SUCCESS! Now fetching names for all {len(found_avatars)} avatars...")
            print("This may take several minutes...")
            
            def get_avatar_name_simple(avatar_id, cookies):
                """Simple version of avatar name fetching for batch processing"""
                url = f"https://vrchat.com/home/avatar/{avatar_id}"
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        twitter_title = soup.find('meta', property='twitter:title') or soup.find('meta', attrs={'name': 'twitter:title'})
                        og_title = soup.find('meta', property='og:title') or soup.find('meta', attrs={'property': 'og:title'})
                        
                        if twitter_title and twitter_title.get('content'):
                            return twitter_title.get('content').strip()
                        elif og_title and og_title.get('content'):
                            return og_title.get('content').strip()
                    
                    return "Name not found"
                except Exception:
                    return "Error fetching name"
            
            # Fetch names for all avatars
            with open("vrchat_avatars_with_names.txt", "w", encoding="utf-8") as f:
                f.write("VRChat Avatar URLs with Names and Cache Folders\n")
                f.write("=" * 60 + "\n\n")
                
                for i, (avatar_id, folder_name) in enumerate(found_avatars.items(), 1):
                    print(f"Fetching name for avatar {i}/{len(found_avatars)}: {avatar_id}")
                    
                    url = f"https://vrchat.com/home/avatar/{avatar_id}"
                    avatar_name = get_avatar_name_simple(avatar_id, cookies)
                    
                    f.write(f"Avatar: {avatar_name}\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"Cache Folder: {folder_name}\n")
                    f.write("-" * 40 + "\n\n")
                    
                    # Small delay to be respectful to the server
                    time.sleep(0.5)
            
            print(f"\n✅ Complete results saved to 'vrchat_avatars_with_names.txt'")
            print(f"🎉 Successfully processed {len(found_avatars)} avatars with names!")
        else:
            print(f"\n⚠️  Test failed or no cookies available. Creating simple list without names...")
            with open("vrchat_avatars_simple.txt", "w", encoding="utf-8") as f:
                f.write("VRChat Avatar URLs and Cache Folders\n")
                f.write("=" * 50 + "\n\n")
                
                for avatar_id, folder_name in found_avatars.items():
                    url = f"https://vrchat.com/home/avatar/{avatar_id}"
                    f.write(f"URL: {url}\n")
                    f.write(f"Cache Folder: {folder_name}\n")
                    f.write("-" * 40 + "\n\n")
            
            print(f"✅ Simple list saved to 'vrchat_avatars_simple.txt'")
            print(f"💡 To get names, make sure you're logged into Firefox and run with --cookies-from-browser firefox")
else:
    print("❌ No avatars found to test with") 