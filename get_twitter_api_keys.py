#!/usr/bin/env python
"""
Twitter API Key Generator Guide

این برنامه به شما نشان می‌دهد که چگونه کلیدهای API توییتر را به دست آورید 
و برای استفاده در برنامه‌های مختلف ذخیره کنید.
"""
import os
import sys
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from datetime import datetime
import tweepy

# ------------------------------- تنظیمات -----------------------------
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".twitter_keys")
CONFIG_FILE = os.path.join(CONFIG_DIR, "credentials.json")

# -------------------- راهنماهای گام به گام برای API توییتر -----------
GUIDE_TEXT = """
# راهنمای دریافت کلیدهای API توییتر

## مرحله 1: ثبت‌نام در پلتفرم توسعه‌دهندگان توییتر
1. به حساب توییتر خود وارد شوید
2. به https://developer.twitter.com مراجعه کنید
3. روی "Sign Up" کلیک کنید و مراحل ثبت‌نام را تکمیل کنید
4. توضیح دهید که می‌خواهید چه استفاده‌ای از API توییتر داشته باشید

## مرحله 2: ایجاد یک پروژه جدید
1. به داشبورد توسعه‌دهندگان خود بروید
2. روی "Projects & Apps" کلیک کنید
3. یک پروژه جدید ایجاد کنید
4. یک برنامه (App) جدید در پروژه خود ایجاد کنید

## مرحله 3: دریافت کلیدهای API
1. پس از ایجاد برنامه، به بخش "Keys and Tokens" بروید
2. "API Key and Secret" را کپی کنید. اینها همان Consumer Key و Consumer Secret هستند
3. روی "Generate" برای Access Token و Access Token Secret کلیک کنید
4. این مقادیر را در جای امنی ذخیره کنید

## مرحله 4: تنظیم مجوزهای برنامه
1. به بخش "App Settings" بروید
2. مطمئن شوید که برنامه شما دارای مجوز "Read and Write" باشد
3. اگر می‌خواهید Direct Message ارسال کنید، مجوز "Read, Write, and Direct Messages" را انتخاب کنید
4. برنامه را ذخیره کنید

## مرحله 5: تنظیم Callback URL
1. برای برنامه‌های وب، یک Callback URL تنظیم کنید (برای اسکریپت‌های ساده می‌توانید از http://localhost:8000 استفاده کنید)
2. تغییرات را ذخیره کنید
"""

# ---------------------------- توابع کمکی -------------------------------
def ensure_config_dir():
    """اطمینان از وجود پوشه پیکربندی"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)


def save_credentials(creds):
    """ذخیره اطلاعات API در فایل پیکربندی"""
    ensure_config_dir()
    creds["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(creds, f, indent=2, ensure_ascii=False)
    
    return True


def load_credentials():
    """بارگذاری اطلاعات API از فایل پیکربندی"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def verify_credentials(consumer_key, consumer_secret, access_token, access_token_secret):
    """بررسی اعتبار اطلاعات API با فراخوانی یک API ساده"""
    try:
        auth = tweepy.OAuth1UserHandler(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret
        )
        api = tweepy.API(auth)
        user = api.verify_credentials()
        return True, f"@{user.screen_name} (فعال)"
    except Exception as e:
        return False, f"خطا: {str(e)}"


def open_twitter_developer():
    """باز کردن صفحه توسعه‌دهندگان توییتر"""
    webbrowser.open("https://developer.twitter.com/en/portal/dashboard")


def open_twitter_apps():
    """باز کردن صفحه برنامه‌های توییتر"""
    webbrowser.open("https://developer.twitter.com/en/portal/projects-and-apps")


