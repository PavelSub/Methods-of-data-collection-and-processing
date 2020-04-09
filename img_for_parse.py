# brew install tesseract-lang # Установка языкового пакета
import shutil
import PyPDF2
from PIL import Image
import pytesseract
import time
import re
from os import path, listdir

from pymongo import MongoClient
from log_pass import MONGO_LOGIN, MONGO_PWD, IMG_FOLDER
'''
Задача:
Извлечь серийные номера из файлов ( приложены в материалах урока)

Ваша задача разобрать все файлы, распознать на них серийный номер и создать коллекцию в MongoDB с четким указанием из какого файла был взят тот или иной серийный номер.

Дополнительно необходимо создать коллекцию и отдельную папку для хранения файлов в которых вы не смогли распознать серийный номер,
если в файле встречается несколько изображений необходимо явно указать что в файле таком-то страница такая серийный номер не найден.
'''

root_dir = f'{IMG_FOLDER}СКД_Поверка весов'
img_fld_sc = f'{IMG_FOLDER}sucssess'
img_fld_f = f'{IMG_FOLDER}fail'
img_fld_p = f'{IMG_FOLDER}processed'

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

client = MongoClient(f"mongodb+srv://{MONGO_LOGIN}:{MONGO_PWD}@cluster0-ujirt.mongodb.net/test?retryWrites=true&w=majority")
db = client['pdf_col']


def extract_pdf_img(pdf_path):
    try:
        print(f'processing: {pdf_path}')
        pdf_file = PyPDF2.PdfFileReader(open(pdf_path, 'rb'), strict=False)
    # except FileNotFoundError as e:
    #     print(e)
    #     return None
    # except EOFError as e:
    except Exception as e:
        print(e)
        return None

    result = []
    for pg_num in range(0, pdf_file.getNumPages()):
        page = pdf_file.getPage(pg_num)
        page_obj = page['/Resources']['/XObject'].getObject()

        if page_obj['/Im0'].get('/Subtype') == '/Image':
            size = (page_obj['/Im0']['/Width'], page_obj['/Im0']['/Height'])
            data = page_obj['/Im0']._data

            mode = 'RGB' if page_obj['/Im0']['/ColorSpace'] == '/DeviceRGB' else 'P'
            decoder = page_obj['/Im0']['/Filter']
            if decoder == '/DCTDecode':
                file_type = 'jpg'
            elif decoder == '/FlateDecode':
                file_type = 'png'
            elif decoder == '/JPXDecode':
                file_type = 'jp2'
            else:
                file_type = 'bmp'

            result_strict = {
                'page': pg_num,
                'size': size,
                'data': data,
                'mode': mode,
                'file_type': file_type
            }

            result.append(result_strict)

        return result


def save_pdf_image(file_name, f_path, *pdf_strict):
    files_path = []
    for itm in pdf_strict:
        name = f'{file_name[:file_name.rfind(".")]}_#_{itm["page"]}.{itm["file_type"]}'
        p = path.join(f_path, name)

        with open(p, 'wb') as image:
            image.write(itm['data'])
        files_path.append(p)
    return files_path


def extract_numbers(file_path):
    img_obj = Image.open(file_path)
    text = pytesseract.image_to_string(img_obj, 'rus')
    pattern = '[з3]а[ве]о[дл]ской \(сер[ин]й[ин]ый\) [ни]омер|[з3]а[ве]о[дл]кой [ни]омер \([ни]омера\)|сер[ин]й[ин]ый [ни]омер'
    for idx, line in enumerate(text.split('\n')):
        if line:
            if re.search(pattern, line.lower()):
                text_en = pytesseract.image_to_string(img_obj, 'eng')
                number = text_en.split('\n')[idx].split(' ')[-1]
                shutil.move(file_path, img_fld_sc)
                file_name = file_path[file_path.rfind('\\')+1:]
                save_mongo('sucssess', {'number': number, 'file': file_name, 'file_page': file_name[file_name.rfind('_#_')+3:file_name.rfind('.')]})
                print(f'sucssess: {file_name}')
                break
    else:
        shutil.move(file_path, img_fld_f)
        file_name = file_path[file_path.rfind('\\')+1:]
        save_mongo('fail', {'number': None, 'file': file_name, 'file_page': file_name[file_name.rfind('_#_')+3:file_name.rfind('.')]})
        print(f'fail: {file_name}')


def rec_dir_look(dir):
    for f in listdir(dir):
        p = f'{dir}/{f}'
        if path.isfile(p):
            res_img = extract_pdf_img(p)
            if res_img:
                b_img = save_pdf_image(p[p.rfind('/')+1:], img_fld_p, *res_img)
                for i in b_img: extract_numbers(i)
            else:
                print(f'fail: {p}')
        else:
            rec_dir_look(p)


def save_mongo(name, item):
    collection = db[name]
    collection.insert_one(item)


if __name__ == '__main__':
    rec_dir_look(root_dir)

