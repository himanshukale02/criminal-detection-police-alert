import requests
import os
from config import IMGBB_API_KEY  

def upload_to_imgbb(image_path):
   
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY
    }

    try:
        with open(image_path, "rb") as img_file:
            files = {
                "image": img_file
            }
            response = requests.post(url, data=payload, files=files)

        if response.status_code == 200:
            return response.json()["data"]["url"]
        else:
            print("❌ Upload failed:", response.status_code, response.text)
            return None
    except Exception as e:
        print(f"❌ Error uploading to imgbb: {e}")
        return None
























# image_upload.py
# import requests
# import os
# from config import IMGUR_CLIENT_ID

# def upload_to_imgur(image_path):
#     """
#     Uploads an image to Imgur anonymously using just the Client ID.
#     Returns the direct image link.
#     """
#     headers = {
#         "Authorization": f"Client-ID {IMGUR_CLIENT_ID}"
#     }

#     try:
#         with open(image_path, "rb") as img_file:
#             files = {
#                 'image': img_file
#             }
#             response = requests.post("https://api.imgur.com/3/image", headers=headers, files=files)

#         if response.status_code == 200:
#             return response.json()["data"]["link"]
#         else:
#             print("❌ Upload failed:", response.status_code, response.text)
#             return None
#     except Exception as e:
#         print(f"❌ Error uploading to Imgur: {e}")
#         return None