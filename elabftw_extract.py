import tkinter
import tkinter.ttk as ttk
from tkinter import messagebox
import urllib.request
import urllib.parse
import json
import os
import csv
from datetime import datetime
import ssl

#-------本番環境ではやらない（自己署名証明書の回避）--------------------
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
#-------ここまで---------------------------------------------------------

# --- Global variables ---
digitos_data = None
scheme_data = None


# API Communication
class ApiError(Exception):
    pass

def call_api(url, api_key):
    """eLabFTW APIを呼び出す汎用関数"""
    try:
        req = urllib.request.Request(
            url,
            headers={"Authorization": api_key},
        )
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                raise ApiError(f"API Error: Status code {response.status}")
            return json.loads(response.read())
    except Exception as e:
        raise ApiError(f"Failed to call API: {e}")

# ==============================================================================
# Data Fetching Logic
# ==============================================================================
def fetch_data(url_entry, key_entry, id_entry, status_label, right_frame):
    """「Fetch Data」ボタンが押されたときの処理"""
    global digitos_data, scheme_data
    
    base_url = url_entry.get().strip()
    api_key = key_entry.get().strip()
    exp_id = id_entry.get().strip()

    if not all([base_url, api_key, exp_id]):
        messagebox.showerror("Error", "URL, API Key, and Experiment ID are required.")
        return

    status_label.config(text="Fetching data...")
    status_label.update()

    try:
        # 1. 実験ノートのアップロードファイル一覧を取得
        uploads_url = f"{base_url.rstrip('/')}/api/v2/experiments/{exp_id}/uploads"
        uploads = call_api(uploads_url, api_key)

        # 2. 目的のJSONファイルを探す
        digitos_file_info = next((f for f in uploads if f['real_name'] == f"DigiTOS_Info_{exp_id}.json"), None)
        scheme_file_info = next((f for f in uploads if f['real_name'] == f"Reaction_Scheme_{exp_id}.json"), None)

        # 3. 各ファイルの内容をダウンロード
        digitos_data = None
        scheme_data = None

        if digitos_file_info:
            download_url = f"{base_url.rstrip('/')}/api/v2/experiments/{exp_id}/uploads/{digitos_file_info['id']}?format=binary"
            digitos_data = call_api(download_url, api_key)
        
        if scheme_file_info:
            download_url = f"{base_url.rstrip('/')}/api/v2/experiments/{exp_id}/uploads/{scheme_file_info['id']}?format=binary"
            scheme_data = call_api(download_url, api_key)

        if not digitos_data and not scheme_data:
            raise ApiError("Neither Digi-TOS Info nor Reaction Scheme JSON file was found.")

        status_label.config(text="Fetch successful. Please select options and export.")
        create_export_frame(right_frame)

    except ApiError as e:
        messagebox.showerror("API Error", str(e))
        status_label.config(text="Fetch failed.")

# ==============================================================================
# Data Export Logic (Updated: BOM for Excel support)
# ==============================================================================
def export_data(include_digitos_var, include_scheme_var, format_var):
    """「Export」ボタンが押されたときの処理"""
    try:
        include_digitos = include_digitos_var.get()
        include_scheme = include_scheme_var.get()
        file_format = format_var.get()

        if not include_digitos and not include_scheme:
            messagebox.showwarning("Warning", "Please select at least one data type to export.")
            return

        # --- データを単一の辞書にまとめる ---
        record = {}
        
        # 1. Digi-TOSデータの処理
        if include_digitos and digitos_data:
            for key, value in digitos_data.items():
                if isinstance(value, list):
                    record[key] = ", ".join(map(str, value))
                else:
                    record[key] = value

        # 2. Reaction Schemeデータの処理
        if include_scheme and scheme_data:
            for table_name, table_data in scheme_data.items():
                # graphデータなどのリスト以外のものはスキップ
                if not isinstance(table_data, list):
                    continue

                for i, row_data in enumerate(table_data):
                    # --- パターンA: 新しい形式 (辞書/オブジェクト) ---
                    if isinstance(row_data, dict):
                        for key, val in row_data.items():
                            prefix = table_name.rstrip('s').capitalize()
                            column_name = f"{prefix}_{i+1}_{key}"
                            record[column_name] = val
                    
                    # --- パターンB: 古い形式 (リスト/配列) ---
                    elif isinstance(row_data, list):
                        for j, cell_value in enumerate(row_data):
                            column_name = f"{table_name.capitalize()}_{i+1}_{j+1}"
                            record[column_name] = cell_value
        
        if not record:
            messagebox.showerror("Error", "No data available to export.")
            return

        # --- ファイルへの書き込み（縦書き） ---
        delimiter = '\t' if file_format == 'tsv' else ','
        extension = file_format
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"elabftw_export_{timestamp}.{extension}"

        # ★修正ポイント: encoding='utf-8-sig' に変更しました
        # これによりBOM（バイト順マーク）が付き、Excelで文字化けしなくなります
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=delimiter)
            
            # ヘッダー行を出力
            writer.writerow(['Field Name', 'Value'])
            
            # キーをアルファベット順にソートして出力
            sorted_keys = sorted(record.keys())
            
            for key in sorted_keys:
                value = record[key]
                writer.writerow([key, value])
            
        messagebox.showinfo("Success", f"Exported successfully to:\n{os.path.abspath(filename)}")

    except Exception as e:
        print(f"Export Error: {e}") 
        messagebox.showerror("Export Error", f"An error occurred during export:\n{e}")

