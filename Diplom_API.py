import requests
import os
import json

# Название группы в Нетологии
GROUP_NAME = "PD-130" 

# получение картинки с Cataas
def get_cat_image(text, save_path):
    url = f"https://cataas.com/cat/cute/says/{text}"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"[+] Картинка сохранена локально: {save_path}")
        return True
    else:
        print("[-] Не удалось получить картинку.")
        return False

# загрузка файла на Яндекс.Диск
def upload_to_yandex_disk(file_path, yandex_token, folder, file_name):
    headers = {
        "Authorization": f"OAuth {yandex_token}"
    }

    # Создание папки 
    folder_url = f"https://cloud-api.yandex.net/v1/disk/resources"
    requests.put(folder_url, headers=headers, params={"path": folder})

    # Получение URL для загрузки
    upload_url = f"{folder_url}/upload"
    response = requests.get(upload_url, headers=headers, params={
        "path": f"{folder}/{file_name}",
        "overwrite": "true"
    })

    if response.status_code == 200:
        href = response.json().get("href")
        with open(file_path, "rb") as f:
            upload_response = requests.put(href, files={"file": f})
        if upload_response.status_code == 201:
            print(f"[+] Файл загружен на Яндекс.Диск: {folder}/{file_name}")
            return True
        else:
            print("[-] Ошибка при загрузке файла.")
    else:
        print("[-] Не удалось получить ссылку для загрузки.")
    return False



if __name__ == "__main__":
    text = input("Введите текст для картинки: ").strip()
    yandex_token = input("Введите токен Яндекс.Диска: ").strip()

    file_name = f"{text}.jpg"
    local_folder = "cats"
    os.makedirs(local_folder, exist_ok=True)
    local_path = os.path.join(local_folder, file_name)

    # Получение и сохранение картинки
    if get_cat_image(text, local_path):
        file_size = os.path.getsize(local_path)

        # Загрузка на Диск
        if upload_to_yandex_disk(local_path, yandex_token, GROUP_NAME, file_name):
            # Сохраняем JSON с информацией о размере
            json_data = {
                "file_name": file_name,
                "size_bytes": file_size
            }

            with open("upload_info.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            print("[+] Информация сохранена в upload_info.json")

