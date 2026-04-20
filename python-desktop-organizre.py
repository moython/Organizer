"""
Desktop Color Organizer
-----------------------
A safe Windows desktop organizer with preview, undo log, and color themes.

Install:
    pip install customtkinter

Run:
    python desktop_color_organizer.py

Notes:
- By default this targets your Desktop folder on Windows.
- Use Preview first.
- "Apply Theme" creates colored category folders with desktop.ini + icon colors.
  Windows may cache folder icons, so refresh/restart Explorer if icons do not change immediately.
- "Organize" moves files into category folders.
- "Undo Last" restores the most recent organize operation.
"""

from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import customtkinter as ctk
    from tkinter import filedialog, colorchooser, messagebox
except Exception:
    print("Missing dependency. Install with: pip install customtkinter")
    raise

APP_NAME = "Desktop Color Organizer"
APP_DIR = Path.home() / ".desktop_color_organizer"
THEME_FILE = APP_DIR / "theme.json"
UNDO_DIR = APP_DIR / "undo_logs"
ICON_DIR = APP_DIR / "icons"
APP_DIR.mkdir(exist_ok=True)
UNDO_DIR.mkdir(exist_ok=True)
ICON_DIR.mkdir(exist_ok=True)

EXTENSION_MAP = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"},
    "Images": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".ico"},
    "Videos": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".m4a"},
    "Code": {".py", ".js", ".html", ".css", ".json", ".java", ".cpp", ".c", ".cs", ".ipynb"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Apps & Shortcuts": {".lnk", ".url", ".exe", ".msi"},
}
CATEGORY_ORDER = ["Documents", "Images", "Videos", "Audio", "Code", "Archives", "Apps & Shortcuts", "Other"]

PRESET_THEMES = {
    "Ocean": {
        "appearance": "dark",
        "accent": "blue",
        "colors": {
            "Documents": "#7dd3fc",
            "Images": "#38bdf8",
            "Videos": "#22d3ee",
            "Audio": "#2dd4bf",
            "Code": "#60a5fa",
            "Archives": "#818cf8",
            "Apps & Shortcuts": "#a78bfa",
            "Other": "#c084fc",
        },
    },
    "Sunset": {
        "appearance": "dark",
        "accent": "dark-blue",
        "colors": {
            "Documents": "#fb7185",
            "Images": "#f97316",
            "Videos": "#f59e0b",
            "Audio": "#eab308",
            "Code": "#f43f5e",
            "Archives": "#ef4444",
            "Apps & Shortcuts": "#ec4899",
            "Other": "#f472b6",
        },
    },
    "Forest": {
        "appearance": "dark",
        "accent": "green",
        "colors": {
            "Documents": "#4ade80",
            "Images": "#22c55e",
            "Videos": "#10b981",
            "Audio": "#14b8a6",
            "Code": "#84cc16",
            "Archives": "#65a30d",
            "Apps & Shortcuts": "#a3e635",
            "Other": "#bef264",
        },
    },
    "Pastel": {
        "appearance": "light",
        "accent": "blue",
        "colors": {
            "Documents": "#93c5fd",
            "Images": "#f9a8d4",
            "Videos": "#fdba74",
            "Audio": "#86efac",
            "Code": "#c4b5fd",
            "Archives": "#fca5a5",
            "Apps & Shortcuts": "#67e8f9",
            "Other": "#d8b4fe",
        },
    },
    "Monochrome": {
        "appearance": "dark",
        "accent": "dark-blue",
        "colors": {
            "Documents": "#d4d4d8",
            "Images": "#a1a1aa",
            "Videos": "#71717a",
            "Audio": "#e4e4e7",
            "Code": "#f4f4f5",
            "Archives": "#52525b",
            "Apps & Shortcuts": "#cbd5e1",
            "Other": "#94a3b8",
        },
    },
}