# ---------------------------- رابط کاربری ----------------------------
class TwitterAPIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitter API Key Generator | راهنمای دریافت کلیدهای API توییتر")
        self.root.geometry("900x700")
        self.configure_styles()
        
        # بارگذاری اطلاعات ذخیره شده
        self.credentials = load_credentials()
        
        # ایجاد رابط کاربری
        self.create_notebook()
        
    def configure_styles(self):
        """پیکربندی استایل‌های رابط کاربری"""
        style = ttk.Style()
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TFrame", background="#ffffff")
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        
    def create_notebook(self):
        """ایجاد صفحات تب برای بخش‌های مختلف برنامه"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # تب راهنما
        guide_frame = ttk.Frame(notebook)
        self.create_guide_tab(guide_frame)
        notebook.add(guide_frame, text="راهنمای گام به گام")
        
        # تب ورود اطلاعات API
        credentials_frame = ttk.Frame(notebook)
        self.create_credentials_tab(credentials_frame)
        notebook.add(credentials_frame, text="ورود اطلاعات API")
        
        # تب بررسی اعتبار
        verify_frame = ttk.Frame(notebook)
        self.create_verify_tab(verify_frame)
        notebook.add(verify_frame, text="بررسی اعتبار اطلاعات")
        
        # تب خروجی برای استفاده در برنامه‌ها
        export_frame = ttk.Frame(notebook)
        self.create_export_tab(export_frame)
        notebook.add(export_frame, text="خروجی برای برنامه‌ها")
        
    def create_guide_tab(self, parent):
        """ایجاد تب راهنما"""
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # عنوان
        header = ttk.Label(
            frame, 
            text="راهنمای دریافت کلیدهای API توییتر", 
            style="Header.TLabel"
        )
        header.pack(pady=(0, 10))
        
        # متن راهنما
        guide_text = scrolledtext.ScrolledText(
            frame, 
            wrap=tk.WORD, 
            font=("Helvetica", 10),
            height=25
        )
        guide_text.insert(tk.INSERT, GUIDE_TEXT)
        guide_text.configure(state="disabled")
        guide_text.pack(fill="both", expand=True)
        
        # دکمه‌های باز کردن صفحات وب
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=10)
        
        developer_btn = ttk.Button(
            button_frame, 
            text="باز کردن صفحه توسعه‌دهندگان توییتر", 
            command=open_twitter_developer
        )
        developer_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        apps_btn = ttk.Button(
            button_frame, 
            text="باز کردن صفحه برنامه‌های توییتر", 
            command=open_twitter_apps
        )
        apps_btn.pack(side=tk.LEFT)
        
    def create_credentials_tab(self, parent):
        """ایجاد تب ورود اطلاعات API"""
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # عنوان
        header = ttk.Label(
            frame, 
            text="ورود اطلاعات API توییتر", 
            style="Header.TLabel"
        )
        header.pack(pady=(0, 20))
        
        # فرم ورود اطلاعات
        form_frame = ttk.Frame(frame)
        form_frame.pack(fill="both")
        
        # Consumer Key
        ttk.Label(form_frame, text="Consumer Key (API Key):").grid(row=0, column=0, sticky="w", pady=5)
        self.consumer_key_var = tk.StringVar(value=self.credentials.get("consumer_key", ""))
        ttk.Entry(form_frame, textvariable=self.consumer_key_var, width=50).grid(row=0, column=1, sticky="w", pady=5)
        
        # Consumer Secret
        ttk.Label(form_frame, text="Consumer Secret (API Secret):").grid(row=1, column=0, sticky="w", pady=5)
        self.consumer_secret_var = tk.StringVar(value=self.credentials.get("consumer_secret", ""))
        ttk.Entry(form_frame, textvariable=self.consumer_secret_var, width=50, show="*").grid(row=1, column=1, sticky="w", pady=5)
        
        # Access Token
        ttk.Label(form_frame, text="Access Token:").grid(row=2, column=0, sticky="w", pady=5)
        self.access_token_var = tk.StringVar(value=self.credentials.get("access_token", ""))
        ttk.Entry(form_frame, textvariable=self.access_token_var, width=50).grid(row=2, column=1, sticky="w", pady=5)
        
        # Access Token Secret
        ttk.Label(form_frame, text="Access Token Secret:").grid(row=3, column=0, sticky="w", pady=5)
        self.access_token_secret_var = tk.StringVar(value=self.credentials.get("access_token_secret", ""))
        ttk.Entry(form_frame, textvariable=self.access_token_secret_var, width=50, show="*").grid(row=3, column=1, sticky="w", pady=5)
        
        # دکمه ذخیره
        save_btn = ttk.Button(frame, text="ذخیره اطلاعات", command=self.save_credentials_action)
        save_btn.pack(pady=20)
        
        # پیام وضعیت
        self.status_label = ttk.Label(frame, text="")
        self.status_label.pack(pady=5)
        
        # نمایش زمان آخرین به‌روزرسانی
        if "last_updated" in self.credentials:
            last_update = ttk.Label(
                frame, 
                text=f"آخرین به‌روزرسانی: {self.credentials['last_updated']}"
            )
            last_update.pack(pady=5)
            
    def create_verify_tab(self, parent):
        """ایجاد تب بررسی اعتبار"""
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # عنوان
        header = ttk.Label(
            frame, 
            text="بررسی اعتبار اطلاعات API", 
            style="Header.TLabel"
        )
        header.pack(pady=(0, 20))
        
        # توضیحات
        desc = ttk.Label(
            frame, 
            text="با کلیک روی دکمه زیر، اطلاعات API وارد شده را بررسی کنید."
        )
        desc.pack(pady=(0, 20))
        
        # دکمه بررسی
        verify_btn = ttk.Button(frame, text="بررسی اعتبار اطلاعات", command=self.verify_credentials_action)
        verify_btn.pack(pady=10)
        
        # نتیجه بررسی
        self.verify_result = ttk.Label(frame, text="")
        self.verify_result.pack(pady=10)
        
    def create_export_tab(self, parent):
        """ایجاد تب خروجی برای استفاده در برنامه‌ها"""
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # عنوان
        header = ttk.Label(
            frame, 
            text="خروجی برای استفاده در برنامه‌ها", 
            style="Header.TLabel"
        )
        header.pack(pady=(0, 20))
        
        # توضیحات
        desc = ttk.Label(
            frame, 
            text="از فرمت‌های زیر برای استفاده در برنامه‌های مختلف استفاده کنید:"
        )
        desc.pack(pady=(0, 20))
        
        # فرمت‌های مختلف
        export_frame = ttk.Frame(frame)
        export_frame.pack(fill="both", expand=True)
        
        # برای فایل accounts.txt
        ttk.Label(export_frame, text="1. برای فایل accounts.txt (استفاده در post_tweets.py):").pack(anchor="w", pady=(10, 5))
        self.accounts_format = scrolledtext.ScrolledText(export_frame, height=3, font=("Courier", 10))
        self.accounts_format.pack(fill="x")
        
        # برای متغیرهای محیطی
        ttk.Label(export_frame, text="2. برای متغیرهای محیطی:").pack(anchor="w", pady=(10, 5))
        self.env_format = scrolledtext.ScrolledText(export_frame, height=5, font=("Courier", 10))
        self.env_format.pack(fill="x")
        
        # برای Python
        ttk.Label(export_frame, text="3. برای استفاده مستقیم در کد Python:").pack(anchor="w", pady=(10, 5))
        self.python_format = scrolledtext.ScrolledText(export_frame, height=5, font=("Courier", 10))
        self.python_format.pack(fill="x")
        
        # دکمه به‌روزرسانی فرمت‌ها
        update_btn = ttk.Button(frame, text="به‌روزرسانی فرمت‌ها", command=self.update_formats)
        update_btn.pack(pady=10)
        
    def save_credentials_action(self):
        """ذخیره اطلاعات API"""
        creds = {
            "consumer_key": self.consumer_key_var.get().strip(),
            "consumer_secret": self.consumer_secret_var.get().strip(),
            "access_token": self.access_token_var.get().strip(),
            "access_token_secret": self.access_token_secret_var.get().strip()
        }
        
        # بررسی خالی نبودن فیلدها
        if not all(creds.values()):
            self.status_label.config(text="لطفاً همه فیلدها را پر کنید", foreground="red")
            return
        
        # ذخیره اطلاعات
        if save_credentials(creds):
            self.credentials = creds
            self.status_label.config(text="اطلاعات با موفقیت ذخیره شد", foreground="green")
            self.update_formats()
        else:
            self.status_label.config(text="خطا در ذخیره اطلاعات", foreground="red")
            
    def verify_credentials_action(self):
        """بررسی اعتبار اطلاعات API"""
        creds = {
            "consumer_key": self.consumer_key_var.get().strip(),
            "consumer_secret": self.consumer_secret_var.get().strip(),
            "access_token": self.access_token_var.get().strip(),
            "access_token_secret": self.access_token_secret_var.get().strip()
        }
        
        # بررسی خالی نبودن فیلدها
        if not all(creds.values()):
            self.verify_result.config(text="لطفاً ابتدا همه اطلاعات API را وارد کنید", foreground="red")
            return
        
        # بررسی اعتبار
        success, message = verify_credentials(**creds)
        
        if success:
            self.verify_result.config(text=f"اطلاعات معتبر است. حساب: {message}", foreground="green")
        else:
            self.verify_result.config(text=f"اطلاعات نامعتبر است. {message}", foreground="red")
            
    def update_formats(self):
        """به‌روزرسانی فرمت‌های خروجی"""
        creds = {
            "consumer_key": self.consumer_key_var.get().strip(),
            "consumer_secret": self.consumer_secret_var.get().strip(),
            "access_token": self.access_token_var.get().strip(),
            "access_token_secret": self.access_token_secret_var.get().strip()
        }
        
        # اگر اطلاعات کامل نیست، فرمت‌ها را خالی کن
        if not all(creds.values()):
            for widget in [self.accounts_format, self.env_format, self.python_format]:
                widget.configure(state="normal")
                widget.delete(1.0, tk.END)
                widget.configure(state="disabled")
            return
        
        # برای accounts.txt
        self.accounts_format.configure(state="normal")
        self.accounts_format.delete(1.0, tk.END)
        self.accounts_format.insert(tk.INSERT, 
            f"{creds['consumer_key']},{creds['consumer_secret']},{creds['access_token']},{creds['access_token_secret']}"
        )
        self.accounts_format.configure(state="disabled")
        
        # برای متغیرهای محیطی
        self.env_format.configure(state="normal")
        self.env_format.delete(1.0, tk.END)
        self.env_format.insert(tk.INSERT, 
            f"TWITTER_CONSUMER_KEY={creds['consumer_key']}\n"
            f"TWITTER_CONSUMER_SECRET={creds['consumer_secret']}\n"
            f"TWITTER_ACCESS_TOKEN={creds['access_token']}\n"
            f"TWITTER_ACCESS_TOKEN_SECRET={creds['access_token_secret']}"
        )
        self.env_format.configure(state="disabled")
        
        # برای Python
        self.python_format.configure(state="normal")
        self.python_format.delete(1.0, tk.END)
        self.python_format.insert(tk.INSERT, 
            f"consumer_key = \"{creds['consumer_key']}\"\n"
            f"consumer_secret = \"{creds['consumer_secret']}\"\n"
            f"access_token = \"{creds['access_token']}\"\n"
            f"access_token_secret = \"{creds['access_token_secret']}\"\n"
        )
        self.python_format.configure(state="disabled")


def main():
    """تابع اصلی برنامه"""
    # تنظیم کدگذاری برای پشتیبانی بهتر از کاراکترهای یونیکد
    if sys.stdout.encoding != 'utf-8':
        if hasattr(sys.stdout, 'buffer'):
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    root = tk.Tk()
    app = TwitterAPIApp(root)
    
    # تنظیم فونت مناسب برای نمایش متن فارسی
    try:
        try_fonts = ["Tahoma", "Arial", "Helvetica"]
        for font in try_fonts:
            root.option_add("*Font", font)
            break
    except Exception:
        pass  # در صورت عدم موفقیت، از فونت پیش‌فرض استفاده می‌کنیم
    
    root.mainloop()


if __name__ == "__main__":
    main()
