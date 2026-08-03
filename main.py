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

    self.title("Sigma Macro Pro")
    self.geometry("320x520+50+50")  # ขยายความสูงเพื่อใส่ช่องตั้งค่า Delay
    self.attributes("-topmost", True)
    self.attributes("-alpha", 0.9)

    # Variables
    self.record_state = 0
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
    self.card_select.pack(pady=4, fill="x", padx=20)

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
    self.card_place.pack(pady=4, fill="x", padx=20)

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

    # Loop & Delay Settings Panel
    self.frame_settings = ctk.CTkFrame(self, fg_color="transparent")
    self.frame_settings.pack(pady=8, fill="x", padx=20)

    # Loop Count Setting
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
    self.entry_loop.pack(pady=(2, 6))

    # Delay Settings Frame (เรียงเป็น 2 คอลัมน์)
    self.frame_delays = ctk.CTkFrame(self.frame_settings, fg_color="transparent")
    self.frame_delays.pack(fill="x")

    # Start Delay
    self.frame_start_delay = ctk.CTkFrame(
        self.frame_delays, fg_color="transparent"
    )
    self.frame_start_delay.pack(side="left", expand=True, fill="x", padx=(0, 5))
    ctk.CTkLabel(
        self.frame_start_delay,
        text="Start Delay (sec):",
        font=("Segoe UI", 10),
    ).pack(anchor="w")
    self.entry_start_delay = ctk.CTkEntry(self.frame_start_delay, width=130)
    self.entry_start_delay.insert(0, "0.5")
    self.entry_start_delay.pack(pady=2)

    # Click Delay
    self.frame_click_delay = ctk.CTkFrame(
        self.frame_delays, fg_color="transparent"
    )
    self.frame_click_delay.pack(side="right", expand=True, fill="x", padx=(5, 0))
    ctk.CTkLabel(
        self.frame_click_delay,
        text="Action Delay (sec):",
        font=("Segoe UI", 10),
    ).pack(anchor="w")
    self.entry_click_delay = ctk.CTkEntry(self.frame_click_delay, width=130)
    self.entry_click_delay.insert(0, "0.5")
    self.entry_click_delay.pack(pady=2)

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
    cur_x, cur_y = pyautogui.position()

    if self.record_state == 0 or self.record_state == 2:
      self.select_pos = (cur_x, cur_y)
      self.record_state = 1

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
      self.place_pos = (cur_x, cur_y)
      self.record_state = 2

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
    # ดึงค่าตั้งค่า
    raw_loop = self.entry_loop.get().strip().lower()
    is_inf = raw_loop == "inf"
    max_loops = (
        float("inf") if is_inf else int(raw_loop if raw_loop.isdigit() else 100)
    )

    try:
      start_delay = float(self.entry_start_delay.get().strip())
    except ValueError:
      start_delay = 0.5

    try:
      action_delay = float(self.entry_click_delay.get().strip())
    except ValueError:
      action_delay = 0.5

    # 1. หน่วงเวลาก่อนเริ่มงานรอบแรก (Start Delay)
    self.lbl_status.configure(
        text=f"Starting in {start_delay}s...", text_color="#F59E0B"
    )
    time.sleep(start_delay)

    if not self.is_running:
      return

    self.lbl_status.configure(text="Macro Running...", text_color="#10B981")

    count = 0
    while self.is_running and count < max_loops:
      # 2. คลิกเลือกยูนิต
      pyautogui.click(self.select_pos[0], self.select_pos[1])

      # หน่วงเวลาก่อนคลิกจุดถัดไป (Action Delay)
      time.sleep(action_delay)

      if not self.is_running:
        break

      # 3. คลิกวางยูนิต
      pyautogui.click(self.place_pos[0], self.place_pos[1])

      # หน่วงเวลาก่อนเริ่มรอบถัดไป
      time.sleep(action_delay)

      count += 1

    if self.is_running:
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
