from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime


cluster = MongoClient("mongodb+srv://admin:admin@cluster0.gadtl.mongodb.net/?retryWrites=true&w=majority")
db = cluster["tee"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:","")
    res = MessagingResponse()
    user = users.find_one({"number":number})
    if bool(user) == False:
        res.message("Hi, thanks for contacting *The Red Velvet*.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                    "To get our *address*")
        users.insert_one({"number":number, "status":"main","messages":[]})
    elif user["status"]== "main":
        try :
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            res.message("Response 1")
        elif option == 2:
            res.message("*ordering mode*")
            users.update_one({"number": number}, {"$set":{"status": "ordering"}})
            res.message("You can select one of the following cakes to order: \n\n1️⃣ Red Velvet  \n2️⃣ Dark Forest \n3️⃣ Ice Cream Cake"
                "\n4️⃣ Plum Cake \n5️⃣ Sponge Cake \n6️⃣ Genoise Cake \n7️⃣ Angel Cake \n8️⃣ Carrot Cake \n9️⃣ Fruit Cake  \n0️⃣ Go Back")
        elif option == 3:
            res.message("This is option 3")
        elif option == 4:
            res.message("This is *Option 4*")
        else:
            res.message("Please enter a valid responseee ")
            return str(res)

    elif user["status"] == "ordering":
        try :
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from one of the options below: "
                        "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                        "To get our *address*")
        elif 1 <= option <= 3 :
            cakes=["Red Velvet Cake","Dark Forest"," Ice Cream Cake"]
            selected = cakes[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})
            res.message("Excellent choice 😉")
            res.message("Please enter your address to confirm the order")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thanks for shopping with us!")
        res.message(f"Your order for {selected} has been received and will be delivered within an hour, Thank you")
        orders.insert_one({"number":number, "item": selected, "address": text,"order_time": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})

    elif user["status"] == "ordered":
        res.message("Hi, thanks for contacting again.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                    "To get our *address*")
        users.update_one({"number": number}, {"$set": {"status": "main"}})
        #res.message("I don't know what to say")
    users.update_one({"number":number},{"$push":{"messages":{"text":text, "date":datetime.now()}}})


    #msg = response.message(f"Thanks for contacting me. You have sent '{text}' from {number}")

    # msg.media("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimg.icons8.com%2Fcolor%2F452%2Fvalorant.png&f=1&nofb=1")
    return str(res)

if __name__ == "__main__":
    app.run()
