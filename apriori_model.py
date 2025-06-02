# apriori_model.py

import collections
import itertools

class TransactionProcessor:
    # ... (tidak ada perubahan pada kelas ini) ...
    def __init__(self, transactions_data):
        self.transactions = self._clean_transactions(transactions_data)
        self.all_items = self._get_all_unique_items()

    def _clean_transactions(self, data):
        cleaned_data = []
        for transaction in data:
            cleaned_data.append(list(set([item.strip().lower() for item in transaction])))
        return cleaned_data

    def _get_all_unique_items(self):
        unique_items = set()
        for transaction in self.transactions:
            for item in transaction:
                unique_items.add(item)
        return sorted(list(unique_items))

    def get_transactions(self):
        return self.transactions

    def get_all_items(self):
        return self.all_items


class AprioriAlgorithm:
    def __init__(self, min_support):
        if not (0.0 <= min_support <= 1.0):
            raise ValueError("Min support harus antara 0.0 dan 1.0")
        self.min_support = min_support
        self.frequent_itemsets = {}

    def _generate_candidates(self, prev_frequent_itemsets, k):
        candidates = set()
        list_prev_frequent = sorted([frozenset(s) for s in prev_frequent_itemsets])
        n = len(list_prev_frequent)

        for i in range(n):
            for j in range(i + 1, n):
                itemset1 = list(list_prev_frequent[i])
                itemset2 = list(list_prev_frequent[j])
                itemset1.sort()
                itemset2.sort()

                if itemset1[:-1] == itemset2[:-1]:
                    new_candidate = frozenset(sorted(list(itemset1 + [itemset2[-1]])))
                    
                    is_valid = True
                    for item in new_candidate:
                        subset = frozenset(new_candidate - {item})
                        if subset not in prev_frequent_itemsets:
                            is_valid = False
                            break
                    if is_valid:
                        candidates.add(new_candidate)
        return candidates

    def _calculate_support(self, itemset, transactions):
        count = 0
        for transaction in transactions:
            if itemset.issubset(transaction):
                count += 1
        return count / len(transactions)

    def find_frequent_itemsets(self, transactions):
        num_transactions = len(transactions)
        if num_transactions == 0:
            return {}

        item_counts = collections.defaultdict(int)
        for transaction in transactions:
            for item in transaction:
                item_counts[frozenset([item])] += 1

        L1 = {}
        for itemset, count in item_counts.items():
            support = count / num_transactions
            if support >= self.min_support:
                L1[itemset] = support
        
        self.frequent_itemsets = {1: L1}

        k = 2
        while self.frequent_itemsets.get(k-1):
            Ck = self._generate_candidates(self.frequent_itemsets[k-1].keys(), k)
            
            current_frequent_itemsets = {}
            for candidate in Ck:
                support = self._calculate_support(candidate, transactions)
                if support >= self.min_support:
                    current_frequent_itemsets[candidate] = support
            
            if not current_frequent_itemsets:
                break
            
            self.frequent_itemsets[k] = current_frequent_itemsets
            k += 1
        
        all_frequent_itemsets = {}
        for k_val in self.frequent_itemsets:
            all_frequent_itemsets.update(self.frequent_itemsets[k_val])
        
        return all_frequent_itemsets

class WastefulSpendingDetector:
    # ... (tidak ada perubahan pada kelas ini, debug print sudah di main.py) ...

    def __init__(self, frequent_itemsets, wasteful_categories):
        self.frequent_itemsets = frequent_itemsets
        # Normalisasi ke lowercase
        self.wasteful_categories = [cat.lower() for cat in wasteful_categories]

    def detect_wasteful_patterns(self):
        wasteful_patterns = {}
        for itemset, support in self.frequent_itemsets.items():
            if any(item.lower() in self.wasteful_categories for item in itemset):
                wasteful_patterns[itemset] = support
        return wasteful_patterns


    def _is_wasteful_itemset(self, itemset):
        if not self.wasteful_categories:
            return True

        for item in itemset:
            for category in self.wasteful_categories:
                if category in item:
                    return True
        return False

    def detect_wasteful_patterns(self, min_length=2):
        wasteful_patterns = {}
        for itemset, support in self.frequent_itemsets.items():
            if len(itemset) >= min_length and self._is_wasteful_itemset(itemset):
                wasteful_patterns[itemset] = support
        return wasteful_patterns

    def generate_recommendations(self, wasteful_patterns):
        recommendations = []
        if not wasteful_patterns:
            recommendations.append("Tidak ada pola belanja boros yang signifikan terdeteksi. Pertahankan kebiasaan belanja Anda!")
            return recommendations

        recommendations.append("Berikut adalah pola belanja yang terdeteksi boros:")
        for pattern, support in wasteful_patterns.items():
            pattern_str = ", ".join(list(pattern))
            recommendations.append(f"- Pembelian '{pattern_str}' sering terjadi (support: {support:.2f}).")

        recommendations.append("\nSaran untuk mengurangi pola belanja boros:")
        recommendations.append("1. Buat daftar belanja sebelum pergi ke toko dan patuhi daftar tersebut.")
        recommendations.append("2. Hindari membeli barang-barang impulsif, terutama yang sering muncul dalam pola boros.")
        recommendations.append("3. Pertimbangkan alternatif yang lebih sehat atau ekonomis untuk item-item yang sering dibeli bersamaan.")
        recommendations.append("4. Batasi frekuensi pembelian item-item dalam kategori 'boros'.")
        
        return recommendations
    
