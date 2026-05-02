import asyncio
import json
import threading
import tkinter as tk
from tkinter import messagebox

import requests
import websockets

API_BASE = "http://localhost:8000"
WS_BASE = "ws://localhost:8000"


class ProxyClientApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Proxy Client")
        self.root.geometry("420x350")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        self.ws = None
        self.ws_thread = None
        self.connected = False
        self.user_id = None

        self._build_ui()

    def _build_ui(self):
        tk.Label(
            self.root,
            text="Proxy Client",
            font=("Inter", 18, "bold"),
            fg="#a8b8d8",
            bg="#1a1a2e",
        ).pack(pady=(20, 10))

        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.pack(pady=10, padx=30, fill="x")

        tk.Label(
            frame,
            text="Ключ активации:",
            font=("Inter", 11),
            fg="#e0e0f0",
            bg="#1a1a2e",
        ).pack(anchor="w")

        self.key_entry = tk.Entry(
            frame,
            font=("Consolas", 12),
            bg="#222244",
            fg="#e0e0f0",
            insertbackground="#a8b8d8",
            relief="flat",
            bd=8,
        )
        self.key_entry.pack(fill="x", pady=(5, 0))

        self.connect_btn = tk.Button(
            self.root,
            text="Подключиться",
            font=("Inter", 12, "bold"),
            bg="#a8b8d8",
            fg="#1a1a2e",
            activebackground="#8898b8",
            relief="flat",
            cursor="hand2",
            command=self._on_connect,
        )
        self.connect_btn.pack(pady=15, padx=30, fill="x", ipady=6)

        self.disconnect_btn = tk.Button(
            self.root,
            text="Отключиться",
            font=("Inter", 12, "bold"),
            bg="#d8a8a8",
            fg="#1a1a2e",
            activebackground="#b88888",
            relief="flat",
            cursor="hand2",
            command=self._on_disconnect,
        )

        status_frame = tk.Frame(self.root, bg="#222244", bd=1, relief="solid")
        status_frame.pack(pady=10, padx=30, fill="x")

        self.status_label = tk.Label(
            status_frame,
            text="Статус: Отключено",
            font=("Inter", 11),
            fg="#d8a8a8",
            bg="#222244",
            pady=8,
        )
        self.status_label.pack()

        self.vm_label = tk.Label(
            status_frame,
            text="",
            font=("Consolas", 10),
            fg="#a8d8c4",
            bg="#222244",
            pady=4,
        )
        self.vm_label.pack()

    def _on_connect(self):
        key = self.key_entry.get().strip()
        if not key:
            messagebox.showwarning("Ошибка", "Введите ключ активации")
            return

        self.connect_btn.config(state="disabled", text="Подключение...")
        threading.Thread(target=self._activate_key, args=(key,), daemon=True).start()

    def _activate_key(self, key: str):
        try:
            resp = requests.post(
                f"{API_BASE}/api/proxy/activate",
                json={"activation_key": key},
                timeout=10,
            )

            if resp.status_code == 200:
                data = resp.json()
                self.user_id = data["user_id"]
                vm = data["vm"]

                self.root.after(0, self._show_connected, vm)
                self._start_websocket()
            elif resp.status_code == 503:
                self.root.after(
                    0,
                    self._show_error,
                    "Все прокси-серверы заняты. Попробуйте позже.",
                )
            else:
                detail = resp.json().get("detail", "Неизвестная ошибка")
                self.root.after(0, self._show_error, detail)
        except requests.exceptions.ConnectionError:
            self.root.after(0, self._show_error, "Не удалось подключиться к серверу")
        except Exception as e:
            self.root.after(0, self._show_error, str(e))

    def _show_connected(self, vm: dict):
        self.connected = True
        self.status_label.config(text="Статус: Подключено", fg="#a8d8b4")
        self.vm_label.config(
            text=f"{vm['protocol']}://{vm['host']}:{vm['port']} ({vm['name']})"
        )
        self.connect_btn.pack_forget()
        self.disconnect_btn.pack(pady=15, padx=30, fill="x", ipady=6)
        self.key_entry.config(state="disabled")

    def _show_error(self, message: str):
        self.status_label.config(text="Статус: Ошибка", fg="#d8a8a8")
        self.vm_label.config(text="")
        self.connect_btn.config(state="normal", text="Подключиться")
        messagebox.showerror("Ошибка", message)

    def _show_disconnected(self):
        self.connected = False
        self.status_label.config(text="Статус: Отключено", fg="#d8a8a8")
        self.vm_label.config(text="")
        self.disconnect_btn.pack_forget()
        self.connect_btn.pack(pady=15, padx=30, fill="x", ipady=6)
        self.connect_btn.config(state="normal", text="Подключиться")
        self.key_entry.config(state="normal")

    def _on_disconnect(self):
        self.disconnect_btn.config(state="disabled", text="Отключение...")
        threading.Thread(target=self._disconnect, daemon=True).start()

    def _disconnect(self):
        if self.ws:
            asyncio.run_coroutine_threadsafe(self.ws.close(), self.ws_loop)
        self.root.after(0, self._show_disconnected)

    def _start_websocket(self):
        self.ws_thread = threading.Thread(target=self._run_ws_loop, daemon=True)
        self.ws_thread.start()

    def _run_ws_loop(self):
        self.ws_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ws_loop)
        self.ws_loop.run_until_complete(self._ws_listen())

    async def _ws_listen(self):
        uri = f"{WS_BASE}/ws/status/{self.user_id}"
        try:
            async with websockets.connect(uri) as ws:
                self.ws = ws
                async for message in ws:
                    try:
                        data = json.loads(message)
                        status = data.get("status", "unknown")

                        if status == "connected":
                            vm = data.get("vm")
                            if vm:
                                self.root.after(0, self._show_connected, vm)
                        elif status == "disconnected":
                            self.root.after(0, self._show_disconnected)
                        elif status == "no_free_vms":
                            self.root.after(
                                0,
                                self._show_error,
                                "Все прокси заняты",
                            )
                        elif status == "error":
                            msg = data.get("message", "Ошибка сервера")
                            self.root.after(0, self._show_error, msg)
                    except json.JSONDecodeError:
                        pass
        except Exception:
            if self.connected:
                self.root.after(0, self._show_disconnected)


def main():
    root = tk.Tk()
    ProxyClientApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
