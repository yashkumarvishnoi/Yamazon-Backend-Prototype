from pymongo import MongoClient
import sys
from faker import Faker
import datetime

client=MongoClient("mongodb://localhost:27017/")
db=client["amazon"]
Product_catalogue=db["Products"]
products_list=db["Products"]
user_collection=db["Users"]
transactions_collection=db["Transactions"]
admin_collection=db["Admin"]


fake= Faker()
# Admin Performing operations and methods for admin to perform his duties.
def insert_data():
    data={}
    name= input("Enter the name of the product: ")
    product_id=int(input("Enter the unique product Id: "))
    price=float(input("Enter the price of the product:"))
    description=input("Describe the product (optional if not then type none): ")
    Units=0
    data['Name']=name
    data['Product Id']=product_id
    data['Price']=price
    data['Description']=description
    data['Units']=Units
    result1=Product_catalogue.insert_one(data)
    print("Document inserted with ID: ",result1.inserted_id)

def delete_data():
    op=input("Choose which way deletion will be performed(1: by ID,2: by Query,3: Delete all Data): ")
    if op == '1':
        doc_id=int(input("Enter the Product ID to delete: "))
        result2=Product_catalogue.delete_one({"Product Id":doc_id})
        print(result2.deleted_count," Documents Deleted")
    elif op == '2':
        field=input("Enter the field to query for deletion: ")
        value=input("Enter the value to match: ")
        query={field:value}
        result2=Product_catalogue.delete_many(query) 
        print(result2.deleted_count," Documents Deleted")  
    elif op == '3':
        result2=Product_catalogue.delete_many({})
        print(result2.deleted_count," number of documents deleted")     

def view_data():
    op1=input("Choose how to view data(1: All data,2: Selective document based query on id: ")
    if op1 == '1':
        # all_documents = Product_catalogue.find()
        # for document in all_documents:
        #     print(document)
        
        Products=products_list.find()
        for product in Products:
            print("===================================================================================================")
            print(f"Product Id: {product['Product Id']},\nProduct: {product['Name']},\nPrice: {product['Price']},\nUnits bought: {product['Units']},\nDescription: {product['Description']}"+"\n" )
            print("===================================================================================================")
    elif op1 == '2':
        field="Product Id"
        value=int(input("Enter the value to match: "))
        query = {field: value}
        filtered_documents = Product_catalogue.find(query)
        for document in filtered_documents:
            print("===================================================================================================")
            print(f"Product Id: {document['Product Id']},\nProduct: {document['Name']},\nPrice: {document['Price']},\nUnits bought: {document['Units']},\nDescription: {document['Description']}"+"\n" )
            print("===================================================================================================")
    else:
        print("Wrong Option chosen try again....:")
        view_data()
#     elif op1 == '3':
#         field=input("Enter the field to query for deletion: ")
#         value=(input("Enter the value to match: "))
#         query = {field: value} 
#         filtered_documents = Product_catalogue.find(query)
#         for document in filtered_documents:
#             print(document)
# # All these methods are to be performed by the user all functionalities of user are included

def view_products():
    Products=products_list.find()
    for product in Products:
        print(f"Product Id: {product['Product Id']},Product: {product['Name']},Price: {product['Price']}")


def choose_products():
     id=(input("Enter the Product Id of the product you want to select by comma seperated value:-"))
     id_li=id.split(',')
     id_list = [int(x) for x in id_li]
     return id_list

def select_products(choosen_id):
     selected_products=[]
     for product_id in choosen_id:
          product=products_list.find_one({"Product Id": product_id})
          if product:
               selected_products.append(product)
          else:
               print(f"Product with ID {product_id} not found") 
     return selected_products               


def buy_products(user_id, selected_products):
    total_cost = sum(product['Price'] for product in selected_products)
    transaction_id = fake.unique.random_number(digits=3)
    current_date = datetime.datetime.combine(datetime.date.today(), datetime.time())  # Get the current datetime
    
    transaction = {
        "Transaction_id": transaction_id,
        "User_id": user_id,
        "Products": selected_products,
        "Total_cost": total_cost,
        "Transaction_date": current_date  # Add the current date to the transaction
    }
    
    transactions_collection.insert_one(transaction)
    print("===================================================================================================")
    print("Payment Receipt:---")
    print(f"Transaction id: {transaction_id},")
    print(f"User id: {user_id},")
    # Assuming selected_products is a list of dictionaries
    for product in selected_products:
        
        print(f"Product Id: {product['Product Id']},")
        print(f"Products name: {product['Name']},")
        print(f"Product Price: {product['Price']},")
    print(f"Total Billing Amount: {total_cost}")
    print("--------------------------------------------------------------------------------------------------")

    print("Transaction completed. Thank you for your purchase!")
    print("===================================================================================================")

