
from easyocr import Reader
from PIL import Image
import io
import json
import csv
import openai
import ast
import requests
from io import BytesIO
import pprint
import openai_gpt


img_url = 'https://i.ibb.co/kQvHGjj/aewrg.png'


reader = Reader(["tr"])

def get_text(input_img):
    result = reader.readtext(input_img, detail=0)
    return " ".join(result)

def get_json(result):

    dump = json.dumps(result, indent=4, ensure_ascii=False)
    return dump

def main():
    # img = read_image_from_url(img_url)

    ocr_output = get_text(img_url)
    result = openai_gpt.openai_response(ocr_output)
    json_output = get_json(result)
    pprint.pprint(json_output)


if __name__ == "__main__":
    main()
