import re
import os
import json
import signal
import shutil
import requests
import subprocess
from cookies import cookies
from bs4 import BeautifulSoup

def ascii_clear():
    os.system('cls||clear')
    print("""
                                                                                        
                                                                                        
    @@@@            (@@@@@@@@@&                                                                                                                                      
    @@@@         @@@@@@@@@@@@@@@@@@                                                                                                                                  
      (        @@@@@&          @@@@@@                                                                                                                                
    @@@@     (@@@@#              @@@@@                 @@@@@@@@@@@          %@@@@@@@@@@&        @@@@@&@@@@@@@@@   @@@@@@@@@@@                                        
    @@@@     @@@@%                @@@@@             (@@@@@@%(#@@@@@&      @@@@@@&((&@@@@@@      @@@@@@@@#(&@@@@@@@@@@%(#@@@@@@@                                      
    @@@@     @@@@                 @@@@@            %@@@@                 @@@@@        &@@@@     @@@@@        @@@@@@        @@@@&                                     
    @@@@     @@@@@           @@   @@@@(            @@@@&(               (@@@@          @@@@&    @@@@@         @@@@         @@@@@                                     
    @@@@      @@@@@%      (%@@@@@@@@@(             &@@@@                 @@@@%        (@@@@     @@@@@         @@@@         @@@@@                                     
    @@@@        @@@@@@@%(  (@@@@@@@@       #@@(     &@@@@@&   (@@@@(      @@@@@@(  (@@@@@@      @@@@@         @@@@         @@@@@                                     
    @@@@          (@@@@@@@@@@@@@@@@@@(    &@@@@#      (@@@@@@@@@@@%         @@@@@@@@@@@@        @@@@@         @@@@         @@@@@                                     
                                  @@&       (     
                                         
                                                IQ.com Downloader V2                              
                                                    TAJLN 2023  
""")

def signal_handler(sig, frame):
    print('\nBye :)')
    quit()

signal.signal(signal.SIGINT, signal_handler)

def get_base_html(url, res, lang, cookies):
    cookies['lang'] = lang
    cookies['QiyiPlayerBID'] = str(res)

    try:
        response = requests.get(url, cookies=cookies)
        return response.content
    except:
        print('Failed to request provided url')
        quit()

def get_ext(base_html):
    try:
        next_data = json.loads(BeautifulSoup(base_html, features="lxml").find("script", {"id": "__NEXT_DATA__"}).text)
        video = next_data['props']['initialProps']['pageProps']['prePlayerData']['dash']['data']['program']['video']
        
        for v in video:
            if 'm3u8' in v:
                with open('temp.m3u8', "w+") as file:
                    file.write(v['m3u8'])
                    print('Saved temp m3u8 to file')
            
                return v['m3u8']
    except Exception as e:
        print('Failed to get extm3u from html')
        print(e)

def get_album_id(base_html):
    next_data = json.loads(BeautifulSoup(base_html, features="lxml").find("script", {"id": "__NEXT_DATA__"}).text)
    return str(next_data['props']['initialState']['album']['videoAlbumInfo']['albumId'])

def get_episodes(base_html, lang):
    r = []
    
    try:
        album_id = get_album_id(base_html)
    
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        }

        params = {
            'platformId': '3',
            'modeCode': 'my',
            'langCode': lang,
            'startOrder': '0',
            'endOrder': '10000',
        }

        response = requests.get(
            'https://pcw-api.iq.com/api/v2/episodeListSource/' + album_id, params=params, headers=headers).json()

        epg = response['data']['epg']
        for e in epg:
            if 'playLocSuffix' in e:
                r.append('https://www.iq.com/play/' + e['playLocSuffix'])
    except:
        pass
        
    return r
def get_series_title(base_html):
    try:
        return BeautifulSoup(base_html, features="lxml").find("span", {"class": "intl-album-title-word-wrap"}).find('span').text
    except:
        print('Failed to get series title')
        quit()
    
