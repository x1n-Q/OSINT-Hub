"""
Main GUI Application
Modern, user-friendly interface for OSINT Hub.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import customtkinter as ctk
import threading
import os
import webbrowser
from pathlib import Path
from datetime import datetime

from osinthub.tools.registry import ToolCategory
from osinthub.core.tool_manager import ToolManager
from osinthub.core.results_manager import ResultsManager

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Theme colors
ACCENT_COLOR = "#3b82f6"  # Professional blue
SUCCESS_COLOR = "#10b981" # Emerald green
ERROR_COLOR = "#ef4444"   # Red
BG_DARK = "#0f172a"       # Slate 900
BG_CARD = "#1e293b"       # Slate 800
STATUS_COLORS = {
    "READY": SUCCESS_COLOR,
    "AVAILABLE": ACCENT_COLOR,
    "SETUP REQUIRED": "#f97316",
    "MANUAL": "#f59e0b",
    "DOCS ONLY": "#0ea5e9",
    "UNSUPPORTED": ERROR_COLOR,
}

class ToolCard(ctk.CTkFrame):
    """A card widget displaying a tool with modern styling."""

    def __init__(self, master, tool, tool_manager, on_click=None, **kwargs):
        super().__init__(master, **kwargs)
        self.tool = tool
        self.tool_manager = tool_manager
        self.on_click = on_click

        self.configure(
            fg_color=BG_CARD,
            border_color="#334155",
            border_width=1,
            corner_radius=12,
            height=140
        )
        self.grid_propagate(False)

        # Icon with background
        self.icon_bg = ctk.CTkFrame(
            self,
            width=60,
            height=60,
            corner_radius=10,
            fg_color="#334155"
        )
        self.icon_bg.grid(row=0, column=0, rowspan=2, padx=15, pady=15)
        self.icon_bg.grid_propagate(False)

        self.icon_label = ctk.CTkLabel(
            self.icon_bg,
            text=tool.icon or "🛠️",
            font=ctk.CTkFont(family="Segoe UI Emoji" if os.name == "nt" else None, size=32)
        )
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Name and description
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)

        self.name_label = ctk.CTkLabel(
            info_frame,
            text=tool.name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        self.name_label.pack(anchor="w")

        self.desc_label = ctk.CTkLabel(
            info_frame,
            text=tool.description,
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8",
            wraplength=220,
            justify="left"
        )
        self.desc_label.pack(anchor="w", pady=(5, 0))

        # Status badge
        status_text, _ = self.tool_manager.get_tool_availability(tool)
        status_color = STATUS_COLORS.get(status_text, "#64748b")

        self.status_badge = ctk.CTkFrame(
            self,
            fg_color=status_color,
            corner_radius=4,
            height=20
        )
        self.status_badge.grid(row=1, column=1, sticky="sw", padx=(0, 15), pady=(0, 15))

        self.status_label = ctk.CTkLabel(
            self.status_badge,
            text=status_text,
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color="white",
            padx=6
        )
        self.status_label.pack()

        # Hover and click effect
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", lambda e=None: self._on_click())
        
        # Recursive binding for all children
        self._bind_click_recursive(self)

    def _bind_click_recursive(self, widget):
        """Recursively bind click event to all children."""
        if widget != self:
            widget.bind("<Button-1>", lambda e=None: self._on_click())
        
        for child in widget.winfo_children():
            self._bind_click_recursive(child)

    def _on_enter(self, event):
        self.configure(border_color=ACCENT_COLOR, fg_color="#243347")

    def _on_leave(self, event):
        self.configure(border_color="#334155", fg_color=BG_CARD)

    def _on_click(self):
        if self.on_click:
            self.on_click(self.tool)

    def update_status(self):
        """Update the installed status display."""
        status_text, _ = self.tool_manager.get_tool_availability(self.tool)
        status_color = STATUS_COLORS.get(status_text, "#64748b")
        self.status_badge.configure(fg_color=status_color)
        self.status_label.configure(text=status_text)

class ToolDetailView(ctk.CTkFrame):
    """Detailed view of a tool with installation/run controls."""

    def __init__(self, master, tool, tool_manager, results_manager, on_back, **kwargs):
        super().__init__(master, **kwargs)
        self.tool = tool
        self.tool_manager = tool_manager
        self.results_manager = results_manager
        self.on_back = on_back
        self.configure(fg_color="transparent")
        self.tool.installed = self.tool_manager.check_tool_installed(self.tool)

        self._build_ui()

    def _apply_install_state(self):
        """Sync buttons with actual tool availability."""
        availability, detail = self.tool_manager.get_tool_availability(self.tool)
        installed = availability == "READY"
        self.tool.installed = installed
        self.run_btn.configure(state="normal" if installed else "disabled")

        if availability in {"READY", "AVAILABLE"}:
            self.install_btn.configure(
                state="normal",
                text="REINSTALL" if installed else "INSTALL",
                fg_color="#334155" if installed else SUCCESS_COLOR,
                hover_color="#475569" if installed else "#059669",
            )
        else:
            self.install_btn.configure(
                state="disabled",
                text=availability,
                fg_color="#475569",
                hover_color="#475569",
            )

        self.availability_badge.configure(fg_color=STATUS_COLORS.get(availability, "#64748b"))
        self.availability_label.configure(text=availability)
        self.availability_detail.configure(text=detail)

    def _open_url(self, url: str):
        """Open upstream docs in the default browser."""
        if url.startswith("http"):
            webbrowser.open_new_tab(url)

    def _build_ui(self):
        """Build the detail view UI."""
        # Header
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=15)
        header.pack(fill="x", padx=10, pady=10)

        header_top = ctk.CTkFrame(header, fg_color="transparent")
        header_top.pack(fill="x", padx=18, pady=(18, 12))

        back_btn = ctk.CTkButton(
            header_top,
            text="← BACK",
            width=80,
            height=32,
            fg_color="#334155",
            hover_color="#475569",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_back
        )
        back_btn.pack(side="left", padx=(0, 16), pady=(6, 0), anchor="n")

        icon_bg = ctk.CTkFrame(header_top, width=60, height=60, corner_radius=10, fg_color="#1e293b")
        icon_bg.pack(side="left", padx=(0, 16), pady=(0, 4), anchor="n")
        icon_bg.pack_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_bg,
            text=self.tool.icon or "🛠️",
            font=ctk.CTkFont(family="Segoe UI Emoji" if os.name == "nt" else None, size=32)
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        info_frame = ctk.CTkFrame(header_top, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        title_label = ctk.CTkLabel(
            info_frame,
            text=self.tool.name.upper(),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title_label.pack(anchor="w")

        category_label = ctk.CTkLabel(
            info_frame,
            text=self.tool.category.value,
            font=ctk.CTkFont(size=13),
            text_color=ACCENT_COLOR
        )
        category_label.pack(anchor="w")

        availability, detail = self.tool_manager.get_tool_availability(self.tool)
        self.availability_panel = ctk.CTkFrame(
            header,
            fg_color="#172235",
            border_color="#25324a",
            border_width=1,
            corner_radius=10,
        )
        self.availability_panel.pack(fill="x", padx=18, pady=(0, 18))

        availability_frame = ctk.CTkFrame(self.availability_panel, fg_color="transparent")
        availability_frame.pack(anchor="w", fill="x", padx=16, pady=14)

        self.availability_badge = ctk.CTkFrame(
            availability_frame,
            fg_color=STATUS_COLORS.get(availability, "#64748b"),
            corner_radius=4,
            height=22
        )
        self.availability_badge.pack(anchor="w")

        self.availability_label = ctk.CTkLabel(
            self.availability_badge,
            text=availability,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white",
            padx=8
        )
        self.availability_label.pack()

        self.availability_detail = ctk.CTkLabel(
            availability_frame,
            text=detail,
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8",
            wraplength=820,
            justify="left"
        )
        self.availability_detail.pack(anchor="w", pady=(6, 0))

        # Action Buttons
        actions_frame = ctk.CTkFrame(header_top, fg_color="transparent")
        actions_frame.pack(side="right", pady=(4, 0), anchor="n")

        self.run_btn = ctk.CTkButton(
            actions_frame,
            text="RUN TOOL",
            width=140,
            height=40,
            fg_color=ACCENT_COLOR,
            hover_color="#2563eb",
            font=ctk.CTkFont(size=13, weight="bold"),
            state="normal" if self.tool.installed else "disabled",
            command=self._run_tool
        )
        self.run_btn.pack(side="right", padx=5)

        self.install_btn = ctk.CTkButton(
            actions_frame,
            text="INSTALL" if not self.tool.installed else "REINSTALL",
            width=120,
            height=40,
            fg_color="#334155" if self.tool.installed else SUCCESS_COLOR,
            hover_color="#475569" if self.tool.installed else "#059669",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._install_tool
        )
        self.install_btn.pack(side="right", padx=5)
        self._apply_install_state()

        # Content area
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Description Card
        desc_card = ctk.CTkFrame(content, fg_color=BG_CARD, corner_radius=12)
        desc_card.pack(fill="x", pady=10)

        desc_title = ctk.CTkLabel(
            desc_card,
            text="DESCRIPTION",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#94a3b8"
        )
        desc_title.pack(anchor="w", padx=20, pady=(15, 5))

        desc_text = ctk.CTkLabel(
            desc_card,
            text=self.tool.long_description or self.tool.description,
            font=ctk.CTkFont(size=14),
            text_color="white",
            wraplength=800,
            justify="left"
        )
        desc_text.pack(anchor="w", padx=20, pady=(0, 20))

        # Parameters Card
        if self.tool.parameters:
            param_card = ctk.CTkFrame(content, fg_color=BG_CARD, corner_radius=12)
            param_card.pack(fill="x", pady=10)

            param_title = ctk.CTkLabel(
                param_card,
                text="PARAMETERS",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#94a3b8"
            )
            param_title.pack(anchor="w", padx=20, pady=(15, 10))

            self.param_entries = {}
            # Use a container with grid for perfect alignment
            param_container = ctk.CTkFrame(param_card, fg_color="transparent")
            param_container.pack(fill="x", padx=20, pady=(0, 20))
            param_container.grid_columnconfigure(0, weight=3) # Name/Desc
            param_container.grid_columnconfigure(1, weight=1) # Input

            for i, param in enumerate(self.tool.parameters):
                # Row frame for hover effect or spacing
                row_frame = ctk.CTkFrame(param_container, fg_color="transparent")
                row_frame.grid(row=i, column=0, columnspan=2, sticky="ew", pady=5)
                row_frame.grid_columnconfigure(0, weight=3)
                row_frame.grid_columnconfigure(1, weight=1)

                # Info on the left
                info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                info_frame.grid(row=0, column=0, sticky="nsw", pady=5)

                p_name = ctk.CTkLabel(
                    info_frame,
                    text=param.name.upper(),
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="white"
                )
                p_name.pack(anchor="w")

                p_desc = ctk.CTkLabel(
                    info_frame,
                    text=param.description,
                    font=ctk.CTkFont(size=12),
                    text_color="#64748b"
                )
                p_desc.pack(anchor="w")

                # Input on the right
                input_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                input_frame.grid(row=0, column=1, sticky="nse", pady=5)

                if param.type == "boolean":
                    var = tk.BooleanVar(value=param.default == "True" if param.default else False)
                    entry = ctk.CTkCheckBox(input_frame, text="", variable=var, fg_color=ACCENT_COLOR)
                    entry.pack()
                elif param.options:
                    var = tk.StringVar(value=param.default or param.options[0])
                    entry = ctk.CTkComboBox(
                        input_frame,
                        values=param.options,
                        variable=var,
                        width=250,
                        fg_color="#0f172a",
                        border_color="#334155"
                    )
                    entry.pack()
                else:
                    var = tk.StringVar(value=param.default or "")
                    entry = ctk.CTkEntry(
                        input_frame,
                        textvariable=var,
                        width=300,
                        placeholder_text=param.description,
                        fg_color="#0f172a",
                        border_color="#334155"
                    )
                    entry.pack()

                self.param_entries[param.name] = (entry, var)

        # Examples Card
        if self.tool.examples:
            ex_card = ctk.CTkFrame(content, fg_color=BG_CARD, corner_radius=12)
            ex_card.pack(fill="x", pady=10)

            ex_title = ctk.CTkLabel(
                ex_card,
                text="USAGE EXAMPLES",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#94a3b8"
            )
            ex_title.pack(anchor="w", padx=20, pady=(15, 10))

            for ex in self.tool.examples:
                ex_box = ctk.CTkTextbox(
                    ex_card,
                    height=45,
                    font=ctk.CTkFont(family="Courier", size=13),
                    fg_color="#0f172a",
                    border_color="#334155",
                    border_width=1,
                    text_color=SUCCESS_COLOR
                )
                ex_box.pack(fill="x", padx=20, pady=5)
                ex_box.insert("1.0", f"$ {ex}")
                ex_box.configure(state="disabled")

        # Footer Links
        links_frame = ctk.CTkFrame(content, fg_color="transparent")
        links_frame.pack(fill="x", pady=20)

        if self.tool.homepage:
            home_btn = ctk.CTkButton(
                links_frame,
                text="🌐 HOMEPAGE",
                width=150,
                fg_color="#1e293b",
                hover_color="#334155",
                command=lambda: self._open_url(self.tool.homepage)
            )
            home_btn.pack(side="left", padx=5)

        if self.tool.documentation:
            doc_btn = ctk.CTkButton(
                links_frame,
                text="📚 DOCUMENTATION",
                width=150,
                fg_color="#1e293b",
                hover_color="#334155",
                command=lambda: self._open_url(self.tool.documentation)
            )
            doc_btn.pack(side="left", padx=5)

    def _install_tool(self):
        """Install the tool."""
        self.install_btn.configure(state="disabled", text="INSTALLING...")

        def install_thread():
            success, message = self.tool_manager.install_tool(self.tool)

            # Update UI in main thread
            self.after(0, lambda: self._install_complete(success, message))

        threading.Thread(target=install_thread, daemon=True).start()

    def _install_complete(self, success: bool, message: str):
        """Handle installation completion."""
        self.install_btn.configure(state="normal")

        if success:
            self.tool_manager.refresh_tool_states()
            self._apply_install_state()
            messagebox.showinfo("Success", f"{self.tool.name} installed successfully!")
        else:
            self._apply_install_state()
            messagebox.showerror("Installation Failed", message)

    def _run_tool(self):
        """Run the tool with configured parameters."""
        if not self.tool_manager.check_tool_installed(self.tool):
            self._apply_install_state()
            messagebox.showwarning("Tool Not Available", f"{self.tool.name} is not currently installed.")
            return

        # Gather parameters
        params = {}
        missing = []
        if self.tool.parameters:
            for param in self.tool.parameters:
                if param.name in self.param_entries:
                    entry, var = self.param_entries[param.name]
                    value = var.get()
                    params[param.name] = value
                    if param.required and str(value).strip() == "":
                        missing.append(param.name)

        if missing:
            messagebox.showwarning("Missing Parameters", f"Please fill in: {', '.join(missing)}")
            return

        # Show output window
        self._show_output_window(params)

    def _show_output_window(self, params: dict):
        """Show tool output in a new window with modern styling."""
        output_window = ctk.CTkToplevel(self)
        output_window.title(f"Running {self.tool.name}")
        output_window.geometry("900x700")
        output_window.configure(fg_color=BG_DARK)

        # Header
        header = ctk.CTkFrame(output_window, height=60, fg_color=BG_CARD, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text=f"EXECUTING: {self.tool.name.upper()}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ACCENT_COLOR
        )
        title.pack(side="left", padx=20)

        # Output display
        output_frame = ctk.CTkFrame(output_window, fg_color="#0f172a", corner_radius=10)
        output_frame.pack(fill="both", expand=True, padx=20, pady=20)

        output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=("Courier", 12),
            bg="#0f172a",
            fg="#e2e8f0",
            insertbackground="white",
            borderwidth=0,
            highlightthickness=0
        )
        output_text.pack(fill="both", expand=True, padx=15, pady=15)

        output_text.insert("1.0", f"[*] Starting {self.tool.name}...\n")
        output_text.insert("end", f"[*] Target: {params}\n")
        output_text.insert("end", f"[*] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output_text.insert("end", f"{'-'*60}\n\n")
        output_text.see("end")

        # Buttons
        btn_frame = ctk.CTkFrame(output_window, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        stop_btn = ctk.CTkButton(
            btn_frame,
            text="STOP PROCESS",
            fg_color=ERROR_COLOR,
            hover_color="#dc2626",
            width=150,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: output_window.destroy()
        )
        stop_btn.pack(side="left", padx=5)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="SAVE LOG",
            fg_color="#334155",
            hover_color="#475569",
            width=150,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._save_output(output_text.get("1.0", "end"))
        )
        save_btn.pack(side="left", padx=5)

        # Run in thread with streaming callback
        def stream_callback(line):
            if output_window.winfo_exists():
                output_window.after(0, lambda: self._append_to_output(output_text, line))

        def run_thread():
            success, stdout, stderr = self.tool_manager.run_tool(self.tool, params, output_callback=stream_callback)
            
            if output_window.winfo_exists():
                output_window.after(0, lambda: self._update_output(output_text, success, stdout, stderr, params))

        threading.Thread(target=run_thread, daemon=True).start()

    def _append_to_output(self, text_widget, line: str):
        """Append a single line to the output display."""
        if text_widget.winfo_exists():
            text_widget.insert("end", line)
            text_widget.see("end")

    def _update_output(self, text_widget, success: bool, stdout: str, stderr: str, params: dict):
        """Update output window with final results summary."""
        if not text_widget.winfo_exists():
            return
            
        text_widget.insert("end", "\n" + "="*60 + "\n")

        if success:
            text_widget.insert("end", "✓ Scan completed successfully\n")
        else:
            text_widget.insert("end", "✗ Scan failed\n")
            if stderr:
                text_widget.insert("end", f"\nReason:\n{stderr}\n")

        text_widget.see("end")

        # Save result
        if success:
            parsed_data = {"stdout": stdout}
            try:
                result = self.results_manager.save_result(
                    self.tool,
                    str(params.get("target") or params.get("username") or params.get("domain") or params.get("number") or "unknown"),
                    stdout,
                    parsed_data
                )
                text_widget.insert("end", f"\nResult saved (ID: {result.result_id})")
            except Exception as exc:
                text_widget.insert("end", f"\nWarning: result could not be saved: {exc}")

    def _save_output(self, content: str):
        """Save output to file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Output saved to {filepath}")

