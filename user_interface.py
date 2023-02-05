import customtkinter as ctk
import tkinter as tk
import downloader
import time
import threading
import os
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from pytube import exceptions

path = None
stream = None
youtube_video = None
loading = True
file_size_int = 0

home = os.path.expanduser('~')
path = os.path.join(home, 'Downloads')


def set_theme(mode):
    ctk.set_appearance_mode(mode.split(' ')[0])


def ok_command():
    global youtube_video
    try:
        youtube_video = downloader.video(
            entry.get(), on_progress_callback=on_progress, on_complete_callback=finish_download)
    except exceptions.RegexMatchError:
        if not entry.get() == 'thank you':
            messagebox.showerror(
                title='Unvalid URL!', message='The url you entered is invalid. Please make sure you typed the url correctly.')
        else:
            messagebox.showinfo('Seminet:', "It's my pleasure. :)")
        return False
    except (exceptions.AgeRestrictedError, exceptions.MembersOnly, exceptions.VideoPrivate, exceptions.VideoRegionBlocked, exceptions.VideoUnavailable):
        messagebox.showerror(
            'Video Unavailable', 'The video you want to download cannot be found. Video may be age restricted, removed from your region, members only, or private.')
        return False
    except Exception:
        messagebox.showerror(
            'Error', 'An error has occurred. Please try again.')
        return False
    file_size.set('')
    resolutions_menu.configure(state='disabled')
    continue_button.configure('normal')
    download_button.configure('disabled')
    title.set(youtube_video.title)
    channel.set(youtube_video.author)
    length.set(youtube_video.length_str())
    photo = youtube_video.thumbnail_image()
    thumbnail_label.config(image=photo)
    thumbnail_label.image = photo
    continue_button.configure(state='normal')


def continue_download():
    global loading, streaming_thread, loading_thread
    loading = True
    resolutions_menu.configure(state='disabled')
    continue_button.configure(state='disabled')
    streaming_thread = threading.Thread(target=stream_video, daemon=True)
    loading_thread = threading.Thread(target=loading_animation, daemon=True)
    streaming_thread.start()
    loading_thread.start()


def stream_video():
    global stream, loading
    stream = youtube_video.streams.filter(progressive=True)
    loading = False


def loading_animation():
    while loading:
        loading_text.set('Loading')
        time.sleep(0.3)
        loading_text.set('Loading.')
        time.sleep(0.3)
        loading_text.set('Loading..')
        time.sleep(0.3)
        loading_text.set('Loading...')
        time.sleep(0.3)
        if not loading:
            loading_text.set('')
            continue_button.configure(state='disabled')
            download_button.configure(state='normal')
            file_size.set(
                str(int(stream.get_highest_resolution().filesize_mb))+' MB')
            list_resolutions()
            resolutions_menu.configure(state='normal')


def list_resolutions():
    global videos, video_resolutions, video_itags
    videos = []
    video_resolutions = []
    video_itags = []
    for per_stream in stream:
        videos.append(per_stream)
        video_resolutions.append(per_stream.resolution)
        video_itags.append(per_stream.itag)
    resolutions_menu.configure(values=video_resolutions)
    resolutions_menu.set(video_resolutions[-1])


def set_directory():
    global path
    path = askdirectory()


def get_file_size(value):
    file_size.set(
        str(int(videos[video_resolutions.index(value)].filesize_mb))+' MB')


def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress_bar.set(bytes_downloaded / total_size)
    mb_downloaded = round((bytes_downloaded/1024/1024), 2)
    mb_total_size = round((total_size/1024/1024), 2)
    bytes_completed.set(str(mb_downloaded)+' / '+str(mb_total_size)+' MB')
    if bytes_downloaded == total_size:
        progress_bar.set(1)


def finish_download(a, b):
    messagebox.showinfo(
        'Download Completed', 'Your video has been downloaded successfully. Video location: \n'+str(b))
    download_ok_button.configure(state='normal')


def download_command():
    streaming_thread.join()
    loading_thread.join()
    global progress_bar, bytes_remained, download_ok_button, progress_window
    progress_window = ctk.CTkToplevel(root)

    progress_window.title('Download Progress')
    progress_window.resizable(False, False)

    w = 430
    h = 96
    progress_window.geometry(
        f'{w}x{h}+{int((root.winfo_screenwidth()-w)/2)}+{int((root.winfo_screenheight()-h)/2)}')

    label_frame = ctk.CTkFrame(
        master=progress_window, fg_color='transparent', border_width=0)

    download_label = ctk.CTkLabel(
        master=label_frame, text='Downloading Video:')
    bytes_label = ctk.CTkLabel(
        master=label_frame, textvariable=bytes_completed)
    progress_bar = ctk.CTkProgressBar(
        master=progress_window, width=400, height=10, progress_color='#00FF00', determinate_speed=0.03)
    download_ok_button = ctk.CTkButton(
        master=progress_window, text='OK', state='disabled', command=progress_window.destroy)
    progress_bar.set(0)
    label_frame.grid(row=0, column=0, columnspan=2,
                     padx=10, pady=5)
    download_label.grid(row=0, column=0, padx=5)
    bytes_label.grid(row=0, column=1, padx=5)
    progress_bar.grid(row=1, column=0, columnspan=3, padx=15)
    download_ok_button.grid(row=2, column=2, padx=15, pady=(10, 15))

    video = videos[video_resolutions.index(resolutions_menu.get())]
    bytes_completed.set('0 / '+str(int(video.filesize_mb))+' MB')
    downloading_thread = threading.Thread(target=video.download, kwargs={
                                          'output_path': path}, daemon=True)
    downloading_thread.start()


ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('red_theme.json')

