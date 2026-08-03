import threading
import time
import customtkinter as ctk
import pyautogui
from pynput import keyboard

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MacroApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("Anime Macro Pro")
    self.geometry("320x420+50+50")
    self.attributes("-topmost", True)
    self.attributes("-alpha", 0.9)

    # Variables
    self.record_state = 0  # 0: Ready, 1: Select Unit Recorded, 2: Place Unit Recorded
    self.select_pos = None
    self.place_pos = None

    self.is_running = False
    self.macro_thread = None

    # UI Components
    self.title_label = ctk.CTkLabel(
        self, text="⚡ Macro Helper", font=("Segoe UI", 18, "bold")
    )
    self.title_label.pack(pady=(15, 10))

    # Recording Status Cards
    self.card_select = ctk.CTkFrame(self, fg_color="#1E293B")
    self.card_select.pack(pady=5, fill="x", padx=20)

    self.lbl_select_title = ctk.CTkLabel(
        self.card_select,
        text="1. Select Unit Pos (F8)",
        font=("Segoe UI", 12, "bold"),
    )
    self.lbl_select_title.pack(anchor="w", padx=10, pady=(5, 0))

    self.lbl_select_pos = ctk.CTkLabel(
        self.card_select,
        text="Not Recorded",
        text_color="#94A3B8",
        font=("Segoe UI", 11),
    )
    self.lbl_select_pos.pack(anchor="w", padx=10, pady=(0, 5))

    self.card_place = ctk.CTkFrame(self, fg_color="#1E293B")
    self.card_place.pack(pady=5, fill="x", padx=20)

    self.lbl_place_title = ctk.CTkLabel(
        self.card_place,
        text="2. Place Unit Pos (F8)",
        font=("Segoe UI", 12, "bold"),
    )
    self.lbl_place_title.pack(anchor="w", padx=10, pady=(5, 0))

    self.lbl_place_pos = ctk.CTkLabel(
        self.card_place,
        text="Not Recorded",
        text_color="#94A3B8",
        font=("Segoe UI", 11),
    )
    self.lbl_place_pos.pack(anchor="w", padx=10, pady=(0, 5))

    # Loop Settings Panel
    self.frame_settings = ctk.CTkFrame(self, fg_color="transparent")
    self.frame_settings.pack(pady=10, fill="x", padx=20)

    self.lbl_loop = ctk.CTkLabel(
        self.frame_settings,
        text="Loop Count ('inf' = Unlimited):",
        font=("Segoe UI", 11),
    )
    self.lbl_loop.pack(anchor="w")

    self.entry_loop = ctk.CTkEntry(
        self.frame_settings, placeholder_text="100", width=280
    )
    self.entry_loop.insert(0, "100")
    self.entry_loop.pack(pady=5)

    # Status & Controls
    self.lbl_status = ctk.CTkLabel(
        self,
        text="Press F8 to Start Recording",
        font=("Segoe UI", 13, "bold"),
        text_color="#3B82F6",
    )
    self.lbl_status.pack(pady=10)

    self.btn_toggle = ctk.CTkButton(
        self,
        text="Start/Stop Loop (F12)",
        fg_color="#059669",
        hover_color="#047857",
        command=self.toggle_macro_loop,
    )
    self.btn_toggle.pack(pady=5)

    # Keyboard Listener Thread
    self.start_hotkey_listener()

  def handle_f8_press(self):
    """จัดการการกด F8 เพื่อสลับสเตทและไฮไลต์ GUI"""
    cur_x, cur_y = pyautogui.position()

    if self.record_state == 0 or self.record_state == 2:
      # บันทึก Select Unit
      self.select_pos = (cur_x, cur_y)
      self.record_state = 1

      # ไฮไลต์การเลือกที่ Card 1
      self.card_select.configure(
          fg_color="#1E3A8A", border_width=2, border_color="#3B82F6"
      )
      self.card_place.configure(fg_color="#1E293B", border_width=0)

      self.lbl_select_pos.configure(
          text=f"X: {cur_x}, Y: {cur_y}", text_color="#60A5FA"
      )
      self.lbl_status.configure(
          text="Select Pos Saved! Press F8 for Place Pos", text_color="#F59E0B"
      )

    elif self.record_state == 1:
      # บันทึก Place Unit
      self.place_pos = (cur_x, cur_y)
      self.record_state = 2

      # ไฮไลต์การเลือกที่ Card 2
      self.card_select.configure(
          fg_color="#1E293B", border_width=1, border_color="#10B981"
      )
      self.card_place.configure(
          fg_color="#064E3B", border_width=2, border_color="#10B981"
      )

      self.lbl_place_pos.configure(
          text=f"X: {cur_x}, Y: {cur_y}", text_color="#34D399"
      )
      self.lbl_status.configure(
          text="Both Recorded! Press F12 to Play/Stop", text_color="#10B981"
      )

  def toggle_macro_loop(self):
    """สั่งเปิด/ปิด การทำงานของลูป (F12)"""
    if self.is_running:
      self.stop_macro()
    else:
      self.start_macro()

  def start_macro(self):
    if not self.select_pos or not self.place_pos:
      self.lbl_status.configure(
          text="Error: Record both positions first!", text_color="#EF4444"
      )
      return

    self.is_running = True
    self.btn_toggle.configure(
        text="Stop Loop (F12)", fg_color="#DC2626", hover_color="#B91C1C"
    )
    self.lbl_status.configure(text="Macro Running...", text_color="#10B981")

    # รันการทำงานแบบแยก Thread
    self.macro_thread = threading.Thread(
        target=self._run_macro_loop, daemon=True
    )
    self.macro_thread.start()

  def stop_macro(self):
    self.is_running = False
    self.btn_toggle.configure(
        text="Start Loop (F12)", fg_color="#059669", hover_color="#047857"
    )
    self.lbl_status.configure(text="Macro Stopped", text_color="#F59E0B")

  def _run_macro_loop(self):
    raw_val = self.entry_loop.get().strip().lower()
    is_inf = raw_val == "inf"
    max_loops = float("inf") if is_inf else int(raw_val if raw_val.isdigit() else 100)

    count = 0
    while self.is_running and count < max_loops:
      # 1. กดเลือกยูนิต
      pyautogui.click(self.select_pos[0], self.select_pos[1])
      time.sleep(0.15)

      # 2. กดวางยูนิต
      pyautogui.click(self.place_pos[0], self.place_pos[1])
      time.sleep(0.5)  # ดีเลย์ระหว่างรอบ

      count += 1

    if self.is_running:  # ทำงานครบจำนวนรอบแล้ว
      self.after(0, self.stop_macro)

  def start_hotkey_listener(self):
    def on_press(key):
      try:
        if key == keyboard.Key.f8:
          self.after(0, self.handle_f8_press)
        elif key == keyboard.Key.f12:
          self.after(0, self.toggle_macro_loop)
      except Exception as e:
        print(f"Error: {e}")

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()


if __name__ == "__main__":
  app = MacroApp()
  app.mainloop()
