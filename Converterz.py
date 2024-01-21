import os
import sys
import hashlib
import datetime
import logging
import threading
import tkinter as tk
from tkinter import ttk, PhotoImage, messagebox
from PIL import Image, ImageTk

class ImageConverter:
    OUTPUT_FORMATS = ["webp", "jpeg", "png"]
    DEFAULT_RESIZE_PERCENTAGE = "100"
    DEFAULT_QUALITY_PERCENTAGE = "100"
    VERSION = "1.3"

    def __init__(self, master):
        self.master = master
        master.title("Image Converter")
        master.resizable(False, False)

        # Add icon for the application window
        if getattr(sys, 'frozen', False):
            # We are running in a bundle
            bundle_dir = sys._MEIPASS
        else:
            # We are running in a normal Python environment
            bundle_dir = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(bundle_dir, "logo.icns")
        master.wm_iconbitmap(icon_path)  # Change to wm_iconphoto for macOS compatibility

        # Add icon for the tab
        tab_icon_path = os.path.join(bundle_dir, "tab_icon.png")
        if os.path.exists(tab_icon_path):
            master.tk.call('wm', 'iconphoto', master._w, PhotoImage(file=tab_icon_path))

        self.image_path = ""
        self.new_format = tk.StringVar(value=self.OUTPUT_FORMATS[0])
        self.resize_percentage = tk.StringVar(value=self.DEFAULT_RESIZE_PERCENTAGE)
        self.quality_percentage = tk.StringVar(value=self.DEFAULT_QUALITY_PERCENTAGE)
        self.naming_method = tk.StringVar(value="hash_only")

        self.create_widgets()

        self.converterz_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Converterz")
        os.makedirs(self.converterz_folder, exist_ok=True)

        self.log_file_path = os.path.join(self.converterz_folder, "converter_log.txt")
        logging.basicConfig(filename=self.log_file_path, level=logging.INFO)

        copyright_label = tk.Label(master, text=f"Copyright © 2024 Hamidreza Derhami | Version {self.VERSION}")
        copyright_label.grid(row=10, column=0, columnspan=2, pady=5)

    def show_success_message(self, message):
        messagebox.showinfo("Success", message)

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

    def center_window(self):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        window_width = 420
        window_height = 640

        x_coordinate = int((screen_width - window_width) / 2)
        y_coordinate = int((screen_height - window_height) / 2)

        self.master.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

    def create_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.preview_frame = ttk.LabelFrame(main_frame, text="Preview Image:")
        self.preview_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.canvas = tk.Canvas(self.preview_frame, width=350, height=200, bd=0, highlightthickness=0)
        self.canvas.pack()

        naming_frame = ttk.LabelFrame(main_frame, text="Naming Method:")
        naming_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Radiobutton(naming_frame, text="Hash Only", variable=self.naming_method, value="hash_only").grid(row=0, column=0, pady=5)
        ttk.Radiobutton(naming_frame, text="Hash + Timestamp", variable=self.naming_method, value="hash_timestamp").grid(row=0, column=1, pady=5)
        ttk.Radiobutton(naming_frame, text="Original Filename", variable=self.naming_method, value="original_filename").grid(row=0, column=2, pady=5)

        select_format_frame = ttk.LabelFrame(main_frame, text="Select Output Format:")
        select_format_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        for i, format in enumerate(self.OUTPUT_FORMATS):
            ttk.Radiobutton(select_format_frame, text=format.upper(), variable=self.new_format, value=format).grid(row=0, column=i)

        resize_quality_frame = ttk.LabelFrame(main_frame, text="Resize and Quality:")
        resize_quality_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(resize_quality_frame, text="Resize Percentage:").grid(row=0, column=0, pady=5)
        tk.Entry(resize_quality_frame, textvariable=self.resize_percentage).grid(row=0, column=1, pady=5)

        tk.Label(resize_quality_frame, text="Quality Percentage:").grid(row=1, column=0, pady=5)
        tk.Entry(resize_quality_frame, textvariable=self.quality_percentage).grid(row=1, column=1, pady=5)

        convert_button_frame = ttk.Frame(main_frame)
        convert_button_frame.grid(row=4, column=0, pady=10)

        self.convert_button = tk.Button(convert_button_frame, text="Convert", command=self.convert_image, width=36, height=2)
        self.convert_button.pack()

        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

    def remove_preview(self):
        self.canvas.delete("all")

    def display_preview(self):
        if self.image_path:
            try:
                image = Image.open(self.image_path)
                image.thumbnail((350, 200))
                photo = ImageTk.PhotoImage(image)
                self.canvas.image = photo
                self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            except Exception as e:
                logging.error(f"Error displaying preview image: {str(e)}")

    def convert_image(self):
        if not self.image_path:
            logging.error("Please select an image first!")
            return

        try:
            self.convert_button.config(state=tk.DISABLED)
            convert_thread = threading.Thread(target=self.convert_image_async)
            convert_thread.start()

        except Exception as e:
            logging.error(f"Error converting image: {str(e)}")

    def convert_image_async(self):
        try:
            hash_value, timestamp = self.get_image_info()
            new_file_name = self.generate_new_filename(hash_value, timestamp)
            new_file_path = os.path.join(self.converterz_folder, new_file_name)

            image = Image.open(self.image_path)
            self.resize_image(image)
            self.save_image(image, new_file_path)

            logging.info(f"Image converted: {new_file_path}")

            messagebox.showinfo("Conversion Complete", "Image conversion completed successfully!")

        except Exception as e:
            logging.error(f"Error converting image: {str(e)}")
            self.show_error_message(f"Error converting image: {str(e)}")

        finally:
            self.cleanup()

    def get_image_info(self):
        with open(self.image_path, "rb") as f:
            data = f.read()
            hash_object = hashlib.md5()
            hash_object.update(data)
            hash_value = hash_object.hexdigest()

        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(self.image_path))
        timestamp = creation_time.strftime("%Y%m%d")

        return hash_value, timestamp

    def generate_new_filename(self, hash_value, timestamp):
        original_filename = os.path.basename(self.image_path)

        if self.naming_method.get() == "hash_only":
            return f"{hash_value}.{self.new_format.get()}"
        elif self.naming_method.get() == "hash_timestamp":
            return f"{hash_value}_{timestamp}.{self.new_format.get()}"
        elif self.naming_method.get() == "original_filename":
            return f"{original_filename}.{self.new_format.get()}"

    def resize_image(self, image):
        resize_percentage = int(self.resize_percentage.get())
        if resize_percentage != 100:
            width, height = image.size
            new_size = (int(width * resize_percentage / 100), int(height * resize_percentage / 100))
            image.thumbnail(new_size)

    def save_image(self, image, file_path):
        quality_percentage = int(self.quality_percentage.get())
        image.save(file_path, format=self.new_format.get(), quality=quality_percentage)

    def cleanup(self):
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)
        self.convert_button.config(state=tk.NORMAL)

    def on_enter(self, event):
        self.canvas.config(bg="#e0e0e0")

    def on_leave(self, event):
        self.canvas.config(bg="white")

    def on_drag_motion(self, event):
        x, y = event.x, event.y
        self.canvas.coords("all", x, y)

    def on_drop(self, event):
        x, y = event.x, event.y
        self.remove_preview()
        self.image_path = ""
        self.convert_button.config(state=tk.DISABLED)

        try:
            # Modified: Use splitlist for compatibility with both Windows and macOS
            dropped_files = self.master.tk.splitlist(self.master.tk.call("tk_getOpenFile", "-multiple", "1"))
            if dropped_files:
                self.image_path = dropped_files[0]
                self.display_preview()
                self.convert_button.config(state=tk.NORMAL)
        except Exception as e:
            logging.error(f"Error getting dropped files: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverter(root)
    app.center_window()
    root.mainloop()
