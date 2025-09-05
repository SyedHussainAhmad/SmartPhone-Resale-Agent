import requests
from .state_schema import ImageUnderstandingState
from dotenv import load_dotenv
import os

load_dotenv()

IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
BING_END_POINT= os.getenv("BING_END_POINT")

def search_by_image(state: ImageUnderstandingState) -> ImageUnderstandingState:
    image_path = state["image_path"]
    
    print(f"🔍 Processing image: {image_path}")

    os_path = image_path.replace('/', os.sep)
    
    if not os.path.exists(os_path):
        raise FileNotFoundError(f"Image file not found at path: {os_path}")
    
    if not os.path.isfile(os_path):
        raise ValueError(f"Path exists but is not a file: {os_path}")
    
    try:
        file_size = os.path.getsize(os_path)
        if file_size == 0:
            raise ValueError(f"Image file is empty: {os_path}")
        
        print(f"File validation passed: {os_path} (size: {file_size} bytes)")
        
    except OSError as e:
        raise OSError(f"Cannot access file {os_path}: {e}")
    
    # Check API key
    if not IMGBB_API_KEY:
        raise ValueError("IMGBB_API_KEY not found in environment variables")
    
    try:
        with open(os_path, "rb") as file:
            file_content = file.read()
            if not file_content:
                raise ValueError("File is empty or cannot be read")
            
            file.seek(0)
            
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": IMGBB_API_KEY},
                files={"image": ("image.jpg", file, "image/jpeg")},
                timeout=60  # Increased timeout
            )
            
        print(f"ImgBB response status: {response.status_code}")
        
        if response.status_code != 200:
            raise requests.RequestException(f"ImgBB API returned status {response.status_code}: {response.text}")
            
    # Exceptions just to handle errors of any type
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find image file: {os_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied accessing file: {os_path}")
    except requests.exceptions.Timeout:
        raise TimeoutError("ImgBB upload timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error during upload: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during file upload: {e}")

    # Parse response
    try:
        imgbb_data = response.json()
    except ValueError as e:
        raise ValueError(f"Invalid JSON response from ImgBB: {response.text}")

    if "data" not in imgbb_data:
        if "error" in imgbb_data:
            error_msg = imgbb_data.get("error", {}).get("message", "Unknown error")
            raise ValueError(f"ImgBB upload failed: {error_msg}")
        else:
            raise ValueError(f"Unexpected ImgBB response structure: {imgbb_data}")
    
    if "url" not in imgbb_data["data"]:
        raise ValueError(f"ImgBB response missing URL: {imgbb_data}")

    uploaded_url = imgbb_data["data"]["url"]
    print(f"Successfully uploaded to ImgBB: {uploaded_url}")

    if not RAPID_API_KEY:
        raise ValueError("RAPID_API_KEY not found in environment variables")
    
    try:
        print(f"Starting Bing Visual Search...")
        
        search_response = requests.get(
            BING_END_POINT,
            headers={
                "X-RapidAPI-Host": "bing-image-search5.p.rapidapi.com",
                "X-RapidAPI-Key": RAPID_API_KEY
            },
            params={"query_url": uploaded_url},
            timeout=60
        )

        print(f"Bing Visual Search response status: {search_response.status_code}")
        
        if search_response.status_code != 200:
            raise requests.RequestException(
                f"Bing visual search failed. Status: {search_response.status_code}, "
                f"Response: {search_response.text}"
            )

        search_results = search_response.json()
        print(f"Visual search completed successfully")

    # Exceptions just to handle errors of any type
    except requests.exceptions.Timeout:
        raise TimeoutError("Bing Visual Search timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Bing Visual Search API error: {e}")
    except ValueError as e:
        raise ValueError(f"Invalid JSON response from Bing Visual Search: {search_response.text}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during visual search: {e}")

    state["uploaded_image_url"] = uploaded_url
    state["search_results"] = search_results

    print(f"Image processing completed successfully")
    return state
