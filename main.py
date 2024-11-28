import pandas as pd #will allow to load in the CSV file and easily work with it
from datetime import datetime
import csv #acts as the database
from data_entry import get_date, get_amount, get_category, get_description
import matplotlib.pyplot as plt


class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS) #DataFrame is an object in Pandas that allows for easy access of rows and columns from something like a CSV file
            df.to_csv(cls.CSV_FILE, index=False) #saves the dataframe created above as a CSV file to the same directory as the python file

    @classmethod
    def add_entry(cls, date, amount, category, description):
        #dictionary for all the data
        new_entry = {
            "date": date, 
            "amount": amount, 
            "category": category, 
            "description": description
        }
        with open(cls.CSV_FILE, "a", newline="") as csvfile:  #context manager - for opening the file for entering data and closing the file right after to prevent data leaks, a for append
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        print("Entry added successfully.")
        
    @classmethod
    def search_entry(cls, column, value):
        # Search entries by a specified column and value
        df = pd.read_csv(cls.CSV_FILE)
        if column == "date":
            df["date"] = pd.to_datetime(df["date"], format=cls.FORMAT)
            value = datetime.strptime(value, cls.FORMAT)
        
        mask = df[column] == value
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print(f'No transactions found with {column} = "{value}".')
            main()
        else:
            print(f"Transaction(s) found with {column} = {value}:")
            print(filtered_df.to_string(index=True, formatters={"date": lambda x: x.strftime(cls.FORMAT)}))
        
        return filtered_df

    @classmethod
    def edit_entry(cls, filtered_df):
        df = pd.read_csv(cls.CSV_FILE)

        index_map = {i+1: original_idx for i, original_idx in enumerate(filtered_df.index)}        

        filtered_df = filtered_df.reset_index(drop=True)
        filtered_df.index += 1

        choice = input(f"Choose the row number to edit (1-{filtered_df.index[-1]}): ")
        print(filtered_df.to_string(index=True))

        if choice.isdigit() and int(choice) in index_map:
            actual_index = index_map[int(choice)]            
            choice = input(f"Select column to edit ({cls.COLUMNS}): ")
            if choice in cls.COLUMNS:
                df = df.set_value(actual_index, choice, input("Enter value: "))
            else:
                print(f"Invalid input. Please select one of these columns {cls.COLUMNS}: ")
                cls.edit_entry(filtered_df)
        else:
            print(f"Invalid choice. Please select between 1-{filtered_df.index[-1]}")
            cls.edit_entry(filtered_df)
            

    @classmethod
    def delete_entry(cls, filtered_df):
        """Delete rows from CSV that match those in filtered_df, using a mapped index for readability."""
        # Load the entire CSV into a DataFrame
        df = pd.read_csv(cls.CSV_FILE)       
        
        # Create a mapping of readable indices to the actual DataFrame indices
        index_map = {i+1: original_idx for i, original_idx in enumerate(filtered_df.index)}
        
        # Reset index for filtered_df to display 1-based numbered list
        filtered_df = filtered_df.reset_index(drop=True)
        filtered_df.index += 1  # Make it start from 1 for readability

        # Ask for deletion choice
        choice = input("Choose the row number to delete or type 'all' to delete all matches: ")
        print(filtered_df.to_string(index=True))

        if choice.lower() == 'all':
            # Delete all rows in filtered_df from the main DataFrame
            df = df.drop(index=filtered_df.index)
            print("All matching transactions deleted.")
        elif choice.isdigit() and int(choice) in index_map:
            # Delete the specific row chosen by the user
            df = df.drop(index=index_map[int(choice)])
            print("Selected transaction deleted.")
        else:
            print("Invalid choice. No deletion performed.")
            return

        # Save the updated DataFrame back to the CSV file
        df.to_csv(cls.CSV_FILE, index=False)
        print("CSV file updated.")


    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)
        start_date = datetime.strptime(start_date, CSV.FORMAT)
        end_date = datetime.strptime(end_date, CSV.FORMAT)
        
        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print('No transactions found in the given date range.')
        else:
            print(f"Transactions from {start_date.strftime(CSV.FORMAT)} to {end_date.strftime(CSV.FORMAT)}")
            print(filtered_df.to_string(index=False, formatters={"date": lambda x: x.strftime(CSV.FORMAT)}))
        

            total_income = filtered_df[filtered_df["category"] == "Income".lower()]["amount"].sum()
            total_expense = filtered_df[filtered_df["category"] == "Expense".lower()]["amount"].sum()
            print("\nSummary:")
            print(f"Total Income: ${total_income:.2f}")
            print(f"Total Expense: ${total_expense:.2f}")
            print(f"Net Savings: ${(total_income - total_expense):.2f}")
        
        return filtered_df
    


def add():
    CSV.initialize_csv()
    date = get_date("Enter the date of the transaction (dd-mm-yyyy) you want to add or enter for today's date: ", allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)

def delete(column, value):
    filtered_df = CSV.search_entry(column, value)
    if filtered_df == 0:
        return
    else:    
        choice = input("Delete transaction/s? (y/n): ").lower()
        if choice == "y":
            CSV.delete_entry(filtered_df)

def edit(column, value):
    filtered_df = CSV.search_entry(column, value)
    choice = input("Edit transaction/s? (y/n): ").lower()
    if choice == "y":
        CSV.edit_entry(filtered_df)

def search():
    print("1. View transactions and summary within a date range \n2. Search transaction \n3. Main Menu")
    choice = input("Enter your choice (1-3): ")
    if choice == "1":
        start_date = input("Enter the start date (dd-mm-yyyy): ")
        end_date = input("Enter the end date (dd-mm-yyyy): ")
        df = CSV.get_transactions(start_date, end_date)

        choice == input("(1) Plot transactions or go back to (2) Main Menu: ")
        if choice == "2":
            main()
        elif choice == "1":
            plot_transactions(df)
        else:
            print("Invalid choice.")

    elif choice == "2":
        column = input("Enter the column to search by (date, amount, category, description): ")
        value = input(f"Enter the value to search for in {column}: ")
        CSV.search_entry(column, value)
        choice == input("\n1. Edit transaction(s) \n2. Delete transaction(s) \n3. Back to Search \n4. Main Menu \nEnter choice (1-4): ")
        if choice == "1":
            edit()
        elif choice == "2":
            CSV.delete_entry()
        elif choice == "3":
            search()
        elif choice == "4":
            main()
    elif choice == "3":
        main()
    else:
        print("Invalid choice.")
        search()

def plot_transactions(df):
    df.set_index("date", inplace=True)

    income_df = df[df["category"] == "Income"].resample("D").sum().reindex(df.index, fill_value=0)
    expense_df = df[df["category"] == "Expense"].resample("D").sum().reindex(df.index, fill_value=0)

    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income".lower(), color="g")
    plt.plot(expense_df.index, expense_df["amount"], label="Expense".lower(), color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title('Income and Expenses Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    while True:
        print("\n1. Add a new transaction")
        print("2. Search transaction(s)")
        print("3. Edit a transaction")
        print("4. Delete a transaction")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            add()
        if choice == "2":
            search()
        if choice == "3":
            column = input("Enter the column to search by (date, amount, category, description): ")
            value = input(f"Enter the value to search for in {column}: ")
            edit(column, value)
        elif choice == "4":
            column = input("Enter the column to delete by (date, amount, category, description): ")
            value = input(f"Enter the value to delete for in {column}: ")
            delete(column, value)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Enter a number between 1 and 4.")


if __name__ == "__main__":
    main()




