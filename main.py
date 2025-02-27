from google import genai
import PIL.Image
from PIL import Image
from PIL.ExifTags import TAGS
import os
import time
import re


# Define folder holding images
images_folderpath = "Photos"
description_folderpath = "Description"
dateTime_folderpath = "DateTime"


# Retrieve images from dir
def get_images(images_folderpath):

    image_list = os.listdir(images_folderpath)

    if len(image_list) == 0:
        print("The folder is empty.") 
    else: 
        image_count = len(image_list)
        return image_list, image_count


# Get DateTime from metadata
def get_datetime(image_list, i):
    # Open the image
    image = Image.open(f'{images_folderpath}/{image_list[i]}')

    # Extracting the EXIF metadata
    exifdata = image.getexif()

    # Looping through all the tags present in EXIF data
    for tagid in exifdata:
        
        # Getting the tag name instead of tag id
        tagname = TAGS.get(tagid, tagid)

        # Corrected indentation of the if statement
        if tagname == "DateTime":
            # Getting the respective value
            value = exifdata.get(tagid)
            metadata = (f"{tagname:25}: {value}")
            return metadata
        

# Run api to get image description
def get_description(image_list, i):

    # i used later for index to loop through images
    image = PIL.Image.open(f'{images_folderpath}/{image_list[i]}')

    client = genai.Client(api_key="APIKEY")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=["Examine the picture then return a thourough description of what you see. Please keep your response in a paragraph(s) format", image])

    response = response.text
    return response


# Create text files that match each image name
def write_to_file(outputfolder, image_list, i, text):
    # Define the text file name based on the image name (changing extension to .txt)
    text_file_path = f"{outputfolder}/{os.path.splitext(image_list[i])[0]}.txt"
    
    # Add newlines after each sentence (assuming sentences end with '.', '!', or '?')
    formatted_text = re.sub(r'(?<!\d)(?<=[.!?]) +', r'\n', text)
    
    # Write formatted text to the file
    with open(text_file_path, "w", encoding="utf-8") as file:
        file.write(formatted_text + "\n")


# Main function and boilerplate
def main():
    image_list, image_count = get_images(images_folderpath)
    for i in range(image_count):
        response = get_description(image_list, i)
        write_to_file(description_folderpath, image_list, i, response)
        metadata = get_datetime(image_list, i)
        write_to_file(dateTime_folderpath, image_list, i, metadata)
        print(f"Picture {i+1} Done")
        time.sleep(5) # using this to avoid gemini request limit (15 RPM)


if __name__ == '__main__':
  main()