def default_desktop() -> Path:
    home = Path.home()
    candidates = [home / "Desktop", home / "OneDrive" / "Desktop"]
    for c in candidates:
        if c.exists():
            return c
    return home / "Desktop"


def unique_destination(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    i = 1
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def categorize(path: Path) -> str:
    suffix = path.suffix.lower()
    for category, exts in EXTENSION_MAP.items():
        if suffix in exts:
            return category
    return "Other"


def list_desktop_items(folder: Path) -> List[Path]:
    items = []
    for item in folder.iterdir():
        if item.name.startswith("~$"):
            continue
        if item.name in {APP_DIR.name}:
            continue
        if item.is_dir() and item.name in CATEGORY_ORDER:
            continue
        items.append(item)
    return items


def make_preview(folder: Path) -> Dict[str, List[Path]]:
    preview = {k: [] for k in CATEGORY_ORDER}
    for item in list_desktop_items(folder):
        if item.name.lower() in {"desktop.ini"}:
            continue
        preview[categorize(item)].append(item)
    return preview


def save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_theme() -> dict:
    if THEME_FILE.exists():
        try:
            return json.loads(THEME_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    theme = PRESET_THEMES["Ocean"]
    save_json(THEME_FILE, theme)
    return theme


def rgb_to_bgr_int(hex_color: str) -> int:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b << 16) | (g << 8) | r


def create_ico(hex_color: str, out_path: Path):
    try:
        from PIL import Image, ImageDraw
    except Exception:
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=False)
        from PIL import Image, ImageDraw
    sizes = [16, 24, 32, 48, 64, 128, 256]
    base = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base)
    rgb = tuple(int(hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    shadow = (0, 0, 0, 45)
    draw.rounded_rectangle((28, 52, 228, 196), radius=26, fill=rgb)
    draw.rounded_rectangle((18, 82, 238, 220), radius=28, fill=shadow)
    draw.rounded_rectangle((18, 72, 238, 210), radius=28, fill=tuple(max(0, min(255, c-8)) for c in rgb))
    draw.rounded_rectangle((26, 40, 128, 92), radius=18, fill=tuple(max(0, min(255, c+18)) for c in rgb))
    base.save(out_path, format="ICO", sizes=[(s, s) for s in sizes])


def apply_folder_theme(folder: Path, category: str, hex_color: str):
    category_dir = folder / category
    category_dir.mkdir(exist_ok=True)
    icon_path = ICON_DIR / f"{category.lower().replace(' ', '_').replace('&', 'and')}_{hex_color.lstrip('#')}.ico"
    if not icon_path.exists():
        create_ico(hex_color, icon_path)

    ini = category_dir / "desktop.ini"
    ini_text = f"""[.ShellClassInfo]\nIconResource={icon_path},0\nIconFile={icon_path}\nIconIndex=0\nConfirmFileOp=0\nInfoTip={category} folder\n"""
    ini.write_text(ini_text, encoding="utf-8")

    if os.name == "nt":
        subprocess.run(["attrib", "+h", "+s", str(category_dir)], shell=True)
        subprocess.run(["attrib", "+h", str(ini)], shell=True)
        try:
            import ctypes
            FILE_ATTRIBUTE_READONLY = 0x01
            FILE_ATTRIBUTE_SYSTEM = 0x04
            ctypes.windll.kernel32.SetFileAttributesW(str(category_dir), FILE_ATTRIBUTE_READONLY | FILE_ATTRIBUTE_SYSTEM)
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
        except Exception:
            pass


def organize(folder: Path) -> Tuple[int, Path]:
    preview = make_preview(folder)
    moves = []
    moved_count = 0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    undo_path = UNDO_DIR / f"undo_{timestamp}.json"

    for category, items in preview.items():
        target_dir = folder / category
        target_dir.mkdir(exist_ok=True)
        for src in items:
            if src.name.lower() == "desktop.ini":
                continue
            dest = unique_destination(target_dir / src.name)
            shutil.move(str(src), str(dest))
            moves.append({"from": str(src), "to": str(dest)})
            moved_count += 1

    save_json(undo_path, {"created_at": timestamp, "moves": moves, "desktop": str(folder)})
    return moved_count, undo_path


def last_undo_file() -> Path | None:
    files = sorted(UNDO_DIR.glob("undo_*.json"), reverse=True)
    return files[0] if files else None


def undo_last() -> int:
    undo_file = last_undo_file()
    if not undo_file:
        return 0
    data = json.loads(undo_file.read_text(encoding="utf-8"))
    moves = data.get("moves", [])
    restored = 0
    for move in reversed(moves):
        src = Path(move["to"])
        dest = Path(move["from"])
        if src.exists():
            dest = unique_destination(dest) if dest.exists() else dest
            dest.parent.mkdir(exist_ok=True)
            shutil.move(str(src), str(dest))
            restored += 1
    undo_file.unlink(missing_ok=True)
    return restored


class OrganizerApp(ctk.CTk):
    def __init__(self):
        self.theme_data = load_theme()
        ctk.set_appearance_mode(self.theme_data.get("appearance", "dark"))
        ctk.set_default_color_theme(self.theme_data.get("accent", "blue"))
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1180x760")
        self.minsize(980, 640)
        self.desktop_path = ctk.StringVar(value=str(default_desktop()))
        self.status_text = ctk.StringVar(value="Ready. Preview your desktop before organizing.")
        self.theme_name = ctk.StringVar(value=self._theme_name_from_data())
        self.category_color_vars = {cat: ctk.StringVar(value=self.theme_data["colors"][cat]) for cat in CATEGORY_ORDER}
        self.preview_frames = {}
        self._build_ui()
        self.refresh_preview()

    def _theme_name_from_data(self):
        for name, data in PRESET_THEMES.items():
            if data == self.theme_data:
                return name
        return "Custom"

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self, corner_radius=18)
        left.grid(row=0, column=0, sticky="nsw", padx=16, pady=16)
        left.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(self, corner_radius=18)
        right.grid(row=0, column=1, sticky="nsew", padx=(0,16), pady=16)
        right.grid_columnconfigure((0,1,2,3), weight=1)
        right.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(left, text="Desktop Color Organizer", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(18,4))
        ctk.CTkLabel(left, text="Organize your desktop into themed folders, preview changes, and undo safely.", wraplength=280, justify="left").grid(row=1, column=0, sticky="w", padx=18, pady=(0,14))

        path_frame = ctk.CTkFrame(left, fg_color="transparent")
        path_frame.grid(row=2, column=0, sticky="ew", padx=18, pady=(0,10))
        path_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(path_frame, text="Desktop folder").grid(row=0, column=0, sticky="w")
        ctk.CTkEntry(path_frame, textvariable=self.desktop_path, width=250).grid(row=1, column=0, sticky="ew", pady=(6,0))
        ctk.CTkButton(path_frame, text="Browse", width=80, command=self.pick_folder).grid(row=1, column=1, padx=(8,0), pady=(6,0))

        theme_frame = ctk.CTkFrame(left)
        theme_frame.grid(row=3, column=0, sticky="ew", padx=18, pady=10)
        theme_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(theme_frame, text="Theme", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(12,8))
        theme_menu = ctk.CTkOptionMenu(theme_frame, values=list(PRESET_THEMES.keys()) + ["Custom"], variable=self.theme_name, command=self.load_theme_preset)
        theme_menu.grid(row=1, column=0, sticky="ew", padx=12, pady=(0,10))

        grid = ctk.CTkScrollableFrame(theme_frame, height=260)
        grid.grid(row=2, column=0, sticky="ew", padx=12, pady=(0,12))
        for i, cat in enumerate(CATEGORY_ORDER):
            ctk.CTkLabel(grid, text=cat).grid(row=i, column=0, sticky="w", padx=(0,10), pady=6)
            swatch = ctk.CTkLabel(grid, textvariable=self.category_color_vars[cat], fg_color=self.category_color_vars[cat].get(), corner_radius=10, width=110)
            swatch.grid(row=i, column=1, sticky="ew", pady=6)
            btn = ctk.CTkButton(grid, text="Pick", width=70, command=lambda c=cat, s=swatch: self.pick_color(c, s))
            btn.grid(row=i, column=2, padx=(10,0), pady=6)
            setattr(self, f"swatch_{i}", swatch)

        action_frame = ctk.CTkFrame(left)
        action_frame.grid(row=4, column=0, sticky="ew", padx=18, pady=10)
        for idx in range(2):
            action_frame.grid_columnconfigure(idx, weight=1)
        ctk.CTkButton(action_frame, text="Preview", command=self.refresh_preview).grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(action_frame, text="Apply Theme", command=self.apply_theme).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(action_frame, text="Organize", command=self.run_organize).grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        ctk.CTkButton(action_frame, text="Undo Last", fg_color="#b45309", hover_color="#92400e", command=self.run_undo).grid(row=1, column=1, padx=10, pady=(0,10), sticky="ew")

        ctk.CTkLabel(left, textvariable=self.status_text, wraplength=300, justify="left").grid(row=5, column=0, sticky="sw", padx=18, pady=(8,18))
        left.grid_rowconfigure(5, weight=1)

        header = ctk.CTkFrame(right, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=4, sticky="ew", padx=18, pady=(18,8))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Preview Layout", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Items are grouped by file type, then displayed with your theme colors.").grid(row=1, column=0, sticky="w", pady=(4,0))

        legend = ctk.CTkFrame(right)
        legend.grid(row=1, column=0, columnspan=4, sticky="ew", padx=18, pady=(0,10))
        for i, cat in enumerate(CATEGORY_ORDER):
            dot = ctk.CTkLabel(legend, text=f"  {cat}  ", fg_color=self.category_color_vars[cat].get(), corner_radius=999)
            dot.grid(row=0, column=i, padx=6, pady=10, sticky="w")
            self.preview_frames[f"legend_{cat}"] = dot

        preview_area = ctk.CTkScrollableFrame(right)
        preview_area.grid(row=2, column=0, columnspan=4, sticky="nsew", padx=18, pady=(0,18))
        preview_area.grid_columnconfigure((0,1), weight=1)

        for idx, cat in enumerate(CATEGORY_ORDER):
            frame = ctk.CTkFrame(preview_area, corner_radius=18)
            row, col = divmod(idx, 2)
            frame.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            frame.grid_columnconfigure(0, weight=1)
            badge = ctk.CTkLabel(frame, text=cat, fg_color=self.category_color_vars[cat].get(), corner_radius=999, text_color="black")
            badge.grid(row=0, column=0, sticky="w", padx=14, pady=(14,8))
            textbox = ctk.CTkTextbox(frame, height=150)
            textbox.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0,14))
            textbox.insert("end", "No items yet")
            textbox.configure(state="disabled")
            self.preview_frames[cat] = (badge, textbox)

    def get_folder(self) -> Path:
        return Path(self.desktop_path.get()).expanduser()

    def pick_folder(self):
        selected = filedialog.askdirectory(initialdir=str(self.get_folder()), title="Select desktop folder")
        if selected:
            self.desktop_path.set(selected)
            self.refresh_preview()

    def pick_color(self, category: str, swatch):
        picked = colorchooser.askcolor(color=self.category_color_vars[category].get(), title=f"Pick color for {category}")
        if picked and picked[1]:
            self.category_color_vars[category].set(picked[1])
            swatch.configure(text=picked[1], fg_color=picked[1])
            self.theme_name.set("Custom")
            self.sync_theme_from_ui()
            self.refresh_preview_colors()

    def load_theme_preset(self, theme_name: str):
        if theme_name == "Custom":
            return
        data = PRESET_THEMES[theme_name]
        self.theme_data = json.loads(json.dumps(data))
        ctk.set_appearance_mode(self.theme_data["appearance"])
        ctk.set_default_color_theme(self.theme_data["accent"])
        for i, cat in enumerate(CATEGORY_ORDER):
            self.category_color_vars[cat].set(self.theme_data["colors"][cat])
            getattr(self, f"swatch_{i}").configure(text=self.theme_data["colors"][cat], fg_color=self.theme_data["colors"][cat])
        self.refresh_preview_colors()
        self.status_text.set(f"Loaded {theme_name} theme.")
        self.save_current_theme()

    def sync_theme_from_ui(self):
        self.theme_data = {
            "appearance": ctk.get_appearance_mode().lower(),
            "accent": self.theme_data.get("accent", "blue"),
            "colors": {cat: self.category_color_vars[cat].get() for cat in CATEGORY_ORDER},
        }
        self.save_current_theme()

    def save_current_theme(self):
        save_json(THEME_FILE, self.theme_data)

    def refresh_preview_colors(self):
        for cat in CATEGORY_ORDER:
            badge, _ = self.preview_frames[cat]
            badge.configure(fg_color=self.category_color_vars[cat].get(), text_color="black")
            self.preview_frames[f"legend_{cat}"].configure(fg_color=self.category_color_vars[cat].get(), text_color="black")

    def refresh_preview(self):
        folder = self.get_folder()
        if not folder.exists():
            self.status_text.set("Selected folder does not exist.")
            return
        preview = make_preview(folder)
        total = 0
        for cat in CATEGORY_ORDER:
            _, textbox = self.preview_frames[cat]
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            items = sorted(preview[cat], key=lambda p: p.name.lower())
            total += len(items)
            if items:
                for item in items[:60]:
                    textbox.insert("end", f"• {item.name}\n")
                if len(items) > 60:
                    textbox.insert("end", f"... and {len(items)-60} more\n")
            else:
                textbox.insert("end", "No items")
            textbox.configure(state="disabled")
        self.refresh_preview_colors()
        self.status_text.set(f"Preview ready. {total} items found on desktop.")

    def apply_theme(self):
        folder = self.get_folder()
        if not folder.exists():
            messagebox.showerror(APP_NAME, "Selected folder does not exist.")
            return
        self.sync_theme_from_ui()
        for cat in CATEGORY_ORDER:
            apply_folder_theme(folder, cat, self.category_color_vars[cat].get())
        self.status_text.set("Theme applied to category folders. You may need to refresh Explorer to see icon changes.")
        messagebox.showinfo(APP_NAME, "Theme applied to category folders. Windows may need a refresh to show new icons.")

    def run_organize(self):
        folder = self.get_folder()
        if not folder.exists():
            messagebox.showerror(APP_NAME, "Selected folder does not exist.")
            return
        count = sum(len(v) for v in make_preview(folder).values())
        if count == 0:
            messagebox.showinfo(APP_NAME, "Nothing to organize.")
            return
        ok = messagebox.askyesno(APP_NAME, f"This will move {count} item(s) into themed folders. Continue?")
        if not ok:
            return
        moved, undo_file = organize(folder)
        self.refresh_preview()
        self.status_text.set(f"Organized {moved} items. Undo log saved to {undo_file.name}.")
        messagebox.showinfo(APP_NAME, f"Organized {moved} items successfully.")

    def run_undo(self):
        restored = undo_last()
        if restored == 0:
            messagebox.showinfo(APP_NAME, "No undo log found.")
            return
        self.refresh_preview()
        self.status_text.set(f"Restored {restored} items from the last organize action.")
        messagebox.showinfo(APP_NAME, f"Restored {restored} items.")


if __name__ == "__main__":
    app = OrganizerApp()
    app.mainloop()