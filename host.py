import os
import time
import json
import requests
import subprocess
import git
import signal
import sys


# NGROK başlat
def start_ngrok():
    os.system("cls")
    print("Ngrok başlatılıyor...")
    # Start ngrok and hide the terminal output
    process = subprocess.Popen(["ngrok", "http", "80"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)  # Give ngrok time to start
    return process


# NGROK URL al
def get_ngrok_url():
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        response.raise_for_status()
        data = response.json()
        return data['tunnels'][0]['public_url']
    except requests.RequestException as e:
        print(f"Ngrok URL alınamadı: {e}")
        return None


# JSON dosyasını güncelle veya oluştur
def update_readme_json(repo_path, ngrok_url, is_host_running=True):
    readme_json_path = os.path.join(repo_path, "Host.json")

    # Host.json dosyası yoksa yeni dosya oluştur
    if not os.path.exists(readme_json_path):
        print("Host.json bulunamadı, yeni oluşturuluyor...")
        data = {"ngrok_url": ngrok_url if is_host_running else "Host stopped"}
    else:
        try:
            with open(readme_json_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, ValueError):  # Geçersiz JSON veya boş dosya
            print("Geçersiz veya boş JSON formatı! Yeni bir JSON yapısı oluşturuluyor...")
            data = {"ngrok_url": ngrok_url if is_host_running else "Host stopped"}

        # Dosyadaki ngrok_url'yi güncelle
        data["ngrok_url"] = ngrok_url if is_host_running else "Host stopped"

    # JSON'u dosyaya yaz
    with open(readme_json_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"Host.json güncellendi: {data['ngrok_url']}")


# Git işlemleri (commit & push)
def commit_and_push(repo_path):
    repo = git.Repo(repo_path)
    repo.git.add("Host.json")
    repo.index.commit("Update Ngrok URL")
    origin = repo.remote(name="origin")
    origin.push()
    print("Değişiklikler GitHub'a gönderildi.")


# NGROK sürecini durdur
def stop_ngrok(process):
    os.system("cls")
    print("Ngrok durduruluyor...")
    process.terminate()  # Terminate the ngrok process
    process.wait()  # Wait for the process to terminate properly
    time.sleep(1)  # Ensure Ngrok stops properly
    print("Ngrok durduruldu.")


# Ana işlem
def main():
    REPO_PATH = "C:\\Users\\oglcn\\Desktop\\JustHost"
    ngrok_process = None

    while True:
        print("\n1. Ngrok başlat ve Host.json'ı güncelle (Commit et)")
        print("2. Ngrok'u durdur ve Host.json'ı güncelle (Commit et)")
        print("3. Çık")
        choice = input("Seçiminizi yapın (1/2/3): ")

        if choice == '1':
            if ngrok_process is None:
                ngrok_process = start_ngrok()
                ngrok_url = get_ngrok_url()

                if ngrok_url:
                    update_readme_json(REPO_PATH, ngrok_url)
                    commit_and_push(REPO_PATH)
                else:
                    print("Ngrok URL alınamadı, işlem iptal edildi.")
            else:
                print("Ngrok zaten çalışıyor!")

        elif choice == '2':
            if ngrok_process is not None:
                stop_ngrok(ngrok_process)
                ngrok_process = None
                update_readme_json(REPO_PATH, None, is_host_running=False)
                commit_and_push(REPO_PATH)
            else:
                print("Ngrok çalışmıyor!")

        elif choice == '3':
            print("Çıkılıyor...")
            if ngrok_process is not None:
                stop_ngrok(ngrok_process)
            break

        else:
            print("Geçersiz seçim! Lütfen 1, 2 veya 3 girin.")


if __name__ == "__main__":
    main()
