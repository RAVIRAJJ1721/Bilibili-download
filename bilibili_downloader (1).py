
import os
import requests
import random
import subprocess
import re

banner = """
             ██████╗░██╗██╗░░░░░██╗░░░████████╗██╗░░░██╗
             ██╔══██╗██║██║░░░░░██║░░░╚══██╔══╝██║░░░██║
             ██████╦╝██║██║░░░░░██║░░░░░░██║░░░╚██╗░██╔╝
             ██╔══██╗██║██║░░░░░██║░░░░░░██║░░░░╚████╔╝░
             ██████╦╝██║███████╗██║██╗░░░██║░░░░░╚██╔╝░░
             ╚═════╝░╚═╝╚══════╝╚═╝╚═╝░░░╚═╝░░░░░░╚═╝░░░
"""

def cargar_cookies_desde_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            cookies = file.read().splitlines()
            return '; '.join(cookies)
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return ''

cookies = cargar_cookies_desde_archivo('./cookies.txt')

headers = {
    'Referer': 'https://www.bilibili.tv/',
    'Cookie': cookies
}

def obtener_valor_despues_de_video(enlace):
    url_parseada = enlace.split('/')
    if 'video' in enlace:
        return url_parseada[url_parseada.index('video') + 1]
    elif 'play' in enlace:
        numeros_despues_de_play = [s for s in url_parseada if s.isdigit()]
        if len(numeros_despues_de_play) >= 2:
            return numeros_despues_de_play[1]
        elif len(numeros_despues_de_play) == 1:
            print('Only one number found after /play/. That value will be used.')
            return numeros_despues_de_play[0]
        else:
            print('Not enough numbers found after /play/')
            return None
    else:
        print('Unsupported link type.')
        return None

def obtener_url_de_video_y_audio(valor, calidad_deseada=64):
    if valor:
        regex_video = r'^\d{4,8}$'
        if re.match(regex_video, valor):
            url_api = f'https://api.bilibili.tv/intl/gateway/web/playurl?ep_id={valor}&device=wap&platform=web&qn=64&tf=0&type=0'
        else:
            url_api = f'https://api.bilibili.tv/intl/gateway/web/playurl?s_locale=en_US&platform=web&aid={valor}&qn=120'
        try:
            response = requests.get(url_api, headers=headers)
            data = response.json()
            if not data or 'data' not in data or 'playurl' not in data['data']:
                print('Server response does not contain the expected structure.')
                return None
            url_video = None
            url_audio = None
            for video_info in data['data']['playurl']['video']:
                video_resource = video_info.get('video_resource', {})
                stream_info = video_info.get('stream_info', {})
                calidad_video = stream_info.get('quality', 112)
                if calidad_video == 112 and video_resource.get('url', '').strip():
                    url_video = video_resource['url']
                    break
                elif calidad_video == 80 and video_resource.get('url', '').strip():
                    url_video = video_resource['url']
                    break
                elif calidad_video == 64 and video_resource.get('url', '').strip():
                    url_video = video_resource['url']
                    break
                elif calidad_video == 32 and video_resource.get('url', '').strip():
                    url_video = video_resource['url']
                    break
            audio_info_lista = data['data']['playurl'].get('audio_resource', [])
            if audio_info_lista:
                audio_info = audio_info_lista[0]
                calidad_audio = audio_info.get('quality', 0)
                if calidad_audio >= calidad_deseada:
                    url_audio = audio_info.get('url')
            if url_video and url_audio:
                return {'urlVideo': url_video, 'urlAudio': url_audio}
            else:
                print(f"URL for video or audio with quality {calidad_deseada} not found.")
                return None
        except Exception as e:
            print(f"Error getting video and audio URL: {e}")
            return None
    else:
        print('No value provided after /video/ or /play/')
        return None

def descargar_archivo(url_archivo, nombre_archivo):
    try:
        response = requests.get(url_archivo, stream=True)
        with open(nombre_archivo, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"File downloaded as: {nombre_archivo}")
        return nombre_archivo
    except Exception as e:
        print(f"Error during file download: {e}")
        return None

def eliminar_archivo(nombre_archivo):
    try:
        os.remove(nombre_archivo)
    except Exception as e:
        print(f"Error deleting file {nombre_archivo}: {e}")

def ejecutar_comando_shell(comando):
    try:
        subprocess.run(comando, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def descargar_video_y_audio(enlace, directorio_destino='./Downloads'):
    valor = obtener_valor_despues_de_video(enlace)
    if valor:
        urls = obtener_url_de_video_y_audio(valor)
        if urls:
            print('¡Links found!')
            os.makedirs(directorio_destino, exist_ok=True)
            video_file = os.path.join(directorio_destino, f"{random.randint(100000, 999999)}_video.m4v")
            audio_file = os.path.join(directorio_destino, f"{random.randint(100000, 999999)}_audio.mp4")
            descargar_archivo(urls['urlVideo'], video_file)
            descargar_archivo(urls['urlAudio'], audio_file)
            final_file = os.path.join(directorio_destino, f"{random.randint(100000, 999999)}_final.mp4")
            comando_ffmpeg = f"ffmpeg -i {video_file} -i {audio_file} -vcodec copy -acodec copy -f mp4 {final_file}"
            ejecutar_comando_shell(comando_ffmpeg)
            print(f"Files linked as: {final_file}")
            eliminar_archivo(video_file)
            eliminar_archivo(audio_file)
            print('Video and audio files deleted.')
        else:
            print('URL for the desired quality not found.')
    else:
        print('Link does not contain the expected "video/" or "play/" part.')

def main():
    print(banner)
    enlace = input('Enter the link: ')
    descargar_video_y_audio(enlace)

if __name__ == '__main__':
    main()
