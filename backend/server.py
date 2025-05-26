from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
import os
import random
from supabase import create_client, Client

app = FastAPI()
load_dotenv() 
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NAMES = ["PixelPioneer", "LinkWizard", "MetaMancer", "SnapScout", "ByteSaver"]

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def extract_metadata(url: str) -> dict:
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        
        title = soup.title.string if soup.title else "No title"
        description = (
            soup.find("meta", attrs={"name": "description"}) or
            soup.find("meta", attrs={"property": "og:description"})
        )
        description = description["content"] if description and "content" in description.attrs else "No description"

        favicon = soup.find("link", rel="icon")
        favicon_url = favicon["href"] if favicon and "href" in favicon.attrs else "/favicon.ico"
        if favicon_url.startswith("/"):
            parsed_url = urlparse(url)
            favicon_url = f"{parsed_url.scheme}://{parsed_url.netloc}{favicon_url}"

        og_image = soup.find("meta", attrs={"property": "og:image"})
        og_thumbnail = og_image["content"] if og_image and "content" in og_image.attrs else None

        return {
            "title": title,
            "description": description,
            "favicon": favicon_url,
            "og_thumbnail": og_thumbnail
        }
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return {
            "title": "Unknown",
            "description": "Could not extract metadata.",
            "favicon": "",
            "og_thumbnail": None
        }

def archive_url(url: str) -> str:
    try:
        save_resp = requests.get(f"https://web.archive.org/save/{url}", timeout=30)
        if save_resp.status_code in [200, 302]:
            return f"https://web.archive.org/web/*/{url}"
        else:
            print(f"Archive status code: {save_resp.status_code}")
            return ""
    except requests.Timeout:
        print("Wayback Machine request timed out.")
        return ""
    except Exception as e:
        print(f"Error archiving URL: {e}")
        return ""

def get_screenshot_url(url: str) -> str:
    try:
        api_key = os.getenv("SCREENSHOT_API")
        return f"https://shot.screenshotapi.net/screenshot?token={api_key}&url={url}&output=image&file_type=png"
    except Exception as e:
        print(f"Error generating screenshot URL: {e}")
        return ""
    
@app.post("/save-bookmark")
async def save_bookmark(request: Request):
    data = await request.json()
    url = data.get("url")

    if not url or not is_valid_url(url):
        return {"status": 0 ,"error": "Invalid URL"}

    metadata = extract_metadata(url)
    archive_url_value = archive_url(url)
    screenshot_url = get_screenshot_url(url)
    random_name = random.choice(NAMES)

    data = {
        "url": url,
        "title": metadata["title"],
        "description": metadata["description"],
        "favicon": metadata["favicon"],
        "og_thumbnail": metadata["og_thumbnail"],
        "archive_url": archive_url_value,
        "screenshot_url": screenshot_url,
        "generated_by": random_name
    }

    try:
        response = supabase.table("Bookmark").select("id", "data").single().execute()
        row = response.data 

        existing_data = row["data"] if "data" in row else []
        
        existing_data.append(data)
        
        supabase.table("Bookmark").update({"data": existing_data}).eq("id", row["id"]).execute()
    except Exception as e:
        print(f"Error inserting bookmark: {e}")
        return {"status": 0 ,"error": "Failed to save bookmark"}


    return {"status": 1}

@app.get("/fetch-bookmark")
async def fetch_bookmark():
    try:
        response = supabase.table("Bookmark").select("data").execute()
        if response.data:
            return {"bookmarks": response.data}
        else:
            return {"message": "No bookmarks found."}
    except Exception as e:
        print(f"Error fetching bookmarks: {e}")
        return {"error": "Failed to fetch bookmarks."}

@app.get("/")
async def main_page():
    print("Server is running!")
    return {"message": "Welcome to the Bookmark Manager API!"}