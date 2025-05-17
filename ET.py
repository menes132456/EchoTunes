import tkinter as tk
from tkinter import messagebox
import os
import pygame
import random
import yt_dlp
from mutagen.mp3 import MP3

pygame.init()
pygame.mixer.init()

suanki_sure = 0
sure_timer = None
sarki_durum = "durdu"

root = tk.Tk()
root.title("🎵 EchoTunes")
root.geometry("450x400")
root.config(bg="#1e1e1e")

secilen_dosya = None
current_index = 0
mod = "normal"

def saniye_format(saniye):
    dakika = saniye // 60
    saniye = saniye % 60
    return f"{dakika:02d}:{saniye:02d}"

def sure_sayaci(toplam_sure):
    global suanki_sure, sure_timer, sarki_durum
    if sarki_durum == "caliyor":
        sure_label.config(text=f"{saniye_format(suanki_sure)} / {saniye_format(toplam_sure)}")
        suanki_sure += 1
        sure_timer = root.after(1000, sure_sayaci, toplam_sure)
    else:
        sure_label.config(text=f"{saniye_format(suanki_sure)} / {saniye_format(toplam_sure)}")

def sureyi_guncelle(tam_yol):
    global suanki_sure, sure_timer, sarki_durum
    try:
        audio = MP3(tam_yol)
        toplam_sure = int(audio.info.length)
        suanki_sure = 0
        sarki_durum = "caliyor"

        if sure_timer:
            root.after_cancel(sure_timer)
        sure_sayaci(toplam_sure)
    except Exception:
        sure_label.config(text="Süre okunamadı")

def cal_secili():
    global current_index
    secim = kutu.curselection()
    if secim:
        current_index = secim[0]
        dosya = kutu.get(current_index)
        tam_yol = os.path.join("Songs", dosya)
        pygame.mixer.music.load(tam_yol)
        sureyi_guncelle(tam_yol)
        pygame.mixer.music.play()
        status_label.config(text=f"Çalıyor: {dosya}", fg="dark orange")
        kontrol_butonu.config(text="⏸ Durdur", command=durdur)
        kutu.selection_clear(0, tk.END)
        kutu.selection_set(current_index)
        root.after(1000, kontrol_et)

def durdur():
    global sarki_durum
    pygame.mixer.music.pause()
    sarki_durum = "durdu"
    status_label.config(text="Müzik durduruldu.", fg="purple")
    kontrol_butonu.config(text="▶ Devam", command=devam)

def devam():
    global sarki_durum
    pygame.mixer.music.unpause()
    sarki_durum = "caliyor"
    status_label.config(text="Müzik devam ediyor.", fg="dark orange")
    kontrol_butonu.config(text="⏸ Durdur", command=durdur)

def sonraki_sarki():
    global current_index
    if mod == "karışık":
        current_index = random.randint(0, kutu.size() - 1)
    else:
        current_index += 1

    if current_index < kutu.size():
        dosya = kutu.get(current_index)
        tam_yol = os.path.join("Songs", dosya)
        pygame.mixer.music.load(tam_yol)
        pygame.mixer.music.play()
        sureyi_guncelle(tam_yol)
        kutu.selection_clear(0, tk.END)
        kutu.selection_set(current_index)
        status_label.config(text=f"Çalıyor: {dosya}", fg="lime")
        kontrol_butonu.config(text="⏸ Durdur", command=durdur)
        root.after(1000, kontrol_et)
    else:
        status_label.config(text="Tüm şarkılar çalındı.", fg="red")
        kontrol_butonu.config(text="⏸ Durdur", command=durdur)

def kontrol_et():
    if not pygame.mixer.music.get_busy():
        if mod == "tekrar":
            pygame.mixer.music.play()
            root.after(1000, kontrol_et)
        elif mod in ["sonraki", "karışık"]:
            sonraki_sarki()
    else:
        root.after(1000, kontrol_et)

def mod_degistir():
    global mod
    if mod == "normal":
        mod = "tekrar"
    elif mod == "tekrar":
        mod = "sonraki"
    elif mod == "sonraki":
        mod = "karışık"
    else:
        mod = "normal"
    mod_butonu.config(text=f"Mod: {mod.capitalize()}")
    status_label.config(text=f"Mod değiştirildi: {mod.capitalize()}", fg="cyan")

def youtube_indirme_ekrani():
    global pencere, url_entry, name_entry
    pencere = tk.Toplevel(root)
    pencere.title("YT")
    pencere.geometry("400x200")
    pencere.config(bg="#1e1e1e")

    tk.Label(pencere, text="YT Linki:", fg="white", bg="#1e1e1e").pack(pady=5)
    url_entry = tk.Entry(pencere, width=50)
    url_entry.pack(pady=5)

    tk.Label(pencere, text="isim (istersen):", fg="white", bg="#1e1e1e").pack(pady=5)
    name_entry = tk.Entry(pencere, width=50)
    name_entry.pack(pady=5)

    tk.Button(pencere, text="İndir", command=indir, bg="#27ae60", fg="white").pack(pady=10)

def indir():
    url = url_entry.get()
    custom_name = name_entry.get().strip()

    try:
        if not os.path.exists("Songs"):
            os.makedirs("Songs")

        ffmpeg_yolu = os.path.abspath("ffmpeg")

        mp3_ismi = None  # Başta boş, sonra doldurulacak

        options = {
            'format': 'bestaudio/best',
            'ffmpeg_location': ffmpeg_yolu,
            'outtmpl': f'Songs/{custom_name if custom_name else "%(title)s"}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,  # Konsol çıktısını azaltır
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            if not custom_name:
                mp3_ismi = info_dict['title'] + ".mp3"
            else:
                mp3_ismi = custom_name + ".mp3"

        kutu.insert(tk.END, mp3_ismi)
        messagebox.showinfo("Başarılı", f"{mp3_ismi} indirildi!")
        pencere.destroy()
    except Exception as e:
        messagebox.showerror("Hata", f"İndirme başarısız: {e}")

# --- GUI Arayüz ---

kutu = tk.Listbox(root, width=50, height=12, bg="#2e2e2e", fg="white", selectbackground="dark orange", font=("Consolas", 10))
kutu.pack(padx=10, pady=10)

if not os.path.exists("Songs"):
    os.makedirs("Songs")

dosyalar = [f for f in os.listdir("Songs") if f.endswith(".mp3")]
for sarki in dosyalar:
    kutu.insert(tk.END, sarki)

btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="▶ Çal", command=cal_secili, width=10, bg="#ff5100", fg="white", font=("Arial", 10)).grid(row=0, column=0, padx=5)
kontrol_butonu = tk.Button(btn_frame, text="⏸ Durdur", command=durdur, width=10, bg="#9308a8", fg="white", font=("Arial", 10))
kontrol_butonu.grid(row=0, column=1, padx=5)
mod_butonu = tk.Button(btn_frame, text="Mod: Normal", command=mod_degistir, width=12, bg="#3f51b5", fg="white", font=("Arial", 10))
mod_butonu.grid(row=0, column=2, padx=5)

tk.Button(root, text="YT İndirici", command=youtube_indirme_ekrani, bg="#c0392b", fg="white", font=("Arial", 10)).pack(pady=10)

status_label = tk.Label(root, text="Naber Bebuş", bg="#1e1e1e", fg="white", font=("Arial", 10, "bold"))
status_label.pack(pady=10)

sure_label = tk.Label(root, text="00:00 / 00:00", bg="#1e1e1e", fg="lightgreen", font=("Arial", 10, "bold"))
sure_label.pack(pady=5)

root.mainloop()