# ==============================================================================
# GUI Setup
# ==============================================================================
def create_export_frame(frame):
    """データ取得後に右フレームにUIを生成する"""
    for widget in frame.winfo_children():
        widget.destroy()

    # --- チェックボックス ---
    ttk.Label(frame, text="Select Data to Export:", font=("Arial", 13, "bold")).pack(anchor='w', pady=(0, 10))
    
    include_digitos_var = tkinter.BooleanVar(value=(digitos_data is not None))
    digitos_check = ttk.Checkbutton(frame, text="Digi-TOS Info", variable=include_digitos_var, state=tkinter.NORMAL if digitos_data else tkinter.DISABLED)
    digitos_check.pack(anchor='w', padx=10)

    include_scheme_var = tkinter.BooleanVar(value=(scheme_data is not None))
    scheme_check = ttk.Checkbutton(frame, text="Reaction Scheme", variable=include_scheme_var, state=tkinter.NORMAL if scheme_data else tkinter.DISABLED)
    scheme_check.pack(anchor='w', padx=10)
    
    # --- 保存形式 ---
    ttk.Label(frame, text="Select Format:", font=("Arial", 13, "bold")).pack(anchor='w', pady=(20, 10))
    format_var = tkinter.StringVar(value='tsv')
    tsv_radio = ttk.Radiobutton(frame, text="TSV (Tab-separated)", variable=format_var, value='tsv')
    tsv_radio.pack(anchor='w', padx=10)
    csv_radio = ttk.Radiobutton(frame, text="CSV (Comma-separated)", variable=format_var, value='csv')
    csv_radio.pack(anchor='w', padx=10)

    # --- Exportボタン ---
    export_button = ttk.Button(
        frame,
        text="Export to File",
        command=lambda: export_data(include_digitos_var, include_scheme_var, format_var)
    )
    export_button.pack(pady=30, ipadx=10, ipady=5)

def main():
    root = tkinter.Tk()
    root.title("eLabFTW JSON Exporter")
    root.geometry("800x500")

    # --- Left Frame (Inputs) ---
    left_frame = ttk.Frame(root, padding=20)
    left_frame.pack(side='left', fill='y', expand=False)

    ttk.Label(left_frame, text="eLabFTW Connection", font=("Arial", 16, "bold")).pack(anchor='w', pady=(0, 20))

    ttk.Label(left_frame, text="eLabFTW URL (e.g., https://localhost)").pack(anchor='w')
    url_entry = ttk.Entry(left_frame, width=50)
    url_entry.pack(anchor='w', pady=(0, 10))

    ttk.Label(left_frame, text="API Key").pack(anchor='w')
    key_entry = ttk.Entry(left_frame, width=50, show="*")
    key_entry.pack(anchor='w', pady=(0, 10))

    ttk.Label(left_frame, text="Experiment ID").pack(anchor='w')
    id_entry = ttk.Entry(left_frame, width=50)
    id_entry.pack(anchor='w', pady=(0, 20))
    
    fetch_button = ttk.Button(left_frame, text="Fetch Data")
    fetch_button.pack(pady=10, ipadx=10, ipady=5)
    
    status_label = ttk.Label(left_frame, text="", font=("Arial", 10))
    status_label.pack(pady=10)

    # --- Right Frame (Outputs) ---
    right_frame = ttk.Frame(root, padding=20)
    right_frame.pack(side='right', fill='both', expand=True)
    
    ttk.Label(right_frame, text="Export Options", font=("Arial", 16, "bold")).pack(anchor='w', pady=(0, 20))
    initial_label = ttk.Label(right_frame, text="Please fetch data first.", wraplength=300)
    initial_label.pack()

    # --- Bind fetch button command ---
    fetch_button.config(command=lambda: fetch_data(url_entry, key_entry, id_entry, status_label, right_frame))

    root.mainloop()

if __name__ == "__main__":
    main()