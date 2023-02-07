import gradio as gr
from easyocr import Reader
from PIL import Image
import io
import json
import csv
import openai
import ast
import os


openai.api_key = os.getenv('API_KEY')
reader = Reader(["tr"])

def get_parsed_address(input_img):

    address_full_text = get_text(input_img)
    return openai_response(address_full_text)
    

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


def text_dict(input):
    eval_result = ast.literal_eval(input)

    return (
        str(eval_result['city']),
        str(eval_result['distinct']),
        str(eval_result['neighbourhood']),
        str(eval_result['street']),
        str(eval_result['address']),
        str(eval_result['tel']),
        str(eval_result['name_surname']),
        str(eval_result['no']),
    )


        
def openai_response(ocr_input):
    prompt = f"""Tabular Data Extraction You are a highly intelligent and accurate tabular data extractor from 
            plain text input and especially from emergency text that carries address information, your inputs can be text 
            of arbitrary size, but the output should be in [{{'tabular': {{'entity_type': 'entity'}} }}] JSON format Force it 
            to only extract keys that are shared as an example in the examples section, if a key value is not found in the 
            text input, then it should be ignored. Have only city, distinct, neighbourhood, 
            street, no, tel, name_surname, address Examples: Input: Deprem sırasında evimizde yer alan adresimiz: İstanbul, 
            Beşiktaş, Yıldız Mahallesi, Cumhuriyet Caddesi No: 35, cep telefonu numaram 5551231256, adim Ahmet Yilmaz 
            Output: {{'city': 'İstanbul', 'distinct': 'Beşiktaş', 'neighbourhood': 'Yıldız Mahallesi', 'street': 'Cumhuriyet Caddesi', 'no': '35', 'tel': '5551231256', 'name_surname': 'Ahmet Yılmaz', 'address': 'İstanbul, Beşiktaş, Yıldız Mahallesi, Cumhuriyet Caddesi No: 35'}}
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
    resp["input"] = ocr_input
    dict_keys = [
    'city',
    'distinct',
    'neighbourhood',
    'street',
    'no',
    'tel',
    'name_surname',
    'address',
    'input',
    ]
    for key in dict_keys:
        if key not in resp.keys():
            resp[key] = ''
    return resp


with gr.Blocks() as demo:
    gr.Markdown(
    """
    # Enkaz Bildirme Uygulaması
    """)
    gr.Markdown("Bu uygulamada ekran görüntüsü sürükleyip bırakarak AFAD'a enkaz bildirimi yapabilirsiniz. Mesajı metin olarak da girebilirsiniz, tam adresi ayrıştırıp döndürür. API olarak kullanmak isterseniz sayfanın en altında use via api'ya tıklayın.")
    with gr.Row():
        img_area = gr.Image(label="Ekran Görüntüsü yükleyin 👇")
        ocr_result = gr.Textbox(label="Metin yükleyin 👇 ")
    open_api_text = gr.Textbox(label="Tam Adres")
    submit_button = gr.Button(label="Yükle")
    with gr.Column():
        with gr.Row():
            city = gr.Textbox(label="İl")
            distinct = gr.Textbox(label="İlçe")
        with gr.Row():
            neighbourhood = gr.Textbox(label="Mahalle")
            street = gr.Textbox(label="Sokak/Cadde/Bulvar")
        with gr.Row():
            tel = gr.Textbox(label="Telefon")
        with gr.Row():
            name_surname = gr.Textbox(label="İsim Soyisim")
            address = gr.Textbox(label="Adres")
        with gr.Row():
            no = gr.Textbox(label="Kapı No")


    submit_button.click(get_parsed_address, inputs = img_area, outputs = open_api_text, api_name="upload_image")

    ocr_result.change(openai_response, ocr_result, open_api_text, api_name="upload-text")

    open_api_text.change(text_dict, open_api_text,
                         [city, distinct, neighbourhood, street, address, tel, name_surname, no])

if __name__ == "__main__":
    demo.launch()