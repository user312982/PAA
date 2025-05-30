# data_manager.py

import json
import os

class DataManager:
    """
    Kelas untuk mengelola penyimpanan dan pemuatan data transaksi dari file JSON.
    """
    def __init__(self, filename="transactions.json"):
        self.filename = filename
        self._create_file_if_not_exists()

    def _create_file_if_not_exists(self):
        """
        Membuat file JSON jika belum ada.
        """
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f) # Inisialisasi dengan list kosong

    def load_transactions(self):
        """
        Memuat transaksi dari file JSON.

        Returns:
            list of list of str: Data transaksi.
        """
        with open(self.filename, 'r') as f:
            try:
                data = json.load(f)
                # Pastikan setiap transaksi adalah list of str
                if not isinstance(data, list):
                    return []
                for transaction in data:
                    if not isinstance(transaction, list) or not all(isinstance(item, str) for item in transaction):
                        return [] # Jika format tidak sesuai, kembalikan kosong
                return data
            except json.JSONDecodeError:
                return [] # Jika file JSON rusak atau kosong, kembalikan list kosong

    def save_transactions(self, transactions):
        """
        Menyimpan transaksi ke file JSON.

        Args:
            transactions (list of list of str): Data transaksi yang akan disimpan.
        """
        with open(self.filename, 'w') as f:
            json.dump(transactions, f, indent=4) # indent=4 agar JSON mudah dibaca