class ResultsView(ctk.CTkFrame):
    """View and manage saved results with modern styling."""

    def __init__(self, master, results_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.results_manager = results_manager
        self.configure(fg_color="transparent")
        self._build_ui()

    def _build_ui(self):
        """Build results view UI."""
        # Header
        header = ctk.CTkFrame(self, height=80, fg_color=BG_CARD, corner_radius=12)
        header.pack(fill="x", padx=10, pady=10)
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="SCAN HISTORY",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        title.pack(side="left", padx=20, pady=10)

        # Buttons on right
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)

        export_btn = ctk.CTkButton(
            btn_frame,
            text="EXPORT",
            width=100,
            fg_color=ACCENT_COLOR,
            command=self._export_selected
        )
        export_btn.pack(side="left", padx=5)

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="DELETE",
            width=100,
            fg_color="#334155",
            hover_color=ERROR_COLOR,
            command=self._delete_selected
        )
        delete_btn.pack(side="left", padx=5)

        clear_btn = ctk.CTkButton(
            btn_frame,
            text="CLEAR ALL",
            width=100,
            fg_color="#334155",
            hover_color=ERROR_COLOR,
            command=self._clear_all
        )
        clear_btn.pack(side="left", padx=5)

        # Main horizontal paned window for list and detail
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_DARK, bd=0, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Left side: Results list
        list_frame = ctk.CTkFrame(paned, fg_color=BG_CARD, corner_radius=12)
        paned.add(list_frame, width=450)

        # Treeview styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                       background="#1e293b",
                       foreground="#e2e8f0",
                       fieldbackground="#1e293b",
                       rowheight=35,
                       borderwidth=0,
                       font=("Inter", 11))
        style.configure("Treeview.Heading",
                       background="#334155",
                       foreground="white",
                       relief="flat",
                       padding=5,
                       font=("Inter", 11, "bold"))
        style.map("Treeview", background=[('selected', ACCENT_COLOR)])

        self.tree = ttk.Treeview(
            list_frame,
            columns=("tool", "target", "timestamp", "id"),
            show="headings",
            selectmode="extended"
        )

        self.tree.heading("tool", text="TOOL")
        self.tree.heading("target", text="TARGET")
        self.tree.heading("timestamp", text="TIME")
        self.tree.heading("id", text="ID")

        self.tree.column("tool", width=120)
        self.tree.column("target", width=180)
        self.tree.column("timestamp", width=120)
        self.tree.column("id", width=0, stretch=False) # Hide ID column

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Right side: Detail view
        detail_frame = ctk.CTkFrame(paned, fg_color=BG_CARD, corner_radius=12)
        paned.add(detail_frame)

        detail_label = ctk.CTkLabel(
            detail_frame,
            text="RESULT CONTENT",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#94a3b8"
        )
        detail_label.pack(anchor="w", padx=15, pady=(15, 5))

        self.detail_text = scrolledtext.ScrolledText(
            detail_frame,
            wrap=tk.WORD,
            bg="#0f172a",
            fg="#e2e8f0",
            font=("Courier", 12),
            borderwidth=0,
            highlightthickness=0
        )
        self.detail_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self._refresh_results()

    def _refresh_results(self):
        """Refresh the results list."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        results = self.results_manager.get_results(limit=200)
        for result in results:
            self.tree.insert("", "end", values=(
                result.data.get("tool_name", result.tool_id),
                result.target,
                result.timestamp.strftime("%Y-%m-%d %H:%M"),
                result.result_id
            ))

    def _on_select(self, event):
        """Display selected result details."""
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        result_id = item["values"][3]

        result = self.results_manager.get_result(result_id)
        if result:
            self.detail_text.delete("1.0", "end")
            self.detail_text.insert("1.0", f"TOOL: {result.data.get('tool_name')}\n")
            self.detail_text.insert("end", f"TARGET: {result.target}\n")
            self.detail_text.insert("end", f"TIMESTAMP: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.detail_text.insert("end", f"ID: {result.result_id}\n\n")
            self.detail_text.insert("end", f"{'-'*60}\n\n")
            self.detail_text.insert("end", result.data.get("raw", ""))

    def _export_selected(self):
        """Export selected results."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select results to export.")
            return

        results = []
        for item_id in selected:
            item = self.tree.item(item_id)
            result_id = item["values"][3]
            result = self.results_manager.get_result(result_id)
            if result:
                results.append(result)

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON", "*.json"),
                ("CSV", "*.csv"),
                ("Text", "*.txt"),
                ("HTML", "*.html")
            ]
        )

        if filepath:
            ext = Path(filepath).suffix.lower().lstrip(".")
            if self.results_manager.export_results(results, filepath, ext):
                messagebox.showinfo("Exported", f"Results exported to {filepath}")
            else:
                messagebox.showerror("Error", "Failed to export results.")

    def _delete_selected(self):
        """Delete selected results."""
        selected = self.tree.selection()
        if not selected:
            return

        if messagebox.askyesno("Confirm", f"Delete {len(selected)} result(s)?"):
            for item_id in selected:
                item = self.tree.item(item_id)
                result_id = item["values"][3]
                self.results_manager.delete_result(result_id)
            self._refresh_results()

    def _clear_all(self):
        """Clear all results."""
        if messagebox.askyesno("Confirm", "Delete ALL results? This cannot be undone."):
            self.results_manager.clear_results()
            self._refresh_results()
            self.detail_text.delete("1.0", "end")

