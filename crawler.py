import os
import time
import urllib
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from zipfile2 import ZipFile


def get_urls(artist):
    url = 'https://51comic.org/index.php/search?key=' + urllib.parse.quote(artist)
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    search_result = soup.find(attrs={'class': 'search_head'})
    if '没有找到' in search_result.text:
        return []
    else:
        items = soup.find_all(attrs={'class': 'comic-update'})
        url_list = [item.a['href'] for item in items if item.a['href'].strip() != '']
        return url_list


def images_crawler(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    title = name_correction(str(soup.title)[7:-21])
    zip_title = './zip_files/' + title + '.zip'
    z_file = ZipFile(zip_title, 'w')
    items = soup.find_all(attrs={'class': 'lazy-read'})
    for item in tqdm(items, desc='Download progress', ncols=100):
        time.sleep(0.5)
        url1 = item['data-original'].strip()
        headers = {'User-Agent': 'Mozilla/5.0'}
        response1 = requests.get(url1, headers=headers)
        file_name = item['alt']
        with open(file_name, 'wb') as f:
            f.write(response1.content)
            f.flush()
            f.close()
        z_file.write(file_name)
        os.remove(file_name)
    z_file.close()


def name_correction(name):
    if len(name) > 255:
        name = name[:255]
    new_name = ''
    for letter in name:
        if letter in ['<', '>', '/', '\\', '|', ':', '*', '?']:
            new_name += ' '
        else:
            new_name += letter
    return new_name


def print_runtime(t):
    h = t // 3600
    m = (t % 3600) // 60
    s = round(t % 60, 1)
    print(f'time cost: {h}h {m}min {s}s')


if __name__ == '__main__':
    start = time.time()
    tips = ''
    urls = get_urls(tips)
    if len(urls) == 0:
        print('No matching results')
    else:
        for i in range(len(urls)):
            print(f'Downloading {i + 1} / {len(urls)}')
            images_crawler(urls[i])
    end = time.time()
    print_runtime(end - start)
