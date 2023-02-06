
import openai


openai.api_key = "OPEN-API-KEY"



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
    return resp