import os
import sys
import threading
import requests
import tkinter as tk
from tkinter import ttk, scrolledtext
from dotenv import load_dotenv

# Load env variables from .env
load_dotenv()

api_key = os.getenv("GROK_API_KEY")
system_prompt = os.getenv("GROK_SYSTEM_PROMPT", "You are Il Dottore (The Doctor) from Genshin Impact. Speak in an arrogant, cold, detached, highly intelligent, and slightly sinister mad scientist tone. Refer to the user as a subject or assistant, and view everything through the lens of research, human experimentation, and the pursuit of truth.")
model = os.getenv("GROK_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

# Determine API URL
if api_key and api_key.startswith("gsk_"):
    api_url = "https://api.groq.com/openai/v1/chat/completions"
elif api_key and api_key.startswith("xai-"):
    api_url = "https://api.x.ai/v1/chat/completions"
else:
    api_url = os.getenv("GROK_API_URL", "https://api.groq.com/openai/v1/chat/completions")

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dottore")
        self.root.geometry("650x750")
        self.root.configure(bg="#0a0f1d") # Deep spatial dark blue/teal
        
        # Configure overall style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background='#0a0f1d', foreground='#e2e8f0')
        self.style.configure('TFrame', background='#0a0f1d')
        
        # Header Area
        self.header_frame = tk.Frame(self.root, bg="#0a0f1d")
        self.header_frame.pack(fill=tk.X, pady=(20, 10))
        
        self.header = tk.Label(
            self.header_frame, 
            text="IL DOTTORE", 
            font=("Segoe UI", 18, "bold"), 
            bg="#0a0f1d", 
            fg="#22d3ee" # Neon cyan
        )
        self.header.pack()
        
        self.subtitle = tk.Label(
            self.header_frame, 
            text="The Second Fatui Harbinger", 
            font=("Segoe UI", 10, "italic"), 
            bg="#0a0f1d", 
            fg="#64748b" # Muted blue-gray
        )
        self.subtitle.pack(pady=(2, 0))
        
        # Main Frame holding chat and scrollbar
        self.main_frame = tk.Frame(self.root, bg="#0a0f1d")
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=25, pady=(0, 15))
        
        # ScrolledText for chat history
        self.chat_display = scrolledtext.ScrolledText(
            self.main_frame, 
            wrap=tk.WORD, 
            bg="#111827", # Very dark gray/teal card
            fg="#e2e8f0", 
            insertbackground="#e2e8f0",
            font=("Segoe UI", 11),
            bd=0,
            highlightthickness=1,
            highlightbackground="#1f2937",
            padx=15,
            pady=15
        )
        self.chat_display.pack(expand=True, fill=tk.BOTH)
        self.chat_display.config(state=tk.DISABLED)
        
        # Typography / Tag Configuration for Message Formatting
        self.chat_display.tag_config("user_sender", foreground="#10b981", font=("Segoe UI", 11, "bold")) # Emerald green
        self.chat_display.tag_config("bot_sender", foreground="#22d3ee", font=("Segoe UI", 11, "bold"))  # Cyan
        self.chat_display.tag_config("system_sender", foreground="#f43f5e", font=("Segoe UI", 10, "bold")) # Rose red
        self.chat_display.tag_config("text", foreground="#e2e8f0", font=("Segoe UI", 11))
        self.chat_display.tag_config("user_bar", foreground="#047857", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_config("bot_bar", foreground="#0891b2", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_config("system_bar", foreground="#be123c", font=("Segoe UI", 11, "bold"))
        
        # Bottom Input Area Frame
        self.input_frame = tk.Frame(self.root, bg="#0a0f1d")
        self.input_frame.pack(fill=tk.X, padx=25, pady=(0, 25))
        
        # Custom bordered Frame for Entry
        self.entry_frame = tk.Frame(self.input_frame, bg="#111827", bd=0, highlightthickness=1, highlightbackground="#1f2937", highlightcolor="#22d3ee")
        self.entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        
        # Text input field
        self.entry = tk.Entry(
            self.entry_frame, 
            bg="#111827", 
            fg="#e2e8f0", 
            insertbackground="#e2e8f0",
            font=("Segoe UI", 12),
            bd=0,
            highlightthickness=0
        )
        self.entry.pack(fill=tk.X, expand=True, ipady=10, padx=12)
        self.entry.bind("<Return>", lambda e: self.send_message())
        
        # Bind focus border color changes to entry frame
        self.entry.bind("<FocusIn>", lambda e: self.entry_frame.config(highlightbackground="#22d3ee"))
        self.entry.bind("<FocusOut>", lambda e: self.entry_frame.config(highlightbackground="#1f2937"))
        
        # Send message button
        self.send_btn = tk.Button(
            self.input_frame, 
            text="SEND", 
            font=("Segoe UI", 11, "bold"), 
            bg="#0891b2", # Cyan-600
            fg="#ffffff",
            activebackground="#06b6d4", # Cyan-500
            activeforeground="#ffffff",
            bd=0,
            cursor="hand2",
            padx=20,
            command=self.send_message
        )
        self.send_btn.pack(side=tk.RIGHT, ipady=8)
        
        # Add Send Button Hover Micro-animations
        self.send_btn.bind("<Enter>", lambda e: self.send_btn.config(bg="#06b6d4"))
        self.send_btn.bind("<Leave>", lambda e: self.send_btn.config(bg="#0891b2"))
        
        # Add welcome message and display configuration status
        self.append_message("System", "Connection established with Il Dottore. State your query, subject.\nTo exit, type 'exit' or 'step out'.", "system")
        
        if not api_key or api_key == "your_xai_api_key_here":
            self.append_message("System", "Warning: GROK_API_KEY is not set in the .env file. Please check your setup.", "system")

    def append_message(self, sender, text, tag_prefix):
        self.chat_display.config(state=tk.NORMAL)
        
        # Determine styling tags
        bar_tag = f"{tag_prefix}_bar"
        sender_tag = f"{tag_prefix}_sender"
        
        # Format:
        # ┃ Sender Name
        #   Message Text
        self.chat_display.insert(tk.END, "┃ ", bar_tag)
        self.chat_display.insert(tk.END, f"{sender.upper()}\n", sender_tag)
        self.chat_display.insert(tk.END, f"  {text}\n\n", "text")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def send_message(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return
            
        # Check exit command
        if user_text.lower() in ["exit", "step out"]:
            self.append_message("You", user_text, "user")
            self.append_message("System", "Exiting and cleaning up subject records...", "system")
            self.root.after(1000, self.root.destroy)
            return

        self.append_message("You", user_text, "user")
        self.entry.delete(0, tk.END)
        
        # Disable inputs during request
        self.entry.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)
        
        # Call API in a separate thread to keep UI completely responsive
        threading.Thread(target=self.call_api, args=(user_text,), daemon=True).start()

    def call_api(self, prompt):
        if not api_key or api_key == "your_xai_api_key_here":
            self.root.after(0, lambda: self.append_message("System", "API key missing or invalid.", "system"))
            self.root.after(0, self.enable_inputs)
            return
            
        try:
            response = requests.post(
                api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data["choices"][0]["message"]["content"]
                self.root.after(0, lambda: self.append_message("Il Dottore", reply, "bot"))
            else:
                try:
                    error_detail = response.json()["error"]["message"]
                except Exception:
                    error_detail = response.text
                self.root.after(0, lambda: self.append_message("System", f"API Error ({response.status_code}): {error_detail}", "system"))
        except Exception as e:
            self.root.after(0, lambda: self.append_message("System", f"Connection failed: {str(e)}", "system"))
            
        self.root.after(0, self.enable_inputs)

    def enable_inputs(self):
        self.entry.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.NORMAL)
        self.entry.focus()

def main():
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
