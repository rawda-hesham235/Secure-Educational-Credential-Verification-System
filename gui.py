import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from blockchain import Blockchain 

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, radius=15, font=("Cambria", 10, "bold")):
        temp = tk.Label(parent, text=text, font=font)
        temp.update_idletasks()
        text_width = temp.winfo_reqwidth()
        text_height = temp.winfo_reqheight()
        temp.destroy()

        padding = 40
        extra_height = 20
        width = text_width + padding
        height = text_height + extra_height

        super().__init__(parent, width=width, height=height, highlightthickness=0, bg="#141e30")
        self.command = command
        self.font = font
        self.radius = radius

        self.create_gradient(self, width, height)

        self.create_rounded_rect(2, 2, width - 2, height - 2, radius, fill="white", outline="")
        self.create_text(width // 2, height // 2, text=text, fill="black", font=font)
        self.bind("<Button-1>", lambda event: self.command())

    def create_gradient(self, canvas, width, height):
        for i in range(height):
            color = self.interpolate_color("#141e30", "#243b55", i / height)
            canvas.create_line(0, i, width, i, fill=color)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1 + r, y1, x2 - r, y1,
                  x2, y1, x2, y1 + r,
                  x2, y2 - r, x2, y2,
                  x2 - r, y2, x1 + r, y2,
                  x1, y2, x1, y2 - r,
                  x1, y1 + r, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)

    def interpolate_color(self, color1, color2, ratio):
        r1, g1, b1 = self.hex_to_rgb(color1)
        r2, g2, b2 = self.hex_to_rgb(color2)
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        return self.rgb_to_hex(r, g, b)

    def hex_to_rgb(self, hex_color):
        return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

    def rgb_to_hex(self, r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

class BlockchainApp(ttk.Frame):
    def __init__(self, master, blockchain):
        super().__init__(master)
        self.blockchain = blockchain
        master.title("File Blockchain")
        master.geometry("800x600")
        master.resizable(False, False)

        self.bg_canvas = tk.Canvas(master, width=800, height=600, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.create_gradient(self.bg_canvas, "#141e30", "#243b55")

        self.frame = tk.Frame(master, bg="#141e30")
        self.frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

        self.create_widgets()

    def create_gradient(self, canvas, color1, color2):
        for i in range(600):
            color = self.interpolate_color(color1, color2, i / 600)
            canvas.create_line(0, i, 800, i, fill=color)

    def interpolate_color(self, color1, color2, ratio):
        r1, g1, b1 = self.hex_to_rgb(color1)
        r2, g2, b2 = self.hex_to_rgb(color2)
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        return self.rgb_to_hex(r, g, b)

    def hex_to_rgb(self, hex_color):
        return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

    def rgb_to_hex(self, r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    def create_widgets(self):
        title_label = tk.Label(self.frame, text="File Blockchain", font=("Cambria", 18, "bold"),
                               fg="white", bg="#141e30")
        title_label.pack(pady=10)

        btn_frame = tk.Frame(self.frame, bg="#141e30")
        btn_frame.pack(pady=10)

        RoundedButton(btn_frame, text="Add File", command=self.add_file).grid(row=0, column=0, padx=5, pady=5)
        RoundedButton(btn_frame, text="Check File", command=self.check_file).grid(row=0, column=1, padx=5, pady=5)
        RoundedButton(btn_frame, text="Delete File", command=self.delete_file).grid(row=0, column=2, padx=5, pady=5)
        RoundedButton(btn_frame, text="Display All Files", command=self.display_all).grid(row=0, column=3, padx=5, pady=5)
        RoundedButton(btn_frame, text="Delete All Blockchain", command=self.delete_all_blockchain).grid(row=0, column=4, padx=5, pady=5)

        info_label = tk.Label(self.frame, text="Blockchain Info:", font=("Cambria", 12, "bold"),
                              fg="white", bg="#141e30")
        info_label.pack(pady=5, anchor="w", padx=20)

        self.text_area = ScrolledText(self.frame, height=15, wrap=tk.WORD, font=("Courier", 10),
                                      bg="#1c2a3a", fg="white", insertbackground="white", bd=0)
        self.text_area.pack(fill="both", expand=True, padx=20, pady=10)

    def add_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    file_data = f.read()
                file_name = os.path.basename(file_path)
                new_block = self.blockchain.add_block(file_name, file_data)
                messagebox.showinfo("Success", f"File added in block {new_block.index}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def check_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    file_data = f.read()
                block = self.blockchain.check_file(file_data)
                self.text_area.delete("1.0", tk.END)
                if block:
                    info = (
                        f"File found in block:\n"
                        f"Index: {block.index}\n"
                        f"Timestamp: {block.timestamp}\n"
                        f"File Name: {block.file_name}\n"
                        f"Block Hash: {block.hash}"
                    )
                else:
                    info = "File not found in blockchain."
                self.text_area.insert(tk.END, info)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def delete_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    file_data = f.read()
                deleted_index = self.blockchain.delete_block(file_data)
                if deleted_index is not None:
                    messagebox.showinfo("Success", f"File deleted from block {deleted_index}")
                else:
                    messagebox.showwarning("Not Found", "File not found or cannot delete Genesis Block.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def display_all(self):
        try:
            details = self.blockchain.get_all_files()
            self.text_area.delete("1.0", tk.END)
            if details:
                for detail in details:
                    self.text_area.insert(tk.END, detail)
            else:
                self.text_area.insert(tk.END, "Blockchain is empty.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def delete_all_blockchain(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete the entire blockchain?")
        if confirm:
            try:
                self.blockchain.reset_chain()
                messagebox.showinfo("Success", "Blockchain has been reset to the Genesis Block.")
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, "Blockchain has been reset.\n")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")