def get_title(base_html):
    try:
        return BeautifulSoup(base_html, features="lxml").find("p", {"class": "intl-play-title"}).text
    except Exception as e:
        print('Failed to get title (wrong url?)')
        quit()
        
  
def choose_lang():
    print('\nSelect language:')
    print('1. English')
    print('2. Simplified Chinese')
    print('3. Traditional Chinese')
    print('4. Bahasa Indonesia')
    print('5. Bahasa Malaysia')
    print('6. Thai')
    print('7. Vietnamese')
    print('8. Japanese')
    print('9. Português')
    print('10. Español')
    
    choice = int(input('\nChoice: '))
    
    if choice > 10 or choice < 1:
        return choose_res()
    
    l = ['en_us', 'zh_cn', 'zh_tw', 'id_id', 'ms_my', 'th_th', 'vi_vn', 'ja', 'pt_br', 'es_mx']
    
    return l[choice-1]
  
def choose_res():
    print('\nSelect resolution:')
    print('1. 1080p')
    print('2. 720')
    print('3. 480p')
    print('4. 360p')
    
    choice = int(input('\nChoice: '))
    
    if choice > 4 or choice < 1:
        return choose_res()
    
    l = [600, 400, 300, 200]
    
    return l[choice-1]

def slugify(value, allow_unicode=False):
    value = str(value)
    value = re.sub(r'[^\w\s-]', '', value)
    return re.sub(r'[-\s]+', '.', value).strip('-_')

def dl_media(foldername, filename):
    foldername = slugify(foldername)
    filename = slugify(filename)

    proc_list = ['N_m3u8DL-RE.exe', '--save-dir', 'Downloads/' + foldername, '--tmp-dir', 'Temp/', '--save-name', filename, './temp.m3u8', '-M', 'mp4']
    print('Downloading')
    subprocess.run(proc_list)
    
    os.remove('./temp.m3u8')

def dl_subtitles(base_html, foldername, filename):
    print('Downloading subtitles')
    
    foldername = slugify(foldername)
    filename = slugify(filename)

    next_data = json.loads(BeautifulSoup(base_html, features="lxml").find("script", {"id": "__NEXT_DATA__"}).text)
    
    stl = next_data['props']['initialProps']['pageProps']['prePlayerData']['dash']['data']['program']['stl']
    
    for s in stl:
        lang = s['_name']
        sub_url = 'https://meta.video.iqiyi.com' + s['srt']
        
        subpath = '.\\Downloads\\' + foldername + '\\' + filename + '.' + lang + '.srt'
        
        f = open(subpath, "w", encoding="utf-8")
        f.write(requests.get(sub_url).text)
        f.close()

try:
    shutil.rmtree('Temp')
except:
    pass

ascii_clear()

url = input('Enter iq.com url: ').replace('album', 'play')

ascii_clear()

lang = choose_lang()

ascii_clear()

res = choose_res()

    
base_html = get_base_html(url, res, lang, cookies)

ascii_clear()

episodes = get_episodes(base_html, lang)

if len(episodes) == 0:
    print('Single media detected')

    title = get_title(base_html)
    print('Found: ' + title)

    get_ext(base_html)

    dl_media(title, title)
    dl_subtitles(base_html, title, title)

else:
    print('Series detected')

    series_title = get_series_title(base_html)
    title = get_title(base_html)
    print('Found episode: ' + title)
    
    c = input('Do you want to download the entire series? (y/n): ')
    
    if c.lower() == 'y':
        for e in episodes:
            ascii_clear()
            
            episode_html = get_base_html(e, res, lang, cookies)
            title = get_title(episode_html)
            
            print(title + '\n')
            
            get_ext(episode_html)
            
            dl_media(series_title, title)
            dl_subtitles(episode_html, series_title, title)
        
    else:
        ascii_clear()
    
        print('Single episode download selected\n')
        
        print(title + '\n')
        
        get_ext(base_html)
        
        dl_media(series_title, title)
        dl_subtitles(base_html, series_title, title)   
    
print('Done')
