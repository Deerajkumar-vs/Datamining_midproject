
bfTime = 0.0
aTime = 0.0
choice = None
minimumSup = None
minimumConfi = None
file_name = None

import sys
import csv
from itertools import combinations
from typing import Dict, List, Tuple
import time
mini_conf=0

def frequentset(list1: List[str], notconsider: List[set], item_set_list: List[set], n: int,
                  min_supp: float, counttot: int, support_of_all_item_set: Dict[Tuple[str], int]) -> Tuple[Dict[Tuple[str], int], List[set]]:
    comb = combinations(list1, n)
    item_support_count = {}
    for i in comb:
        set_i = set(i)
        i = tuple(sorted(i))
        for j in item_set_list:
            if set_i.issubset(j):
                if notconsider:
                    count = 0
                    for k in notconsider:
                        if k.issubset(set_i):
                            count = 1
                            break
                    if not count:
                        if i in item_support_count:
                            item_support_count[i] += 1
                        else:
                            item_support_count[i] = 1
                else:
                    if i in item_support_count:
                        item_support_count[i] += 1
                    else:
                        item_support_count[i] = 1
    fsReturn = {}
    rsReturn = []

    if item_support_count:
        print()
        for i in item_support_count:
            if (item_support_count[i] / counttot) * 100 >= min_supp:
                fsReturn[i] = item_support_count[i]
            else:
                rsReturn.append(set(list(i)))
        print()
        if fsReturn:
            itemprint(fsReturn, n, counttot)
            support_of_all_item_set.update(item_support_count)
            association_rules(fsReturn,support_of_all_item_set,mini_conf)
            return fsReturn, rsReturn
    return None, None
def itemprint(frequent_set: Dict[Tuple[str], int], n: int, counttot: int):
    print("Frequent itemsets", n, "iteration")
    for i in frequent_set:
        print(i, round(frequent_set[i] * 100 / counttot, 2))
    print()
from itertools import combinations
from typing import Dict, Tuple

def association_rules(frequent_set: Dict[Tuple[str], int], support_of_all_item_set: Dict[Tuple[str], int], min_conf: float):
    for items_set_tuple in frequent_set.keys():
        print("Association Rule for itemset -", items_set_tuple)
        size_of_item_set = len(items_set_tuple)
        itemset = set(items_set_tuple)
        while size_of_item_set - 1 > 0:
            comb = combinations(items_set_tuple, size_of_item_set - 1)
            for i in comb:
                left_side_items = i
                right_side_items = tuple(itemset - set(i))
                item_conf = round(support_of_all_item_set[items_set_tuple] * 100 / support_of_all_item_set[left_side_items], 2)
                if item_conf >= min_conf:
                    print(left_side_items, "=>", right_side_items, item_conf, "Rule Selected")
                else:
                    print(left_side_items, "=>", right_side_items, item_conf, "Rule Rejected")
            size_of_item_set -= 1
        print()


def bruteforce(file_name: str, min_supp: int, min_conf: int):
    global bfTime
    global mini_conf
    mini_conf=min_conf

    start_time=time.time()
    with open(file_name, "r") as file_object:
        reader = csv.reader(file_object)
        all_tx = []
        counttot = 0
        support_of_all_item_set = {}
        c1 = {}  
        item_set_list = []


        for row1 in reader:
            transaction_id = row1[0]
            items = row1[1].split(", ")
            all_tx.append(transaction_id)
            seen = set()
            for item in items:
                c1[(item,)] = c1.get((item,), 0) + 1
                seen.add(item)
            item_set_list.append(seen)
            counttot += 1

        frequent_set = {}
        rejected_set = []
        print()
        for i in c1:
            if (c1[i] / counttot) * 100 >= min_supp:
                frequent_set[i] = c1[i]
            else:
                rejected_set.append(set(i))
        support_of_all_item_set.update(c1)

        list1 = [item[0] for item in frequent_set.keys()]
        print()
        print(itemprint(frequent_set, 1, counttot))

        item_set_size = 1
        while len(list1) > item_set_size:
            frequent_set1, rejected_set1 = frequentset(
                list1, rejected_set, item_set_list, item_set_size + 1,
                min_supp, counttot, support_of_all_item_set
            )
            if not frequent_set1:
                break
            item_list = [items for item_tuples in frequent_set1.keys() for items in item_tuples]
            list1 = list(set(item_list))
            rejected_set = rejected_set1
            frequent_set = frequent_set1
            item_set_size += 1

        association_rules(frequent_set, support_of_all_item_set, min_conf)
        end_time= time.time()
        bfTime= end_time-start_time
        print(f"Time taken to complete the process using brute force method:{bfTime:.6f}")

def get_user_input():
    global choice, minimumSup, minimumConfi, file_name  

    print("Please select a dataset:")
    print("1. Juice Bar")
    print("2. Burlington")
    print("3. Costco")
    print("4. Walmart")
    print("5. ShopRite")

    choice = input("Enter the number corresponding to your choice: ")
    minimumSup = int(input("Enter minimum support as %: "))
    minimumConfi = int(input("Enter minimum confidence as %: "))

    file_names = {
        '1': 'juicebar.csv',
        '2': 'burlington.csv',
        '3': 'costco.csv',
        '4': 'walmart.csv',
        '5': 'shoprite.csv'
    }

    if choice in file_names:
        file_name = file_names[choice]
        print(f"You selected: {file_name}")
    else:
        print("Invalid choice. Please try again.")
        get_user_input()  

def run_analysis():
    global file_name, minimumSup, minimumConfi 
    bruteforce(file_name, minimumSup, minimumConfi)
get_user_input()

run_analysis()

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import time

def apriori_from_csv(file_name: str, minimumSup: float, minimumConfi: float):
    global aTime
    start_time=time.time()
    df = pd.read_csv(file_name, header=None)
    transactions = []
    for row in df.itertuples(index=False):
        transactions.append(row[1].split(", "))
    from mlxtend.preprocessing import TransactionEncoder
    encoder = TransactionEncoder()
    encoded_data = encoder.fit(transactions).transform(transactions)
    df = pd.DataFrame(encoded_data, columns=encoder.columns_)
    print(df)

    fi = apriori(df, min_support=minimumSup / 100, use_colnames=True)
    rules = association_rules(fi, metric="confidence", min_threshold=minimumConfi / 100)
    print("Frequent Itemsets:")
    print(fi)
    print("\nAssociation Rules:")
    print(rules)
    end_time= time.time()
    aTime= end_time-start_time
apriori_from_csv(file_name, minimumSup, minimumConfi)


def time_complexity():
    print(f"Brute Force Time: {bfTime:.6f} seconds")
    print(f"Apriori Time: {aTime:.6f} seconds")
    if bfTime < aTime:
        print("Brute Force is the fastest method.")
    elif aTime < bfTime:
        print("Apriori is the fastest method.")
    else:
        print("Both methods take approximately the same time.")
time_complexity()