import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, scrolledtext
from apriori_model import TransactionProcessor, AprioriAlgorithm, WastefulSpendingDetector
from data_manager import DataManager

class SpendingAnalyzerAppGUI:
    def __init__(self, master):
        self.master = master
        master.title("Aplikasi Deteksi Pola Belanja Boros")
        master.geometry("800x700")

        self.data_manager = DataManager()
        self.transactions_data = self.data_manager.load_transactions()

        self.frequent_itemsets = None
        self.wasteful_patterns = None

        self.create_widgets()
        self.update_transactions_display()

    def create_widgets(self):
        # Frame Input Transaksi
        input_frame = ctk.CTkFrame(self.master)
        input_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(input_frame, text="Input Transaksi Baru", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5, 5))
        ctk.CTkLabel(input_frame, text="Item (pisahkan dengan koma, cth: kopi,gula,rokok):").pack(anchor="w", padx=10)
        self.transaction_entry = ctk.CTkEntry(input_frame, width=50)
        self.transaction_entry.pack(pady=5, fill="x", padx=10)

        add_button = ctk.CTkButton(input_frame, text="Tambah Transaksi", command=self.add_transaction)
        add_button.pack(pady=5, padx=10)

        # Frame Pengaturan Analisis
        settings_frame = ctk.CTkFrame(self.master)
        settings_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(settings_frame, text="Pengaturan Analisis", font=ctk.CTkFont(weight="bold")).grid(row=0, columnspan=2, sticky="w", padx=10, pady=(5, 5))
        ctk.CTkLabel(settings_frame, text="Min Support (0.0 - 1.0):").grid(row=1, column=0, sticky="w", padx=10, pady=2)
        self.min_support_entry = ctk.CTkEntry(settings_frame, width=10)
        self.min_support_entry.insert(0, "0.1")
        self.min_support_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=2)

        ctk.CTkLabel(settings_frame, text="Kategori Boros (pisahkan dengan koma, cth: rokok,snack):").grid(row=2, column=0, sticky="w", padx=10, pady=2)
        self.wasteful_categories_entry = ctk.CTkEntry(settings_frame, width=50)
        self.wasteful_categories_entry.insert(0, "rokok,snack,minuman bersoda,permen,mie instan,sosis,kopi instan,susu kental manis")
        self.wasteful_categories_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=2)
        settings_frame.grid_columnconfigure(1, weight=1)

        analyze_button = ctk.CTkButton(settings_frame, text="Analisis Belanja", command=self.analyze_spending)
        analyze_button.grid(row=3, columnspan=2, pady=10, padx=10)

        # Frame Tampilan Transaksi
        transactions_display_frame = ctk.CTkFrame(self.master)
        transactions_display_frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkLabel(transactions_display_frame, text="Transaksi Tersimpan", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5, 5))

        self.transactions_text = scrolledtext.ScrolledText(transactions_display_frame, width=70, height=10, wrap=tk.WORD)
        self.transactions_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        clear_button = ctk.CTkButton(transactions_display_frame, text="Bersihkan Semua Transaksi", command=self.clear_all_transactions)
        clear_button.pack(pady=5, padx=10)

    def add_transaction(self):
        items_str = self.transaction_entry.get().strip()
        if not items_str:
            messagebox.showwarning("Input Kosong", "Mohon masukkan item transaksi.")
            return

        items = [item.strip() for item in items_str.split(',') if item.strip()]
        if not items:
            messagebox.showwarning("Input Tidak Valid", "Mohon masukkan item yang valid, dipisahkan koma.")
            return

        self.transactions_data.append(items)
        self.data_manager.save_transactions(self.transactions_data)
        self.update_transactions_display()
        self.transaction_entry.delete(0, ctk.END)
        messagebox.showinfo("Sukses", "Transaksi berhasil ditambahkan!")

    def clear_all_transactions(self):
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus SEMUA transaksi?"):
            self.transactions_data = []
            self.data_manager.save_transactions(self.transactions_data)
            self.update_transactions_display()
            messagebox.showinfo("Sukses", "Semua transaksi telah dihapus.")

    def update_transactions_display(self):
        self.transactions_text.delete(1.0, tk.END)
        if not self.transactions_data:
            self.transactions_text.insert(tk.END, "Belum ada transaksi tersimpan.")
            return

        for i, transaction in enumerate(self.transactions_data):
            self.transactions_text.insert(tk.END, f"{i+1}. {', '.join(transaction)}\n")

    def analyze_spending(self):
        min_support_str = self.min_support_entry.get().strip()
        wasteful_cat_str = self.wasteful_categories_entry.get().strip()

        try:
            min_support = float(min_support_str)
            if not (0.0 <= min_support <= 1.0):
                raise ValueError()
        except ValueError:
            messagebox.showerror("Input Error", "Min Support harus berupa angka desimal antara 0.0 dan 1.0.")
            return

        wasteful_categories = [cat.strip() for cat in wasteful_cat_str.split(',') if cat.strip()] if wasteful_cat_str else []

        if not self.transactions_data:
            messagebox.showinfo("Analisis Gagal", "Tidak ada data transaksi untuk dianalisis.")
            return

        try:
            processor = TransactionProcessor(self.transactions_data)
            processed_transactions = processor.get_transactions()

            apriori_algo = AprioriAlgorithm(min_support)
            self.frequent_itemsets = apriori_algo.find_frequent_itemsets(processed_transactions)

            if not self.frequent_itemsets:
                messagebox.showinfo("Hasil Analisis", "Tidak ada itemset frekuen yang ditemukan.\nCoba turunkan nilai Min Support atau tambahkan transaksi.")
                return

            detector = WastefulSpendingDetector(self.frequent_itemsets, wasteful_categories=wasteful_categories)
            self.wasteful_patterns = detector.detect_wasteful_patterns()

            # === TAMPILKAN HASIL DALAM POPUP ===
            result_popup = tk.Toplevel(self.master)
            result_popup.title("Hasil Analisis & Rekomendasi")
            result_popup.geometry("600x500")

            result_text = scrolledtext.ScrolledText(result_popup, wrap=tk.WORD, width=80, height=25)
            result_text.pack(padx=10, pady=10, fill="both", expand=True)

            result_text.insert(tk.END, "--- Hasil Analisis Pola Belanja Boros ---\n")
            if self.wasteful_patterns:
                sorted_patterns = sorted(self.wasteful_patterns.items(), key=lambda x: -x[1])
                for pattern, support in sorted_patterns:
                    pattern_str = ", ".join(sorted(list(pattern)))
                    result_text.insert(tk.END, f"Pola Boros: {pattern_str} (Support: {support:.2f})\n")
            else:
                result_text.insert(tk.END, "Tidak ada pola boros yang terdeteksi berdasarkan kriteria.\n")

            result_text.insert(tk.END, "\n--- Rekomendasi ---\n")
            recommendations = detector.generate_recommendations(self.wasteful_patterns)
            for rec in recommendations:
                result_text.insert(tk.END, f"{rec}\n")

            result_text.configure(state=tk.DISABLED)

        except Exception as e:
            import traceback
            error_message = f"Terjadi kesalahan saat analisis:\n{traceback.format_exc()}"
            messagebox.showerror("Error", error_message)

if __name__ == "__main__":
    root = ctk.CTk()
    app = SpendingAnalyzerAppGUI(root)
    root.mainloop()
