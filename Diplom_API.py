import requests
import json
from io import BytesIO
from urllib.parse import quote

# Название вашей группы в Нетологии
GROUP_NAME = "PD-130"


def get_cat_image_bytes(text: str) -> BytesIO:
    url = f"https://cataas.com/cat/cute/says/{quote(text)}"
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Картинка с текстом '{text}' получена.")
        return BytesIO(response.content)
    else:
        raise Exception(f"[!] Ошибка загрузки картинки '{text}': {response.status_code}")


def create_folder_on_disk(token: str, folder_name: str) -> None:
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": folder_name}
    response = requests.put(url, headers=headers, params=params)

    if response.status_code == 201:
        print(f"Папка '{folder_name}' создана на Яндекс.Диске.")
    elif response.status_code == 409:
        print(f"[i] Папка '{folder_name}' уже существует на Яндекс.Диске.")
    else:
        raise Exception(f"[!] Ошибка создания папки: {response.status_code}")


def upload_to_yandex_disk(token: str, folder: str, file_name: str, file_data: BytesIO) -> int:
    headers = {"Authorization": f"OAuth {token}"}
    path_on_disk = f"{folder}/{file_name}"

    # Получаем ссылку для загрузки
    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    params = {"path": path_on_disk, "overwrite": "true"}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        href = response.json()["href"]
        upload_response = requests.put(href, data=file_data.getvalue())
        if upload_response.status_code == 201:
            print(f"Файл '{file_name}' загружен на Яндекс.Диск.")
            return len(file_data.getvalue())
        else:
            raise Exception(f"[!] Ошибка при загрузке файла '{file_name}'.")
    else:
        raise Exception(f"[!] Не удалось получить ссылку загрузки для '{file_name}'.")


if __name__ == "__main__":
    texts_input = input("Введите тексты для картинок (через запятую): ").strip()
    token = input("Введите OAuth-токен Яндекс.Диска: ").strip()

    texts = [t.strip() for t in texts_input.split(",") if t.strip()]
    if not texts:
        print("[!]Не введено ни одного текста.")

    try:
        create_folder_on_disk(token, GROUP_NAME)
    except Exception as e:
        print(e)

    results = []

    for text in texts:
        try:
            img_bytes = get_cat_image_bytes(text)
            filename = f"{text.replace(' ', '_')}.jpg"
            size = upload_to_yandex_disk(token, GROUP_NAME, filename, img_bytes)
            results.append({
                "file_name": filename,
                "original_text": text,
                "size_bytes": size
            })
        except Exception as e:
            print(e)

    # Сохранение результата
    with open("upload_info.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"Информация сохранена в 'upload_info.json' ({len(results)} файл(а/ов)).")
