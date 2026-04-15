#This module defines the FileSearchApp class, which is a Tkinter-based GUI application for scanning folders, indexing file metadata, and providing search and filter functionalities.
from pathlib import Path
import sys
import os
import hashlib
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, filedialog

from tkinterdnd2 import DND_FILES, TkinterDnD

from scanner.file_scanner import FileScanner
from storage.index_storage import IndexStorage
from search.search_engine import SearchEngine
from search.filters import FileFilter
from search.sorter import FileSorter
from search.paginator import Paginator

class FileSearchApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("File Search Indexer")
        self.geometry("1500x920")
        self.minsize(1260, 780)
        self.configure(bg="#0b1220")

        self.records = []
        self.current_results = []
        self.current_page = 1

        json_file, sqlite_file = self.get_app_data_paths()

        self.storage = IndexStorage(
            json_file=json_file,
            sqlite_file=sqlite_file
        )

        self.folder_var = tk.StringVar()
        self.search_name_var = tk.StringVar()
        self.extension_var = tk.StringVar()
        self.min_size_var = tk.StringVar()
        self.max_size_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="name")
        self.order_var = tk.StringVar(value="asc")
        self.page_size_var = tk.StringVar(value="15")
        self.recent_days_var = tk.StringVar(value="7")

        self.total_files_var = tk.StringVar(value="0")
        self.visible_results_var = tk.StringVar(value="0")
        self.total_size_var = tk.StringVar(value="0 bytes")
        self.page_info_var = tk.StringVar(value="Page 0 / 0")

        self.selected_name_var = tk.StringVar(value="-")
        self.selected_extension_var = tk.StringVar(value="-")
        self.selected_size_var = tk.StringVar(value="-")
        self.selected_date_var = tk.StringVar(value="-")
        self.selected_path_var = tk.StringVar(value="-")

        self.toast_frame = None
        self.toast_after_id = None

        self.search_popup = None
        self.filter_popup = None
        self.recent_popup = None
        self.duplicate_popup = None

        self.setup_style()
        self.create_layout()

    def get_app_data_paths(self):
        app_support_dir = Path.home() / "Library" / "Application Support" / "FileSearchIndexer"
        app_support_dir.mkdir(parents=True, exist_ok=True)

        json_file = app_support_dir / "file_index.json"
        sqlite_file = app_support_dir / "file_index.db"

        return str(json_file), str(sqlite_file)    

    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("App.TFrame", background="#0b1220")
        style.configure("Card.TFrame", background="#111827")

        style.configure(
            "Title.TLabel",
            background="#0b1220",
            foreground="#f8fafc",
            font=("Helvetica", 22, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background="#0b1220",
            foreground="#94a3b8",
            font=("Helvetica", 10)
        )

        style.configure(
            "Section.TLabel",
            background="#111827",
            foreground="#e5e7eb",
            font=("Helvetica", 11, "bold")
        )

        style.configure(
            "Field.TLabel",
            background="#111827",
            foreground="#cbd5e1",
            font=("Helvetica", 10, "bold")
        )

        style.configure(
            "Muted.TLabel",
            background="#111827",
            foreground="#94a3b8",
            font=("Helvetica", 10)
        )

        style.configure(
            "Modern.TButton",
            background="#1e293b",
            foreground="#f8fafc",
            borderwidth=0,
            focusthickness=0,
            padding=(10, 8),
            font=("Helvetica", 10, "bold")
        )
        style.map(
            "Modern.TButton",
            background=[("active", "#334155"), ("pressed", "#475569")]
        )

        style.configure(
            "Accent.TButton",
            background="#2563eb",
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            padding=(10, 8),
            font=("Helvetica", 10, "bold")
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#3b82f6"), ("pressed", "#1d4ed8")]
        )

        style.configure(
            "Panel.TButton",
            background="#172033",
            foreground="#e5e7eb",
            borderwidth=0,
            focusthickness=0,
            padding=(12, 9),
            font=("Helvetica", 10, "bold")
        )
        style.map(
            "Panel.TButton",
            background=[("active", "#243146"), ("pressed", "#334155")]
        )

        style.configure(
            "Modern.TEntry",
            fieldbackground="#0f172a",
            foreground="#f8fafc",
            bordercolor="#334155",
            lightcolor="#334155",
            darkcolor="#334155",
            insertcolor="#f8fafc",
            padding=7
        )

        style.configure(
            "Modern.TCombobox",
            fieldbackground="#0f172a",
            background="#0f172a",
            foreground="#f8fafc",
            bordercolor="#334155",
            lightcolor="#334155",
            darkcolor="#334155",
            arrowcolor="#e5e7eb",
            padding=6
        )

        style.configure(
            "Treeview",
            background="#0f172a",
            fieldbackground="#0f172a",
            foreground="#e5e7eb",
            borderwidth=0,
            rowheight=30,
            font=("Helvetica", 10)
        )
        style.map(
            "Treeview",
            background=[("selected", "#1d4ed8")],
            foreground=[("selected", "#ffffff")]
        )

        style.configure(
            "Treeview.Heading",
            background="#172033",
            foreground="#f8fafc",
            font=("Helvetica", 10, "bold"),
            relief="flat"
        )

    def create_layout(self):
        root = ttk.Frame(self, style="App.TFrame", padding=14)
        root.pack(fill="both", expand=True)

        self.create_header(root)
        self.create_top_section(root)
        self.create_stats_row(root)
        self.create_tools_section(root)
        self.create_main_content(root)

    def create_header(self, parent):
        header = ttk.Frame(parent, style="App.TFrame")
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(
            header,
            text="File Search Indexer",
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Scan folders, browse indexed files, and use search, filters, recent files, and duplicate finder.",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(3, 0))

    def create_top_section(self, parent):
        card = self.make_card(parent)
        card.pack(fill="x", pady=(0, 10))

        content = ttk.Frame(card, style="Card.TFrame")
        content.pack(fill="x")

        ttk.Label(content, text="Folder Input", style="Section.TLabel").grid(
            row=0, column=0, columnspan=8, sticky="w", pady=(0, 8)
        )

        ttk.Label(content, text="Folder Path", style="Field.TLabel").grid(
            row=1, column=0, sticky="w", pady=(0, 5)
        )

        folder_entry = ttk.Entry(
            content,
            textvariable=self.folder_var,
            style="Modern.TEntry"
        )
        folder_entry.grid(row=2, column=0, columnspan=4, sticky="ew", padx=(0, 8))

        ttk.Button(
            content,
            text="Browse",
            style="Modern.TButton",
            command=self.browse_folder
        ).grid(row=2, column=4, padx=4, sticky="ew")

        ttk.Button(
            content,
            text="Scan Folder",
            style="Accent.TButton",
            command=self.scan_folder
        ).grid(row=2, column=5, padx=4, sticky="ew")

        ttk.Button(
            content,
            text="Save JSON",
            style="Modern.TButton",
            command=self.save_json
        ).grid(row=2, column=6, padx=4, sticky="ew")

        ttk.Button(
            content,
            text="Save SQLite",
            style="Modern.TButton",
            command=self.save_sqlite
        ).grid(row=2, column=7, padx=4, sticky="ew")

        ttk.Button(
            content,
            text="Load JSON",
            style="Modern.TButton",
            command=self.load_json
        ).grid(row=3, column=6, padx=4, pady=(6, 0), sticky="ew")

        ttk.Button(
            content,
            text="Load SQLite",
            style="Modern.TButton",
            command=self.load_sqlite
        ).grid(row=3, column=7, padx=4, pady=(6, 0), sticky="ew")

        drop_box = tk.Frame(
            content,
            bg="#0f172a",
            highlightthickness=1,
            highlightbackground="#334155",
            bd=0
        )
        drop_box.grid(row=3, column=0, columnspan=6, sticky="ew", pady=(10, 0))

        self.drop_label = tk.Label(
            drop_box,
            text="Drag and drop a folder here",
            bg="#0f172a",
            fg="#cbd5e1",
            font=("Helvetica", 11, "bold"),
            pady=14
        )
        self.drop_label.pack(fill="x")

        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self.handle_drop)

        for i in range(8):
            content.columnconfigure(i, weight=1)

    def create_stats_row(self, parent):
        row = ttk.Frame(parent, style="App.TFrame")
        row.pack(fill="x", pady=(0, 10))

        self.create_stat_card(row, "Total Files", self.total_files_var).pack(
            side="left", fill="x", expand=True, padx=(0, 5)
        )
        self.create_stat_card(row, "Visible Results", self.visible_results_var).pack(
            side="left", fill="x", expand=True, padx=5
        )
        self.create_stat_card(row, "Total Size", self.total_size_var).pack(
            side="left", fill="x", expand=True, padx=5
        )
        self.create_stat_card(row, "Page", self.page_info_var).pack(
            side="left", fill="x", expand=True, padx=(5, 0)
        )

    def create_stat_card(self, parent, title, variable):
        card = tk.Frame(
            parent,
            bg="#111827",
            highlightthickness=1,
            highlightbackground="#1f2937",
            bd=0
        )

        inner = ttk.Frame(card, style="Card.TFrame", padding=12)
        inner.pack(fill="both", expand=True)

        ttk.Label(inner, text=title, style="Muted.TLabel").pack(anchor="w")

        tk.Label(
            inner,
            textvariable=variable,
            bg="#111827",
            fg="#f8fafc",
            font=("Helvetica", 16, "bold")
        ).pack(anchor="w", pady=(6, 0))

        return card

    def create_tools_section(self, parent):
        card = self.make_card(parent)
        card.pack(fill="x", pady=(0, 10))

        content = ttk.Frame(card, style="Card.TFrame")
        content.pack(fill="x")

        ttk.Label(content, text="Tools", style="Section.TLabel").pack(anchor="w", pady=(0, 8))

        row = ttk.Frame(content, style="Card.TFrame")
        row.pack(fill="x")

        ttk.Button(
            row,
            text="Search",
            style="Panel.TButton",
            command=self.open_search_popup
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            row,
            text="Filter",
            style="Panel.TButton",
            command=self.open_filter_popup
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            row,
            text="Recently Added",
            style="Panel.TButton",
            command=self.open_recent_popup
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            row,
            text="Duplicate Finder",
            style="Panel.TButton",
            command=self.open_duplicate_popup
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            row,
            text="Apply All",
            style="Accent.TButton",
            command=self.apply_filters_and_sort
        ).pack(side="right", padx=(8, 0))

        ttk.Button(
            row,
            text="Reset",
            style="Modern.TButton",
            command=self.reset_filters
        ).pack(side="right")

        sort_box = tk.Frame(
            content,
            bg="#0f172a",
            highlightthickness=1,
            highlightbackground="#243041",
            bd=0
        )
        sort_box.pack(fill="x", pady=(8, 0))

        inner = tk.Frame(sort_box, bg="#0f172a")
        inner.pack(fill="x", padx=12, pady=12)

        tk.Label(inner, text="Sort By", bg="#0f172a", fg="#cbd5e1", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            inner,
            textvariable=self.sort_var,
            values=["name", "size", "date"],
            state="readonly",
            style="Modern.TCombobox",
            width=16
        ).grid(row=1, column=0, padx=(0, 8), pady=(4, 0), sticky="ew")

        tk.Label(inner, text="Order", bg="#0f172a", fg="#cbd5e1", font=("Helvetica", 10, "bold")).grid(row=0, column=1, sticky="w")
        ttk.Combobox(
            inner,
            textvariable=self.order_var,
            values=["asc", "desc"],
            state="readonly",
            style="Modern.TCombobox",
            width=12
        ).grid(row=1, column=1, padx=(0, 8), pady=(4, 0), sticky="ew")

        tk.Label(inner, text="Results / Page", bg="#0f172a", fg="#cbd5e1", font=("Helvetica", 10, "bold")).grid(row=0, column=2, sticky="w")
        ttk.Combobox(
            inner,
            textvariable=self.page_size_var,
            values=["10", "15", "20", "25", "50", "100"],
            state="readonly",
            style="Modern.TCombobox",
            width=14
        ).grid(row=1, column=2, padx=(0, 8), pady=(4, 0), sticky="ew")

        ttk.Button(
            inner,
            text="Previous Page",
            style="Modern.TButton",
            command=self.previous_page
        ).grid(row=1, column=3, padx=4, sticky="ew")

        ttk.Button(
            inner,
            text="Next Page",
            style="Modern.TButton",
            command=self.next_page
        ).grid(row=1, column=4, padx=4, sticky="ew")

        for i in range(5):
            inner.columnconfigure(i, weight=1)

    def create_main_content(self, parent):
        container = ttk.Frame(parent, style="App.TFrame")
        container.pack(fill="both", expand=True)

        left_card = self.make_card(container)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        left_inner = ttk.Frame(left_card, style="Card.TFrame")
        left_inner.pack(fill="both", expand=True)

        ttk.Label(
            left_inner,
            text="Indexed Files",
            style="Section.TLabel"
        ).pack(anchor="w", pady=(0, 8))

        columns = ("name", "extension", "size", "modified_date", "path")
        self.tree = ttk.Treeview(left_inner, columns=columns, show="headings")

        self.tree.heading("name", text="Name")
        self.tree.heading("extension", text="Extension")
        self.tree.heading("size", text="Size (bytes)")
        self.tree.heading("modified_date", text="Modified Date")
        self.tree.heading("path", text="Path")

        self.tree.column("name", width=220)
        self.tree.column("extension", width=95, anchor="center")
        self.tree.column("size", width=120, anchor="e")
        self.tree.column("modified_date", width=165, anchor="center")
        self.tree.column("path", width=560)

        y_scroll = ttk.Scrollbar(left_inner, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(left_inner, orient="horizontal", command=self.tree.xview)

        self.tree.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        self.tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")

        self.tree.bind("<<TreeviewSelect>>", self.show_selected_details)
        self.tree.bind("<Double-1>", self.open_selected_item)

        right_card = self.make_card(container, fixed_width=400)
        right_card.pack(side="right", fill="y", padx=(8, 0))
        right_card.pack_propagate(False)

        right_inner = ttk.Frame(right_card, style="Card.TFrame")
        right_inner.pack(fill="both", expand=True)

        ttk.Label(
            right_inner,
            text="Selected File Details",
            style="Section.TLabel"
        ).pack(anchor="w", pady=(0, 10))

        details_holder = tk.Frame(right_inner, bg="#111827")
        details_holder.pack(fill="both", expand=True)

        self.create_detail_block(details_holder, "Name", self.selected_name_var)
        self.create_detail_block(details_holder, "Extension", self.selected_extension_var)
        self.create_detail_block(details_holder, "Size", self.selected_size_var)
        self.create_detail_block(details_holder, "Modified Date", self.selected_date_var)
        self.create_detail_block(details_holder, "Path", self.selected_path_var, wrap=340)

        button_area = tk.Frame(right_inner, bg="#111827")
        button_area.pack(fill="x", pady=(10, 0))

        ttk.Button(
            button_area,
            text="Open Selected File",
            style="Accent.TButton",
            command=self.open_selected_item
        ).pack(fill="x", pady=(0, 8))

        ttk.Button(
            button_area,
            text="Copy File Path",
            style="Modern.TButton",
            command=self.copy_selected_path
        ).pack(fill="x")

    def create_detail_block(self, parent, title, variable, wrap=0):
        block = tk.Frame(
            parent,
            bg="#0f172a",
            highlightthickness=1,
            highlightbackground="#1f2937",
            bd=0
        )
        block.pack(fill="x", pady=(0, 8))

        inner = tk.Frame(block, bg="#0f172a")
        inner.pack(fill="x", padx=10, pady=9)

        tk.Label(
            inner,
            text=title,
            bg="#0f172a",
            fg="#94a3b8",
            font=("Helvetica", 9, "bold")
        ).pack(anchor="w")

        tk.Label(
            inner,
            textvariable=variable,
            bg="#0f172a",
            fg="#f8fafc",
            font=("Helvetica", 10),
            justify="left",
            anchor="w",
            wraplength=wrap
        ).pack(anchor="w", fill="x", pady=(5, 0))

    def make_card(self, parent, fixed_width=None):
        outer = tk.Frame(
            parent,
            bg="#111827",
            highlightthickness=1,
            highlightbackground="#1f2937",
            bd=0
        )
        if fixed_width is not None:
            outer.configure(width=fixed_width)

        inner = ttk.Frame(outer, style="Card.TFrame", padding=12)
        inner.pack(fill="both", expand=True)
        return outer

    def create_popup(self, title, width, height):
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.geometry(f"{width}x{height}")
        popup.resizable(False, False)
        popup.configure(bg="#111827")
        popup.transient(self)
        popup.grab_set()
        return popup

    def open_search_popup(self):
        if self.search_popup and self.search_popup.winfo_exists():
            self.search_popup.lift()
            return

        self.search_popup = self.create_popup("Search Options", 520, 220)

        wrapper = tk.Frame(self.search_popup, bg="#111827")
        wrapper.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            wrapper,
            text="Search Options",
            bg="#111827",
            fg="#f8fafc",
            font=("Helvetica", 12, "bold")
        ).pack(anchor="w", pady=(0, 12))

        grid = tk.Frame(wrapper, bg="#111827")
        grid.pack(fill="x")

        tk.Label(grid, text="File Name", bg="#111827", fg="#cbd5e1", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.search_name_var, style="Modern.TEntry", width=26).grid(row=1, column=0, padx=(0, 10), pady=(4, 10), sticky="ew")

        tk.Label(grid, text="Extension", bg="#111827", fg="#cbd5e1", font=("Helvetica", 10, "bold")).grid(row=0, column=1, sticky="w")
        ttk.Entry(grid, textvariable=self.extension_var, style="Modern.TEntry", width=20).grid(row=1, column=1, pady=(4, 10), sticky="ew")

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        btns = tk.Frame(wrapper, bg="#111827")
        btns.pack(fill="x", pady=(8, 0))

        ttk.Button(btns, text="Close", style="Modern.TButton", command=self.search_popup.destroy).pack(side="right")
        ttk.Button(
            btns,
            text="Apply",
            style="Accent.TButton",
            command=lambda: [self.apply_filters_and_sort(), self.search_popup.destroy()]
        ).pack(side="right", padx=(0, 8))

    def open_filter_popup(self):
        if self.filter_popup and self.filter_popup.winfo_exists():
            self.filter_popup.lift()
            return

        self.filter_popup = self.create_popup("Filter Options", 760, 260)

        wrapper = tk.Frame(self.filter_popup, bg="#111827")
        wrapper.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            wrapper,
            text="Filter Options",
            bg="#111827",
            fg="#f8fafc",
            font=("Helvetica", 12, "bold")
        ).pack(anchor="w", pady=(0, 12))

        grid = tk.Frame(wrapper, bg="#111827")
        grid.pack(fill="x")

        fields = [
            ("Min Size (bytes)", self.min_size_var, 0),
            ("Max Size (bytes)", self.max_size_var, 1),
            ("Start Date (YYYY-MM-DD)", self.start_date_var, 2),
            ("End Date (YYYY-MM-DD)", self.end_date_var, 3),
        ]

        for label_text, variable, column in fields:
            tk.Label(
                grid,
                text=label_text,
                bg="#111827",
                fg="#cbd5e1",
                font=("Helvetica", 10, "bold")
            ).grid(row=0, column=column, sticky="w")

            ttk.Entry(
                grid,
                textvariable=variable,
                style="Modern.TEntry",
                width=18
            ).grid(row=1, column=column, padx=(0, 10), pady=(4, 10), sticky="ew")

        for i in range(4):
            grid.columnconfigure(i, weight=1)

        btns = tk.Frame(wrapper, bg="#111827")
        btns.pack(fill="x", pady=(8, 0))

        ttk.Button(btns, text="Close", style="Modern.TButton", command=self.filter_popup.destroy).pack(side="right")
        ttk.Button(
            btns,
            text="Apply",
            style="Accent.TButton",
            command=lambda: [self.apply_filters_and_sort(), self.filter_popup.destroy()]
        ).pack(side="right", padx=(0, 8))

    def open_recent_popup(self):
        if self.recent_popup and self.recent_popup.winfo_exists():
            self.recent_popup.lift()
            return

        self.recent_popup = self.create_popup("Recently Added", 420, 210)

        wrapper = tk.Frame(self.recent_popup, bg="#111827")
        wrapper.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            wrapper,
            text="Recently Added Files",
            bg="#111827",
            fg="#f8fafc",
            font=("Helvetica", 12, "bold")
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            wrapper,
            text="Show files modified in the last N days",
            bg="#111827",
            fg="#94a3b8",
            font=("Helvetica", 10)
        ).pack(anchor="w", pady=(0, 10))

        grid = tk.Frame(wrapper, bg="#111827")
        grid.pack(fill="x")

        tk.Label(grid, text="Days", bg="#111827", fg="#cbd5e1", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.recent_days_var, style="Modern.TEntry", width=12).grid(row=1, column=0, pady=(4, 10), sticky="w")

        btns = tk.Frame(wrapper, bg="#111827")
        btns.pack(fill="x", pady=(8, 0))

        ttk.Button(btns, text="Close", style="Modern.TButton", command=self.recent_popup.destroy).pack(side="right")
        ttk.Button(
            btns,
            text="Show Results",
            style="Accent.TButton",
            command=lambda: [self.show_recent_files(), self.recent_popup.destroy()]
        ).pack(side="right", padx=(0, 8))

    def open_duplicate_popup(self):
        if self.duplicate_popup and self.duplicate_popup.winfo_exists():
            self.duplicate_popup.lift()
            return

        self.duplicate_popup = self.create_popup("Duplicate Finder", 500, 220)

        wrapper = tk.Frame(self.duplicate_popup, bg="#111827")
        wrapper.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            wrapper,
            text="Duplicate Finder",
            bg="#111827",
            fg="#f8fafc",
            font=("Helvetica", 12, "bold")
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            wrapper,
            text="This checks file contents and groups files with identical hashes.",
            bg="#111827",
            fg="#94a3b8",
            font=("Helvetica", 10),
            justify="left"
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            wrapper,
            text="For large folders, this may take some time.",
            bg="#111827",
            fg="#94a3b8",
            font=("Helvetica", 10)
        ).pack(anchor="w")

        btns = tk.Frame(wrapper, bg="#111827")
        btns.pack(fill="x", pady=(18, 0))

        ttk.Button(btns, text="Close", style="Modern.TButton", command=self.duplicate_popup.destroy).pack(side="right")
        ttk.Button(
            btns,
            text="Find Duplicates",
            style="Accent.TButton",
            command=lambda: [self.find_duplicates(), self.duplicate_popup.destroy()]
        ).pack(side="right", padx=(0, 8))

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def handle_drop(self, event):
        dropped_path = event.data.strip()

        if dropped_path.startswith("{") and dropped_path.endswith("}"):
            dropped_path = dropped_path[1:-1]

        if os.path.isdir(dropped_path):
            self.folder_var.set(dropped_path)
            self.scan_folder()
        else:
            self.show_toast("Please drop a valid folder.", "error")

    def scan_folder(self):
        folder_path = self.folder_var.get().strip()

        if not folder_path or not os.path.isdir(folder_path):
            self.show_toast("Please select a valid folder.", "error")
            return

        try:
            scanner = FileScanner(folder_path)
            self.records = scanner.scan()
            self.current_results = self.records[:]
            self.current_page = 1

            self.refresh_current_page()
            self.update_summary(self.current_results)
            self.clear_selected_details()

            errors = scanner.get_errors()

            if errors:
                self.show_toast(
                    f"Scan completed with {len(errors)} issue(s). Indexed {len(self.records)} files.",
                    "warning"
                )
            else:
                self.show_toast(
                    f"Scan completed successfully. Indexed {len(self.records)} files.",
                    "success"
                )

        except Exception as error:
            self.show_toast(f"Scan failed: {error}", "error")

    def show_recent_files(self):
        if not self.records:
            self.show_toast("No records available. Scan or load data first.", "warning")
            return

        try:
            days = int(self.recent_days_var.get().strip())
            cutoff = datetime.now() - timedelta(days=days)

            results = []
            for record in self.records:
                record_dt = datetime.strptime(record.modified_date, "%Y-%m-%d %H:%M:%S")
                if record_dt >= cutoff:
                    results.append(record)

            sorter = FileSorter(results)
            results = sorter.sort_by_date(reverse=True)

            self.current_results = results
            self.current_page = 1
            self.refresh_current_page()
            self.update_summary(results)
            self.clear_selected_details()

            self.show_toast(f"Showing {len(results)} recently added files.", "success")
        except ValueError:
            self.show_toast("Days must be a valid number.", "error")

    def compute_file_hash(self, file_path, chunk_size=8192):
        hasher = hashlib.md5()
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()

    def find_duplicates(self):
        if not self.records:
            self.show_toast("No records available. Scan or load data first.", "warning")
            return

        try:
            size_groups = {}
            for record in self.records:
                size_groups.setdefault(record.size, []).append(record)

            candidate_groups = [group for group in size_groups.values() if len(group) > 1]

            hash_groups = {}
            for group in candidate_groups:
                for record in group:
                    if not os.path.exists(record.path):
                        continue
                    try:
                        file_hash = self.compute_file_hash(record.path)
                        hash_groups.setdefault(file_hash, []).append(record)
                    except Exception:
                        continue

            duplicates = []
            for group in hash_groups.values():
                if len(group) > 1:
                    duplicates.extend(group)

            self.current_results = duplicates
            self.current_page = 1
            self.refresh_current_page()
            self.update_summary(duplicates)
            self.clear_selected_details()

            self.show_toast(f"Found {len(duplicates)} duplicate files.", "success")
        except Exception as error:
            self.show_toast(f"Duplicate finder failed: {error}", "error")

    def apply_filters_and_sort(self):
        if not self.records:
            self.show_toast("No records available. Scan or load data first.", "warning")
            return

        try:
            results = self.records[:]

            name_keyword = self.search_name_var.get().strip()
            extension = self.extension_var.get().strip()

            if name_keyword or extension:
                search_engine = SearchEngine(results)
                results = search_engine.search(
                    name_keyword=name_keyword,
                    extension=extension
                )

            file_filter = FileFilter(results)
            results = file_filter.filter(
                min_size=self.parse_int(self.min_size_var.get().strip()),
                max_size=self.parse_int(self.max_size_var.get().strip()),
                start_date=self.start_date_var.get().strip() or None,
                end_date=self.end_date_var.get().strip() or None
            )

            sorter = FileSorter(results)
            reverse = self.order_var.get() == "desc"
            sort_by = self.sort_var.get().strip().lower()

            if sort_by == "name":
                results = sorter.sort_by_name(reverse=reverse)
            elif sort_by == "size":
                results = sorter.sort_by_size(reverse=reverse)
            elif sort_by == "date":
                results = sorter.sort_by_date(reverse=reverse)

            self.current_results = results
            self.current_page = 1

            self.refresh_current_page()
            self.update_summary(results)
            self.clear_selected_details()

            self.show_toast(
                f"Filters applied successfully. {len(results)} results found.",
                "success"
            )

        except ValueError:
            self.show_toast(
                "Invalid input. Size must be numeric and date must be YYYY-MM-DD.",
                "error"
            )
        except Exception as error:
            self.show_toast(f"Could not apply filters: {error}", "error")

    def reset_filters(self):
        self.search_name_var.set("")
        self.extension_var.set("")
        self.min_size_var.set("")
        self.max_size_var.set("")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.sort_var.set("name")
        self.order_var.set("asc")
        self.page_size_var.set("15")
        self.recent_days_var.set("7")

        self.current_results = self.records[:]
        self.current_page = 1

        self.refresh_current_page()
        self.update_summary(self.current_results)
        self.clear_selected_details()

        self.show_toast("Filters reset.", "info")

    def refresh_current_page(self):
        page_size = self.get_page_size()
        paginator = Paginator(self.current_results, page_size)
        total_pages = paginator.get_total_pages()

        if total_pages == 0:
            self.refresh_table([])
            self.page_info_var.set("Page 0 / 0")
            self.visible_results_var.set("0")
            return

        if self.current_page > total_pages:
            self.current_page = total_pages

        page_records = paginator.get_page(self.current_page)
        self.refresh_table(page_records)

        self.page_info_var.set(f"Page {self.current_page} / {total_pages}")
        self.visible_results_var.set(str(len(self.current_results)))

    def refresh_table(self, records):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for record in records:
            self.tree.insert(
                "",
                "end",
                values=(
                    record.name,
                    record.display_extension(),
                    record.formatted_size(),
                    record.modified_date,
                    record.path
                )
            )

    def update_summary(self, visible_records):
        self.total_files_var.set(str(len(self.records)))
        self.visible_results_var.set(str(len(visible_records)))
        total_size = sum(record.size for record in visible_records)
        self.total_size_var.set(self.format_size(total_size))

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_current_page()
            self.clear_selected_details()
            self.show_toast(f"Moved to page {self.current_page}.", "info")
        else:
            self.show_toast("You are already on the first page.", "warning")

    def next_page(self):
        page_size = self.get_page_size()
        paginator = Paginator(self.current_results, page_size)
        total_pages = paginator.get_total_pages()

        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_current_page()
            self.clear_selected_details()
            self.show_toast(f"Moved to page {self.current_page}.", "info")
        else:
            self.show_toast("You are already on the last page.", "warning")

    def show_selected_details(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")

        self.selected_name_var.set(values[0])
        self.selected_extension_var.set(values[1])
        self.selected_size_var.set(values[2])
        self.selected_date_var.set(values[3])
        self.selected_path_var.set(values[4])

    def clear_selected_details(self):
        self.selected_name_var.set("-")
        self.selected_extension_var.set("-")
        self.selected_size_var.set("-")
        self.selected_date_var.set("-")
        self.selected_path_var.set("-")

    def open_selected_item(self, _event=None):
        path = self.selected_path_var.get()

        if not path or path == "-":
            self.show_toast("Select a file first.", "warning")
            return

        try:
            if os.path.exists(path):
                os.system(f'open "{path}"')
                self.show_toast("Opened selected file.", "success")
            else:
                self.show_toast("Selected file no longer exists.", "error")
        except Exception as error:
            self.show_toast(f"Could not open file: {error}", "error")

    def copy_selected_path(self):
        path = self.selected_path_var.get()

        if not path or path == "-":
            self.show_toast("Select a file first.", "warning")
            return

        self.clipboard_clear()
        self.clipboard_append(path)
        self.update()
        self.show_toast("Path copied to clipboard.", "success")

    def save_json(self):
        if not self.records:
            self.show_toast("No records to save.", "warning")
            return

        try:
            self.storage.save_to_json(self.records)
            self.show_toast("Index saved to JSON successfully.", "success")
        except Exception as error:
            self.show_toast(f"Could not save JSON: {error}", "error")

    def save_sqlite(self):
        if not self.records:
            self.show_toast("No records to save.", "warning")
            return

        try:
            self.storage.save_to_sqlite(self.records)
            self.show_toast("Index saved to SQLite successfully.", "success")
        except Exception as error:
            self.show_toast(f"Could not save SQLite: {error}", "error")

    def load_json(self):
        try:
            self.records = self.storage.load_from_json()
            self.current_results = self.records[:]
            self.current_page = 1

            self.refresh_current_page()
            self.update_summary(self.current_results)
            self.clear_selected_details()

            self.show_toast(f"Loaded {len(self.records)} records from JSON.", "success")
        except Exception as error:
            self.show_toast(f"Could not load JSON: {error}", "error")

    def load_sqlite(self):
        try:
            self.records = self.storage.load_from_sqlite()
            self.current_results = self.records[:]
            self.current_page = 1

            self.refresh_current_page()
            self.update_summary(self.current_results)
            self.clear_selected_details()

            self.show_toast(f"Loaded {len(self.records)} records from SQLite.", "success")
        except Exception as error:
            self.show_toast(f"Could not load SQLite: {error}", "error")

    def show_toast(self, message, kind="info"):
        colors = {
            "success": ("#052e2b", "#d1fae5", "#10b981"),
            "error": ("#3b0d0d", "#fee2e2", "#ef4444"),
            "warning": ("#3b2a08", "#fef3c7", "#f59e0b"),
            "info": ("#102a43", "#dbeafe", "#3b82f6")
        }

        bg, fg, accent = colors.get(kind, colors["info"])

        if self.toast_frame is not None:
            self.toast_frame.destroy()
            self.toast_frame = None

        if self.toast_after_id is not None:
            self.after_cancel(self.toast_after_id)
            self.toast_after_id = None

        self.toast_frame = tk.Frame(
            self,
            bg=bg,
            highlightthickness=1,
            highlightbackground=accent,
            bd=0
        )
        self.toast_frame.place(relx=1.0, y=18, x=-18, anchor="ne")

        accent_bar = tk.Frame(self.toast_frame, bg=accent, width=6)
        accent_bar.pack(side="left", fill="y")

        body = tk.Frame(self.toast_frame, bg=bg)
        body.pack(side="left", fill="both", expand=True, padx=12, pady=9)

        tk.Label(
            body,
            text=message,
            bg=bg,
            fg=fg,
            font=("Helvetica", 10, "bold"),
            justify="left"
        ).pack(anchor="w")

        close_button = tk.Label(
            self.toast_frame,
            text="✕",
            bg=bg,
            fg=fg,
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            padx=10
        )
        close_button.pack(side="right")
        close_button.bind("<Button-1>", lambda _e: self.dismiss_toast())

        self.toast_after_id = self.after(3200, self.dismiss_toast)

    def dismiss_toast(self):
        if self.toast_frame is not None:
            self.toast_frame.destroy()
            self.toast_frame = None

        if self.toast_after_id is not None:
            try:
                self.after_cancel(self.toast_after_id)
            except Exception:
                pass
            self.toast_after_id = None

    def get_page_size(self):
        value = self.page_size_var.get().strip()
        return int(value) if value.isdigit() and int(value) > 0 else 15

    @staticmethod
    def parse_int(value):
        if not value:
            return None
        return int(value)

    @staticmethod
    def format_size(size_in_bytes):
        units = ["bytes", "KB", "MB", "GB", "TB"]
        size = float(size_in_bytes)
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"

        return f"{size:.2f} {units[unit_index]}"


if __name__ == "__main__":
    app = FileSearchApp()
    app.mainloop()