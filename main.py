# main.py

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
        input_frame = tk.LabelFrame(self.master, text="Input Transaksi Baru", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(input_frame, text="Item (pisahkan dengan koma, cth: kopi,gula,rokok):").pack(anchor="w")
        self.transaction_entry = tk.Entry(input_frame, width=50)
        self.transaction_entry.pack(pady=5, fill="x")
        
        add_button = tk.Button(input_frame, text="Tambah Transaksi", command=self.add_transaction)
        add_button.pack(pady=5)

        settings_frame = tk.LabelFrame(self.master, text="Pengaturan Analisis", padx=10, pady=10)
        settings_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(settings_frame, text="Min Support (0.0 - 1.0):").grid(row=0, column=0, sticky="w", pady=2)
        self.min_support_entry = tk.Entry(settings_frame, width=10)
        self.min_support_entry.insert(0, "0.1")
        self.min_support_entry.grid(row=0, column=1, sticky="ew", pady=2)

        tk.Label(settings_frame, text="Kategori Boros (pisahkan dengan koma, cth: rokok,snack):").grid(row=1, column=0, sticky="w", pady=2)
        self.wasteful_categories_entry = tk.Entry(settings_frame, width=50)
        self.wasteful_categories_entry.insert(0, "rokok,snack,minuman bersoda")
        self.wasteful_categories_entry.grid(row=1, column=1, sticky="ew", pady=2)
        settings_frame.grid_columnconfigure(1, weight=1)

        analyze_button = tk.Button(settings_frame, text="Analisis Belanja", command=self.analyze_spending)
        analyze_button.grid(row=2, columnspan=2, pady=10)

        transactions_display_frame = tk.LabelFrame(self.master, text="Transaksi Tersimpan", padx=10, pady=10)
        transactions_display_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.transactions_text = scrolledtext.ScrolledText(transactions_display_frame, width=70, height=10, wrap=tk.WORD)
        self.transactions_text.pack(fill="both", expand=True)

        clear_button = tk.Button(transactions_display_frame, text="Bersihkan Semua Transaksi", command=self.clear_all_transactions)
        clear_button.pack(pady=5)

        results_frame = tk.LabelFrame(self.master, text="Hasil Analisis & Rekomendasi", padx=10, pady=10)
        results_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Ubah state awal menjadi normal agar bisa diisi
        self.results_text = scrolledtext.ScrolledText(results_frame, width=70, height=15, wrap=tk.WORD, state=tk.NORMAL)
        self.results_text.pack(fill="both", expand=True)

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
        self.transaction_entry.delete(0, tk.END)
        messagebox.showinfo("Sukses", "Transaksi berhasil ditambahkan!")

    def clear_all_transactions(self):
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus SEMUA transaksi? Tindakan ini tidak dapat dibatalkan."):
            self.transactions_data = []
            self.data_manager.save_transactions(self.transactions_data)
            self.update_transactions_display()
            self.results_text.configure(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.configure(state=tk.DISABLED) # Kunci kembali setelah bersih
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
                raise ValueError("Nilai harus antara 0.0 dan 1.0")
        except ValueError:
            messagebox.showerror("Input Error", "Min Support harus berupa angka desimal antara 0.0 dan 1.0.")
            return

        wasteful_categories = [cat.strip() for cat in wasteful_cat_str.split(',') if cat.strip()] if wasteful_cat_str else []

        # 🌟 Buka state untuk bisa ditulis
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Memulai analisis...\n")
        self.master.update_idletasks() # Perbarui GUI agar pesan ini terlihat

        if not self.transactions_data:
            self.results_text.insert(tk.END, "Tidak ada data transaksi untuk dianalisis.\n")
            self.results_text.configure(state=tk.DISABLED)
            return

        try:
            processor = TransactionProcessor(self.transactions_data)
            processed_transactions = processor.get_transactions()
            print("\n--- DEBUG: Proses Transaksi ---") # DEBUG
            print(f"Total transaksi yang diproses: {len(processed_transactions)}") # DEBUG
            print(f"Transaksi bersih: {processed_transactions}") # DEBUG
            
            apriori_algo = AprioriAlgorithm(min_support)
            self.frequent_itemsets = apriori_algo.find_frequent_itemsets(processed_transactions)
            print("\n--- DEBUG: Hasil Apriori ---") # DEBUG
            print(f"Min Support: {min_support}") # DEBUG
            print(f"Frequent Itemsets Ditemukan: {self.frequent_itemsets}") # DEBUG

            if not self.frequent_itemsets:
                self.results_text.insert(tk.END, "Tidak ada itemset frekuen yang ditemukan pada support minimum ini.\n")
                self.results_text.insert(tk.END, "Coba turunkan nilai Min Support atau tambahkan lebih banyak transaksi.\n")
                self.results_text.configure(state=tk.DISABLED)
                return

            detector = WastefulSpendingDetector(self.frequent_itemsets, wasteful_categories=wasteful_categories)
            self.wasteful_patterns = detector.detect_wasteful_patterns()
            print("\n--- DEBUG: Deteksi Pola Boros ---") # DEBUG
            print(f"Kategori Boros: {wasteful_categories}") # DEBUG
            print(f"Pola Boros Ditemukan: {self.wasteful_patterns}") # DEBUG

            self.results_text.insert(tk.END, "\n--- Hasil Analisis Pola Belanja Boros ---\n")
            if self.wasteful_patterns:
                sorted_patterns = sorted(self.wasteful_patterns.items(), key=lambda x: -x[1]) # Urutkan dari support tertinggi
                for pattern, support in sorted_patterns:
                    pattern_str = ", ".join(list(pattern)) # frozenset perlu diubah ke list untuk join
                    self.results_text.insert(tk.END, f"Pola Boros: {pattern_str} (Support: {support:.2f})\n")
            else:
                self.results_text.insert(tk.END, "Tidak ada pola boros yang terdeteksi berdasarkan kriteria yang diberikan.\n")

            self.results_text.insert(tk.END, "\n--- Rekomendasi ---\n")
            recommendations = detector.generate_recommendations(self.wasteful_patterns)
            for rec in recommendations:
                self.results_text.insert(tk.END, f"{rec}\n")
            
        except Exception as e:
            import traceback
            error_message = f"Terjadi kesalahan saat analisis:\n{traceback.format_exc()}"
            self.results_text.insert(tk.END, error_message)
            print(f"ERROR: {error_message}") # DEBUG error to console

        finally: # Blok finally akan selalu dieksekusi, memastikan state kembali ke DISABLED
            # 🌟 Kunci kembali agar tidak bisa diubah manual setelah semua selesai
            self.results_text.configure(state=tk.DISABLED)
            self.master.update_idletasks() # Pastikan semua update GUI selesai


if __name__ == "__main__":
    root = tk.Tk()
    app = SpendingAnalyzerAppGUI(root)
    root.mainloop()