def increment_units(prod):
    unit=prod['Units']
    prod_id=prod['Product Id']
    
    # Find the product by its Product Id and update the Units field
    new_unit=unit+1
    
    Product_catalogue.update_one(
        {"Product Id": prod_id},{"$set":{"Units": new_unit}}
    )

     

def login():
    print("===================================================================================================")
    username=input("Enter your username: ")
    password=input("Enter your password: ") 
    user = user_collection.find_one({"Username": username, "Password": password})
    if user:
        print("Login successful.")
        return True
    else:
        print("-----------------------------------------------------------------------------------------------")
        print("Invalid username or password.")
        print("Please try again ..\n1: Retry\nAny other key: Exit")
        tr=int(input("Make a choice: "))
        print("-----------------------------------------------------------------------------------------------")
        if tr == 1:
            login()


        else:
            sys.exit()    
        return False
    
def shop():
    print("-----------------------------------------------------------------------------------------------")
    user_id=int(input("Provide your User Id for payment: "))
    if user_collection.find_one({"User Id": user_id}):
        view_products()
        choosen_id=choose_products()
        selected_products=select_products(choosen_id)
        if selected_products:
            for prod in selected_products:
                increment_units(prod)
        
    
            buy_products(user_id,selected_products)
        else:
            print("No products selected. Returning to shopping.")
            shop()    
    else:
        print("-----------------------------------------------------------------------------------------------")
        print("Entered user id does not exist try again...")
        shop()

    print("Done with Shopping so soon!!!\n1: Wanna continue shopping\n2: Nope Done for the day")
    ch=input("Provide your choice: -")
    print("-----------------------------------------------------------------------------------------------")
    if ch == '1':
        shop()
    else:
        return
    
def register():
    print("===================================================================================================")
    name=input("Enter your name: ")
    user_id=int(input("Create your User id(Will be unique): "))
    email=input("Provide your E-mail for contact: ")
    ph=int(input("Enter phone number for contact: "))
    username=input("Create your username: ")
    password=input("Create password: ")
    print("===================================================================================================")
    if user_collection.find_one({"Username": username}):

        print("Username already exists!! Please choose a different username ")
        print("-----------------------------------------------------------------------------------------------")
        register()
        return False
    elif user_collection.find_one({"User Id": user_id}):
        print("User Id needs to be unique use another")
        print("-----------------------------------------------------------------------------------------------")
        register()
        return False
    else:
        user_collection.insert_one({"Name": name,"User Id": user_id,"Email": email,"Phone number": ph,"Username": username,"Password": password})
        print("Registration successfull!! You are now a Yamazon member")
        print("===================================================================================================")
        return True
    


def user():
    print("===================================================================================================")
    print("As a user please confirm your action: ")
    print("1: Already a member, Login to Yamazon:-")
    print("2: Not a member yet, Sign Up:-")
    print("3: Shopping done Exit!!:-")
    
    c=input("Your choice: ")
    print("-----------------------------------------------------------------------------------------------")
    if c == '1':
        login()
        shop()
    elif c == '2':
        register()
        shop()
    elif c == '3':
        sys.exit()
    else:
        print("-----------------------------------------------------------------------------------------------")
        print("Wrong choice entered")
        print("-----------------------------------------------------------------------------------------------")

def analysis_bymonth(target_month,target_year):
    start_date = datetime.datetime(target_year, target_month, 1)
    count=0
    if target_month == 12:
        end_date = datetime.datetime(target_year + 1, 1, 1)
    else:
        end_date = datetime.datetime(target_year, target_month + 1, 1)
    start_datetime = datetime.datetime.combine(start_date,  datetime.time())
    end_datetime = datetime.datetime.combine(end_date,  datetime.time())
    # print(start_datetime)
    # print(end_datetime)
    query = {"Transaction_date": {"$gte": start_datetime, "$lt": end_datetime}}
    cursor = transactions_collection.find(query)
    for transaction in cursor:
        count=count+1
        print("\nTransaction Details:")
        print("Transaction ID:", transaction.get("Transaction_id"))
        print("User Id:", transaction.get("User_id"))
        print("Total cost:", transaction.get("Total_cost"))
        products = transaction.get("products", [])
        print("Transaction date:", transaction.get("Transaction_date"))
        print("Products:")
        for product in products:
            print("\tProduct Name:", product.get("Name"))
            print("\tProduct Id:", product.get("Product_id"))
            print("\tPrice:", product.get("Price"))
            print("\tProduct Id:", product.get("Product_id"))
            
    print(f"Total Transactions in {start_date} are :-",count)
    print("===================================================================================================")