root = ctk.CTk()


url = ctk.StringVar()
url.set('https://www.youtube.com/watch?v=MNeX4EGtR5Y&ab_channel=Fireship')
title = ctk.StringVar(
    value='SeminetScienceInnovatorsYoutubeVideoDownloader')
channel = ctk.StringVar(value='By Seminet')
length = ctk.StringVar(value='4:51')
resolution = ctk.StringVar(value='720p')
file_size = ctk.StringVar()
loading_text = ctk.StringVar(value='')
bytes_completed = ctk.StringVar()


root.title('Youtube Video Downloader')
root.withdraw()

main_window = ctk.CTkToplevel(root)

main_window.iconbitmap('appicon.ico')

main_window.protocol('WM_DELETE_WINDOW', root.destroy)
main_window.title('Youtube Video Downloader | Seminet Science Innovators')
x = 660
y = 270
main_window.geometry(
    f'{x}x{y}+{int((root.winfo_screenwidth()-x)/2)}+{int((root.winfo_screenheight()-y)/2)}')
main_window.resizable(width=False, height=False)

main_window.columnconfigure(1, weight=1)

entry = ctk.CTkEntry(master=main_window, font=('Roboto', 12), textvariable=url)

information = ctk.CTkFrame(master=main_window)
information.columnconfigure(1, weight=1)


first_video = downloader.video(url.get())

photo = first_video.thumbnail_image()
thumbnail_label = tk.Label(master=information, image=photo)
thumbnail_label.image = photo


title_label = ctk.CTkLabel(
    master=information, textvariable=title, font=('Roboto', 14), justify=tk.LEFT, wraplength=190)

channel_label = ctk.CTkLabel(
    master=information, textvariable=channel, font=('Roboto', 12))

length_label = ctk.CTkLabel(
    master=information, textvariable=length, font=('Roboto', 12))


thumbnail_label.grid(row=0, column=0, rowspan=2,
                     padx=(12, 5), pady=10, sticky=tk.N+tk.W)
title_label.grid(row=0, column=1, columnspan=2,
                 padx=(5, 15), pady=13, sticky=tk.N+tk.W)
channel_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.S+tk.W)
length_label.grid(row=1, column=2, padx=(5, 15), pady=5, sticky=tk.S+tk.E)


button_frame = ctk.CTkFrame(
    master=main_window, fg_color='transparent', border_width=0)
ok_button = ctk.CTkButton(master=button_frame, text='OK', command=ok_command)
continue_button = ctk.CTkButton(
    master=button_frame, text='Continue', state='disabled', command=continue_download)
theme_button = ctk.CTkOptionMenu(master=button_frame, values=[
                                 'Light Mode', 'Dark Mode'], anchor=ctk.CENTER, command=set_theme)
theme_button.set('Dark Mode')

loading_label = ctk.CTkLabel(master=main_window, textvariable=loading_text)
# Download Section
download_frame = ctk.CTkFrame(master=main_window)
download_frame.grid_columnconfigure(2, weight=1)
directory_button = ctk.CTkButton(
    master=download_frame, text='Select Folder', command=set_directory)
resolutions_menu = ctk.CTkOptionMenu(master=download_frame, variable=resolution, values=[
                                     '144p', '240p', '360p', '480p', '720p'], anchor=ctk.CENTER, state='disabled', command=get_file_size)
file_size_label = ctk.CTkLabel(master=download_frame, textvariable=file_size)
download_button = ctk.CTkButton(
    master=download_frame, text='Download', state='disabled', command=download_command)

# Grids
entry.grid(row=1, column=0, columnspan=5, padx=10,
           pady=(10, 5), sticky=tk.E+tk.W)
information.grid(row=2, column=0, rowspan=2, columnspan=3,
                 padx=10, pady=5, sticky=tk.W+tk.N+tk.E)
button_frame.grid(row=2, column=4,
                  padx=10, pady=5, sticky=tk.N+tk.E)
ok_button.grid(row=0, column=0, pady=5)
continue_button.grid(row=1, column=0, pady=5)
theme_button.grid(row=2, column=0, pady=5)
loading_label.grid(row=3, column=4, padx=10, sticky=tk.S)
download_frame.grid(row=4, column=0, columnspan=5,
                    padx=10, pady=5, sticky=tk.E+tk.W)
directory_button.grid(row=0, column=1, padx=(10, 5), pady=8)
resolutions_menu.grid(row=0, column=2, padx=5, pady=8, sticky=tk.W)
file_size_label.grid(row=0, column=3, padx=5, pady=8, sticky=tk.E)
download_button.grid(row=0, column=4, padx=5, pady=8, sticky=tk.E)

root.mainloop()
