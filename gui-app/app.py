import ast
import csv
import io
import json

import gradio as gr
import openai
from easyocr import Reader
from PIL import Image

openai.api_key = "OPEN-API-KEY"
reader = Reader(["tr"])


def get_text(input_img):
    result = reader.readtext(input_img, detail=0)
    return " ".join(result)


def save_csv(mahalle, il, sokak, apartman):
    adres_full = [mahalle, il, sokak, apartman]

    with open("adress_book.csv", "a", encoding="utf-8") as f:
        write = csv.writer(f)
        write.writerow(adres_full)
    return adres_full


def get_json(mahalle, il, sokak, apartman):
    adres = {"mahalle": mahalle, "il": il, "sokak": sokak, "apartman": apartman}
    dump = json.dumps(adres, indent=4, ensure_ascii=False)
    return dump


def openai_response(ocr_input):
    prompt = f"""Tabular Data Extraction
You are a highly intelligent and accurate tabular data extractor from plain text input and especially from emergency text that carries address information, your inputs can be text of arbitrary size, but the output should be in [{{'tabular': {{'entity_type': 'entity'}} }}] JSON format

Force it to only extract keys that are shared as an example in the examples section, if a key value is not found in the text input, then it should be ignored and should be returned as an empty string

Have only il, ilçe, mahalle, sokak, no, tel, isim_soyisim, adres

Examples:


Input: Deprem sırasında evimizde yer alan adresimiz: İstanbul, Beşiktaş, Yıldız Mahallesi, Cumhuriyet Caddesi No: 35, cep telefonu numaram 5551231256, adim Ahmet Yilmaz
Output: [{{'Tabular': '{{'il': 'İstanbul', 'ilçe': 'Beşiktaş', 'mahalle': 'Yıldız Mahallesi', 'sokak': 'Cumhuriyet Caddesi', 'no': 35, 'tel': 5551231256, 'isim_soyisim': 'Ahmet Yılmaz', 'adres': 'İstanbul, Beşiktaş, Yıldız Mahallesi, Cumhuriyet Caddesi No: 35'}}' }}]


Input: {ocr_input}
Output:

"""

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\n"],
    )
    resp = response["choices"][0]["text"]
    resp = eval(resp.replace("'{", "{").replace("}'", "}"))
    resp = resp[0]["Tabular"]
    return (
        resp,
        resp["il"],
        resp["ilçe"],
        resp["mahalle"],
        resp["sokak"],
        resp["no"],
        resp["tel"],
        resp["isim_soyisim"],
        resp["adres"],
    )


with gr.Blocks() as demo:
    gr.Markdown(""" # Image to Text - Adres""")
    with gr.Row():
        img_area = gr.Image()
        ocr_result = gr.Textbox(label="OCR")
    open_api_text = gr.Textbox(label="OPENAI")

    with gr.Column():
        with gr.Row():
            il = gr.Textbox(label="il")
            ilce = gr.Textbox(label="ilce")
        with gr.Row():
            mahalle = gr.Textbox(label="mahalle")
            sokak = gr.Textbox(label="sokak/cadde/bulvar")
        with gr.Row():
            no = gr.Textbox(label="no")
            tel = gr.Textbox(label="tel")
        with gr.Row():
            isim_soyisim = gr.Textbox(label="isim_soyisim")
            adres = gr.Textbox(label="adres")

    submit_button = gr.Button()
    submit_button.click(get_text, img_area, ocr_result)

    ocr_result.change(
        openai_response,
        ocr_result,
        [open_api_text, il, ilce, mahalle, sokak, no, tel, isim_soyisim, adres],
    )

    # json_out = gr.Textbox()
    # csv_out = gr.Textbox()

    # adres_submit = gr.Button()
    # adres_submit.click(get_json, [mahalle, il, sokak, apartman], json_out)
    # adres_submit.click(save_csv, [mahalle, il, sokak, apartman], csv_out)


if __name__ == "__main__":
    demo.launch()