def analysis_bydate(target_date,target_month,target_year):
    start_date = datetime.datetime(target_year, target_month, target_date)
    count=0
    if target_date == 30:
        end_date = datetime.datetime(target_year, target_month + 1, 1)
    elif target_date == 30 and target_month == 12:
        end_date = datetime.datetime(target_year + 1, 1, 1)
    else:
        end_date = datetime.datetime(target_year, target_month , target_date +1)
    start_datetime = datetime.datetime.combine(start_date,  datetime.time())
    end_datetime = datetime.datetime.combine(end_date,  datetime.time()) 
    query = {"Transaction_date": {"$gte": start_datetime, "$lt": end_datetime}}
    cursor = transactions_collection.find(query)
    for transaction in cursor:
        count=count+1
        print("\nTransaction Details:")
        print("Transaction ID:", transaction.get("Transaction_id"))
        print("User Id:", transaction.get("User_id"))
        print("Total cost:", transaction.get("Total_cost"))
        products = transaction.get("products", [])
        print("Transaction date:", transaction.get("Transaction_date"))
        print("Products:")
        for product in products:
            print("\tProduct Name:", product.get("Name"))
            print("\tProduct Id:", product.get("Product_id"))
            print("\tPrice:", product.get("Price"))
            print("\tProduct Id:", product.get("Product_id"))
            
    print(f"Total Transactions in {start_date} are :-",count)
    print("===================================================================================================")

def analysis_byyear(target_year):
    start_date = datetime.datetime(target_year, 1, 1)
    count=0
    end_date = datetime.datetime(target_year + 1, 1, 1)
    start_datetime = datetime.datetime.combine(start_date,  datetime.time())
    end_datetime = datetime.datetime.combine(end_date,  datetime.time()) 
    query = {"Transaction_date": {"$gte": start_datetime, "$lt": end_datetime}}
    cursor = transactions_collection.find(query)
    for transaction in cursor:
        count=count+1
        print("\nTransaction Details:")
        print("Transaction ID:", transaction.get("Transaction_id"))
        print("User Id:", transaction.get("User_id"))
        print("Total cost:", transaction.get("Total_cost"))
        products = transaction.get("products", [])
        print("Transaction date:", transaction.get("Transaction_date"))
        print("Products:")
        for product in products:
            print("\tProduct Name:", product.get("Name"))
            print("\tProduct Id:", product.get("Product_id"))
            print("\tPrice:", product.get("Price"))
            print("\tProduct Id:", product.get("Product_id"))
            
    print(f"Total Transactions in {start_date} are :-",count)
    print("===================================================================================================")



def analysis_overall():
    count=0
    transac=transactions_collection.find()
    for tran in transac:
        count=count+1
        count=count+1
        print("\nTransaction Details:")
        print("Transaction ID:", tran.get("Transaction_id"))
        print("User Id:", tran.get("User_id"))
        print("Total cost:", tran.get("Total_cost"))
        products = tran.get("products", [])
        print("Transaction date:", tran.get("Transaction_date"))
        print("Products:")
        for product in products:
            print("\tProduct Name:", product.get("Name"))
            print("\tProduct Id:", product.get("Product_id"))
            print("\tPrice:", product.get("Price"))
            print("\tProduct Id:", product.get("Product_id"))
            
    print("Total Number of transactions:- ",count)
    print("===================================================================================================")

def most_sold():
    pipeline = [
        {"$group": {"_id": "$Product Id", "total_sold": {"$sum": "$Units"}}},
        {"$sort": {"total_sold": -1}},
        {"$limit": 1}
    ]
    result = list(Product_catalogue.aggregate(pipeline))
    if result:
        most_sold_product = result[0]
        product_id = most_sold_product["_id"]
        total_sold = most_sold_product["total_sold"]
        print(f"The most sold product is Product Id: {product_id}, Total Sold: {total_sold}")
        print("===================================================================================================")
    else:
        print("-----------------------------------------------------------------------------------------------")
        print("No products found")
        print("-----------------------------------------------------------------------------------------------")