class OSINTHubApp(ctk.CTk):
    """Main application window with modern layout."""

    def __init__(self):
        super().__init__()

        self.title("OSINT Hub - All-in-One OSINT Framework")
        self.geometry("1280x800")
        self.configure(fg_color=BG_DARK)

        # Initialize managers
        self.tool_manager = ToolManager()
        self.tool_manager.refresh_tool_states(persist=False)
        self.results_manager = ResultsManager()
        self.registry = self.tool_manager.registry

        # Build UI
        self._build_ui()

        # Start auto-refresh for installation status
        self._refresh_status()

    def _build_ui(self):
        """Build the main interface."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=BG_CARD)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(15, 10), padx=20, fill="x")

        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🔍 OSINT HUB",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        logo_label.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            logo_frame,
            text="PROFESSIONAL RECONNAISSANCE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=ACCENT_COLOR
        )
        subtitle.pack(anchor="w")

        # Navigation
        nav_label = ctk.CTkLabel(
            self.sidebar,
            text="CATEGORIES",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#64748b"
        )
        nav_label.pack(anchor="w", padx=25, pady=(10, 5))

        self.nav_buttons = {}
        categories = [("All Tools", None)] + [(cat.value, cat) for cat in ToolCategory]

        for label, cat in categories:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label.upper(),
                height=32,
                anchor="w",
                fg_color="transparent",
                text_color="#94a3b8",
                hover_color="#334155",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda c=cat, l=label: self._show_category(c, l)
            )
            btn.pack(fill="x", padx=15, pady=1)
            self.nav_buttons[label] = btn

        # Results button at bottom of nav
        results_sep = ctk.CTkFrame(self.sidebar, height=1, fg_color="#334155")
        results_sep.pack(fill="x", padx=20, pady=10)

        self.results_btn = ctk.CTkButton(
            self.sidebar,
            text="📊 SCAN HISTORY",
            height=36,
            anchor="w",
            fg_color="transparent",
            text_color="#94a3b8",
            hover_color="#334155",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._show_results
        )
        self.results_btn.pack(fill="x", padx=15, pady=1)

        # Stats at the very bottom
        stats_frame = ctk.CTkFrame(self.sidebar, fg_color="#0f172a", corner_radius=10)
        stats_frame.pack(side="bottom", fill="x", padx=20, pady=10)

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8",
            justify="left",
            padx=15,
            pady=10
        )
        self.stats_label.pack(fill="x")

        # Main content area
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        # Initial view
        self._show_category(None, "All Tools")

    def _update_nav_selection(self, active_label):
        """Update sidebar button styles to show selection."""
        for label, btn in self.nav_buttons.items():
            if label == active_label:
                btn.configure(fg_color=ACCENT_COLOR, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="#94a3b8")

        if active_label == "Results":
            self.results_btn.configure(fg_color=ACCENT_COLOR, text_color="white")
        else:
            self.results_btn.configure(fg_color="transparent", text_color="#94a3b8")

    def _show_category(self, category, label):
        """Show tools for a specific category with improved layout."""
        self._update_nav_selection(label)
        self.tool_manager.refresh_tool_states(persist=False)

        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Get tools
        if category is None:
            tools = self.registry.get_all_tools()
            title = "ALL OSINT TOOLS"
        else:
            tools = self.registry.get_tools_by_category(category)
            title = f"{category.value.upper()} TOOLS"

        # Header Frame
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 30))

        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left")

        # Search box on right
        search_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="Search tools...",
            width=350,
            height=40,
            fg_color=BG_CARD,
            border_color="#334155",
            corner_radius=10
        )
        search_entry.pack(side="right")
        search_entry.bind("<KeyRelease>", lambda e: self._filter_tools(tools, search_entry.get()))

        # Scrollable container for tools
        scroll_container = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True)

        # Tools grid
        self.tools_container = ctk.CTkFrame(scroll_container, fg_color="transparent")
        self.tools_container.pack(fill="both", expand=True)

        self._display_tools(tools)

    def _display_tools(self, tools):
        """Display tool cards in a responsive-ish grid."""
        for i, tool in enumerate(tools):
            card = ToolCard(
                self.tools_container,
                tool,
                self.tool_manager,
                on_click=self._open_tool_detail
            )
            row = i // 2 # 2 columns for better readability at 1280 width
            col = i % 2
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

        # Configure grid columns
        for i in range(2):
            self.tools_container.grid_columnconfigure(i, weight=1, uniform="toolcol")

    def _filter_tools(self, tools, query):
        """Filter displayed tools by search query."""
        for widget in self.tools_container.winfo_children():
            widget.destroy()

        if not query:
            filtered = tools
        else:
            filtered = self.registry.search_tools(query)

        self._display_tools(filtered)

    def _open_tool_detail(self, tool):
        """Open detailed tool view."""
        tool.installed = self.tool_manager.check_tool_installed(tool)

        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Show detail view
        detail = ToolDetailView(
            self.content_frame,
            tool,
            self.tool_manager,
            self.results_manager,
            on_back=lambda: self._show_category(None, "All Tools")
        )
        detail.pack(fill="both", expand=True, padx=20, pady=20)

    def _show_results(self):
        """Show results management view."""
        self._update_nav_selection("Results")

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        results_view = ResultsView(self.content_frame, self.results_manager)
        results_view.pack(fill="both", expand=True, padx=20, pady=20)

    def _refresh_status(self):
        """Periodically refresh tool installation status and stats."""
        self.tool_manager.refresh_tool_states(persist=False)
        stats = self.results_manager.get_statistics()
        latest = stats['latest_scan']
        if latest:
            latest = datetime.fromisoformat(latest).strftime('%Y-%m-%d %H:%M')
        else:
            latest = "None"

        self.stats_label.configure(
            text=f"TOTAL RESULTS: {stats['total_results']}\n"
                 f"TOOLS UTILIZED: {stats['tools_used']}\n"
                 f"UNIQUE TARGETS: {stats['unique_targets']}\n"
                 f"LATEST SCAN: {latest}"
        )

        # Schedule next refresh
        self.after(5000, self._refresh_status)

def main():
    app = OSINTHubApp()
    app.mainloop()

if __name__ == "__main__":
    main()
