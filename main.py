import requests
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os 

API_KEY = os.getenv("EXCHANGE_API_KEY", "1c5204c15afd29ec96d69b35")  
BASE_API_URL = f"https://v6.exchangerate-api.com/v6/1c5204c15afd29ec96d69b35/pair"

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#282c34")  

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', font=('Helvetica', 14), background="#282c34", foreground="white")
        self.style.configure('Header.TLabel', font=('Helvetica', 22, 'bold'), background="#282c34", foreground="#00d4ff")
        self.style.configure('Result.TLabel', font=('Helvetica', 16, 'bold'), background="#374151", foreground="#ffcc00")
        self.style.configure('TButton', font=('Helvetica', 14, 'bold'), background="#00d4ff", foreground="black")

        self.currencies = {
            "AED": "United Arab Emirates Dirham", "AFN": "Afghan Afghani", "ALL": "Albanian Lek",
            "AMD": "Armenian Dram", "ANG": "Netherlands Antillean Guilder", "AOA": "Angolan Kwanza",
            "ARS": "Argentine Peso", "AUD": "Australian Dollar", "AWG": "Aruban Florin",
            "AZN": "Azerbaijani Manat", "BAM": "Bosnia and Herzegovina Convertible Mark",
            "BBD": "Barbadian Dollar", "BDT": "Bangladeshi Taka", "BGN": "Bulgarian Lev",
            "BHD": "Bahraini Dinar", "BIF": "Burundian Franc", "BMD": "Bermudian Dollar",
            "BND": "Brunei Dollar", "BOB": "Bolivian Boliviano", "BRL": "Brazilian Real",
            "BSD": "Bahamian Dollar", "BTN": "Bhutanese Ngultrum", "BWP": "Botswana Pula",
            "BYN": "Belarusian Ruble", "BZD": "Belize Dollar", "CAD": "Canadian Dollar",
            "CDF": "Congolese Franc", "CHF": "Swiss Franc", "CLP": "Chilean Peso",
            "CNY": "Chinese Yuan", "COP": "Colombian Peso", "CRC": "Costa Rican Colón",
            "CZK": "Czech Koruna", "DKK": "Danish Krone", "DOP": "Dominican Peso",
            "EGP": "Egyptian Pound", "EUR": "Euro", "GBP": "British Pound Sterling",
            "HKD": "Hong Kong Dollar", "IDR": "Indonesian Rupiah", "ILS": "Israeli New Shekel",
            "INR": "Indian Rupee", "JPY": "Japanese Yen", "KRW": "South Korean Won",
            "MYR": "Malaysian Ringgit", "NPR": "Nepalese Rupee", "NZD": "New Zealand Dollar",
            "PKR": "Pakistani Rupee", "PHP": "Philippine Peso", "QAR": "Qatari Riyal",
            "RUB": "Russian Ruble", "SAR": "Saudi Riyal", "SGD": "Singapore Dollar",
            "THB": "Thai Baht", "TRY": "Turkish Lira", "USD": "United States Dollar",
            "VND": "Vietnamese Đồng", "ZAR": "South African Rand"
        }

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Currency Converter", style="Header.TLabel").pack(pady=15)

        frame = tk.Frame(self.root, bg="#282c34")
        frame.pack(pady=10)

        ttk.Label(frame, text="From:", font=("Helvetica", 14, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.from_currency_var = tk.StringVar()
        self.from_currency = ttk.Combobox(frame, textvariable=self.from_currency_var, font=('Helvetica', 14), state="readonly", width=25)
        self.from_currency['values'] = [f"{code} - {name}" for code, name in self.currencies.items()]
        self.from_currency.current(0)
        self.from_currency.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame, text="To:", font=("Helvetica", 14, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.to_currency_var = tk.StringVar()
        self.to_currency = ttk.Combobox(frame, textvariable=self.to_currency_var, font=('Helvetica', 14), state="readonly", width=25)
        self.to_currency['values'] = [f"{code} - {name}" for code, name in self.currencies.items()]
        self.to_currency.current(5)
        self.to_currency.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self.root, text="Amount:", font=("Helvetica", 14, "bold")).pack(pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(self.root, font=('Helvetica', 16), justify="center", textvariable=self.amount_var, width=15)
        self.amount_entry.pack(pady=5)
        self.amount_var.trace_add("write", self.validate_number_input)
        self.amount_entry.insert(0, "1")

        self.convert_button = ttk.Button(self.root, text="Convert", command=self.convert_currency)
        self.convert_button.pack(pady=10)

        self.result_label = ttk.Label(self.root, text="1.0 USD = 139.62 NPR", style="Result.TLabel")
        self.result_label.pack(pady=15)

    def validate_number_input(self, *args):
        """Restricts input to valid decimal numbers."""
        value = self.amount_var.get()
        try:
            if value:
                float(value)
        except ValueError:
            self.amount_var.set(value[:-1])  

    def convert_currency(self):
        """Performs currency conversion."""
        from_cur = self.from_currency.get().split(" - ")[0]
        to_cur = self.to_currency.get().split(" - ")[0]
        amount = self.amount_var.get()

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount.")
            return

        threading.Thread(target=self.fetch_conversion, args=(from_cur, to_cur, amount), daemon=True).start()

    def fetch_conversion(self, from_cur, to_cur, amount):
        """Fetches conversion rates from API and updates UI."""
        try:
            response = requests.get(f"{BASE_API_URL}/{from_cur}/{to_cur}", timeout=5)
            data = response.json()

            rate = data.get("conversion_rate")
            if not rate:
                raise ValueError("Invalid API response")

            converted_amount = round(amount * rate, 2)
            self.result_label.config(text=f"{amount} {from_cur} = {converted_amount} {to_cur}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()