def least_sold():
    pipeline = [
        {"$group": {"_id": "$Product Id", "total_sold": {"$sum": "$Units"}}},
        {"$sort": {"total_sold": 1}},
        {"$limit": 1}
    ]
    result = list(Product_catalogue.aggregate(pipeline))
    if result:
        most_sold_product = result[0]
        product_id = most_sold_product["_id"]
        total_sold = most_sold_product["total_sold"]
        print(f"The least sold product is Product Id: {product_id}, Total Sold: {total_sold}")
        print("===================================================================================================")
    else:
        print("-----------------------------------------------------------------------------------------------")
        print("No products found")
        print("-----------------------------------------------------------------------------------------------")

def analysis():
    print("===================================================================================================")
    print("Choose which of the following parameters on basis of which analysis needs to be performed:-")    
    print("1: Transactions performed in specific month")    
    print("2: Total Transactions performed Overall")   
    print("3: Transactions performed on a specific date")   
    print("4: Transactions performed in specific year")   
    print("5: Find the most Sold product")   
    print("6: Find the least sold product")   
    ac=input("Choose the parameters:-")
    print("-----------------------------------------------------------------------------------------------")
    if ac == '1':
        target_month = int(input("Enter month (MM): "))
        target_year = int(input("Enter year (YYYY): "))
        analysis_bymonth(target_month,target_year) 
    elif ac == '2':
        analysis_overall()
    elif ac == '3':
        target_date=int(input("Enter date (DD): "))
        target_month = int(input("Enter month (MM): "))
        target_year = int(input("Enter year (YYYY): "))
        analysis_bydate(target_date,target_month,target_year)
    elif ac == '4':
        target_year = int(input("Enter year (YYYY): "))
        analysis_byyear(target_year)  
    elif ac == '5':
        most_sold()
    elif ac == '6':
        least_sold()              
    else:
        print("No other parameter available")


def view_profile():
    user_profile=user_collection.find()
    for user in user_profile:
        print(f"Name: {user['Name']},User Id: {user['User Id']},Phone Number: {user['Phone number']},Username: {user['Username']},Email: {user['Email']}")
        print("===================================================================================================")

def admin_login():
    print("===================================================================================================")
    username=input("Enter your username: ")
    password=input("Enter your password: ")
    user = admin_collection.find_one({"Username": username, "Password": password})
    print("-----------------------------------------------------------------------------------------------")
    if user:
        print("-----------------------------------------------------------------------------------------------")
        print("Login successful.")
        print("-----------------------------------------------------------------------------------------------")
        return True
    else:
        print("-----------------------------------------------------------------------------------------------")
        print("Invalid username or password.")
        print("Please Try again later...")
        print("-----------------------------------------------------------------------------------------------")
        admin_login()
        return False
    


               

# def login():
def admin_start():
    while True:
        print("===================================================================================================")
        print("\n Menu :")
        print("1: Insert data")
        print("2: Delete data")
        print("3: View Document")
        print("4: Perform Analysis")
        print("5: View all Users")
        print("6: Exit")

        ch=input("Enter your choice: ")
        print("-----------------------------------------------------------------------------------------------")
        if ch == '1':
            insert_data()
        elif ch == '2':
            delete_data()
        elif ch == '3':
            view_data()
        elif ch =='4':
            analysis()
        elif ch == '5':
            view_profile()
        elif ch == '6':
            sys.exit()    
        else: 
            print("Invalid Choice")
            print("===================================================================================================")




while True:
    print("===================================================================================================")
    print("Welcome to Yamazon: A destination for all your shopping endeavours")          
    print("To start your journey please confirm which customer you are:- ")          
    print("1: Customer")                  
    print("2: Admin Login")          
    print("3: Exit!! Wrong platform")          
    choice=input("Please select your choice: ")
    print("-----------------------------------------------------------------------------------------------")
    if choice == '1':
        user()
    elif choice == '2':
        admin_login()
        admin_start()
    elif choice == '3':
        break
    else:
        print("Invalid Choice")                
        print("===================================================================================================")
          
                    

    

