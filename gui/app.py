import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import json

GATEWAY_URL = "http://localhost:8000"

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
            with open(path, "rb") as f:
                resp = requests.post(f"{GATEWAY_URL}/upload", files={"study": ("study.zip", f, "application/zip")})
            resp.raise_for_status()
            job_id = resp.json()["job_id"]

            resp = requests.post(f"{GATEWAY_URL}/analyze/{job_id}", json={"anatomy": "brain"})
            resp.raise_for_status()
            data = resp.json()
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, json.dumps(data, indent=2))
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
