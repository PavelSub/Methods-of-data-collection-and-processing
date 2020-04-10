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

root_dir = f'{IMG_FOLDER}test_img'#СКД_Поверка весов' #
img_fld_sc = f'{IMG_FOLDER}sucssess'
img_fld_f = f'{IMG_FOLDER}fail'
img_fld_p = f'{IMG_FOLDER}processed'

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

client = MongoClient(f"mongodb+srv://{MONGO_LOGIN}:{MONGO_PWD}@cluster0-ujirt.mongodb.net/test?retryWrites=true&w=majority")
db = client['pdf_col']


def extract_pdf_img(pdf_path):
    try:
        print(f'processing pdf-file: {pdf_path}')
        pdf_file = PyPDF2.PdfFileReader(open(pdf_path, 'rb'), strict=False)
    except Exception as e: #FileNotFoundError as e: EOFError
        print(e)
        return None

    result = []
    for pg_num in range(0, pdf_file.getNumPages()):
        page_obj = pdf_file.getPage(pg_num)['/Resources']['/XObject'].getObject()

        page_img = list(page_obj.keys())[0]
        if page_obj[page_img].get('/Subtype') == '/Image':
            size = (page_obj[page_img]['/Width'], page_obj[page_img]['/Height'])
            data = page_obj[page_img]._data

            mode = 'RGB' if page_obj[page_img]['/ColorSpace'] == '/DeviceRGB' else 'P'
            decoder = page_obj[page_img]['/Filter']
            if decoder == '/DCTDecode': file_type = 'jpg'
            elif decoder == '/FlateDecode': file_type = 'png'
            elif decoder == '/JPXDecode': file_type = 'jp2'
            else: file_type = 'bmp'

            result.append({'page': pg_num, 'size': size, 'data': data, 'mode': mode, 'format': file_type})

    return result


def copy_image(file_name, f_path, pdf_ck, *pdf_strict):
    files_path = []
    for itm in pdf_strict:
        if pdf_ck:
            name = f'{file_name[:file_name.rfind(".")]}_#_{itm["page"]}.{itm["format"]}'
            p = path.join(f_path, name.lower())
            with open(p, 'wb') as image:
                image.write(itm['data'])
        else:
            name = f'{file_name[:file_name.rfind(".")]}_#_0.{itm.format}'
            p = path.join(f_path, name.lower())
            itm.save(p, itm.format)
        files_path.append(p)
    return files_path


def extract_pattern(file_path, pattern=''):
    img_obj = Image.open(file_path)
    for i in range(3):
        if image_text_read(img_obj, pattern, file_path):
            img_obj = img_obj.rotate(90, Image.NEAREST, expand=1)
        else:
            break
    else:
        move_and_save_mongo(file_path, 'fail')


def image_text_read(img_obj, pattern, file_path):
    text = pytesseract.image_to_string(img_obj, 'rus')
    for idx, line in enumerate(text.split('\n')):
        if line:
            if re.search(pattern, line.lower()):
                text_en = pytesseract.image_to_string(img_obj, 'eng')
                move_and_save_mongo(file_path, 'sucssess', text_en.split('\n')[idx].split(' ')[-1])
                return False
    return True


def move_and_save_mongo(file_path, cat, obj=None):
    shutil.move(file_path, f'{IMG_FOLDER}{cat}')
    file_name = file_path[file_path.rfind('\\')+1:]
    collection = db[cat]
    collection.insert_one({'number': obj, 'file': file_name, 'file_page': file_name[file_name.rfind('_#_')+3:file_name.rfind('.')]})
    print(f'{cat}: {file_name}')


def rec_dir_look(cat, pattern=''):
    for f in listdir(cat):
        p = f'{cat}/{f}'
        format = f.split('.')[-1]
        if not path.isfile(p):
            rec_dir_look(p)
        elif path.isfile(p) and format in ['pdf', 'jpeg', 'jpg', 'png', 'bmp']:
            pdf_ck = True if format == 'pdf' else False
            res_img = extract_pdf_img(p) if pdf_ck else [Image.open(p)]
            if res_img:
                b_img = copy_image(p[p.rfind('/')+1:], img_fld_p, pdf_ck, *res_img)

                for i in b_img: extract_pattern(i, pattern=pattern)
        else:
            print(f'Unreadable format: {format}')

if __name__ == '__main__':
    pat = '[з3]а[ве]о[дл]ской \(сер[ин]й[ин]ый\) [ни]омер|[з3]а[ве]о[дл]кой [ни]омер \([ни]омера\)|сер[ин]й[ин]ый [ни]омер|[з3]а[ве]о[дл]ской [ни]омер|[з3]а[ве]о[дл]ской'
    rec_dir_look(root_dir, pattern=pat)
