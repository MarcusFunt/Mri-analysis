import tkinter as tk
from tkinter import filedialog, messagebox
import json

from desktop_pipeline import analyze_zip


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MRI Analyzer")
        self.geometry("500x400")
        self.file_path = tk.StringVar()

        tk.Button(self, text="Select ZIP", command=self.select_file).pack(pady=5)
        tk.Label(self, textvariable=self.file_path).pack()
        tk.Button(self, text="Analyze", command=self.run_analysis).pack(pady=5)

        self.output = tk.Text(self, height=15)
        self.output.pack(fill="both", expand=True)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
        if path:
            self.file_path.set(path)

    def run_analysis(self):
        path = self.file_path.get()
        if not path:
            messagebox.showerror("Error", "Please select a ZIP file")
            return
        try:
            data = analyze_zip(path)
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, json.dumps(data, indent=2))
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
