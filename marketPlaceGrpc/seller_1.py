import grpc
import uuid
import market_pb2
import market_pb2_grpc
from threading import Thread
import concurrent.futures
from collections import defaultdict
import Buyer_pb2
import Buyer_pb2_grpc

Notifications = []

class SellerNotification:
    def Notification_Print(self, request, context):
        print(f"\n Notification Received: {request.Notification}")
        response = Buyer_pb2.NotificationResponse()
        response.status = Buyer_pb2.NotificationResponse.Status.SUCCESS
        Notifications.append(request.Notification)
        return response

class SellerClient:
    def __init__(self, market_address, seller_address):
        # Initialize gRPC channel with the market address
        self.market_channel = grpc.insecure_channel(market_address)
        # Initialize stub for market
        self.market_stub = market_pb2_grpc.MarketStub(self.market_channel)
        # Seller's address
        self.seller_address = seller_address
        # Generate and maintain a UUID for the seller
        self.seller_uuid = str(uuid.uuid1())

    def register_seller(self):
        # Register the seller with the market
        request = market_pb2.RegisterSellerRequest(address=self.seller_address, uuid=self.seller_uuid)
        response = self.market_stub.RegisterSeller(request)
        if response.status != 0:
            self.seller_uuid = response.uuid
        return response

    def sell_item(self, product_name, category, quantity, description, price_per_unit):
        # Sell an item on the market
        request = market_pb2.SellItemRequest(
            address=self.seller_address,
            uuid=self.seller_uuid,
            product_name=product_name,
            category=category,
            quantity=quantity,
            description=description,
            price_per_unit=price_per_unit
        )
        response = self.market_stub.SellItem(request)
        return response

    def update_item(self, item_id, new_price, new_quantity):
        # Update item details on the market
        request = market_pb2.UpdateItemRequest(
            address=self.seller_address,
            uuid=self.seller_uuid,
            item_id=item_id,
            new_price=new_price,
            new_quantity=new_quantity

        )
        response = self.market_stub.UpdateItem(request)
        return response

    def delete_item(self, item_id):
        # Delete an item from the market
        request = market_pb2.DeleteItemRequest(item_id=item_id, seller_uuid=self.seller_uuid, address=self.seller_address)
        response = self.market_stub.DeleteItem(request)
        return response

    def display_seller_items(self):
        # Display items of the seller on the market
        request = market_pb2.DisplaySellerItemsRequest(seller_uuid=self.seller_uuid, address = self.seller_address)
        response = self.market_stub.DisplaySellerItems(request)
        return response      

    def receive_notification(self, context = None):
        # Method to receive notifications from the market
        server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
        Buyer_pb2_grpc.add_BuyerServicer_to_server(SellerNotification(), server)
        server.add_insecure_port(f'{self.seller_address}')  # Market service port remains 50051
        server.start()
        server.wait_for_termination()
        # print("Received notification:", request.notification)

def menu():
    print("Menu:")
    print("1. Register Seller")
    print("2. Sell Item")
    print("3. Update Item")
    print("4. Delete Item")
    print("5. Display Seller Items")
    print("6. Notifications")
    print("7. Exit")
    choice = input("Enter your choice: ")
    return choice

if __name__ == '__main__':
    market_address = input("Enter market address:")  # Address of the market server
    seller_address = input("Enter seller address:")
    seller_client = SellerClient(market_address, seller_address)
    Thread(target=seller_client.receive_notification).start()
    seller_uuid = seller_client.seller_uuid  # Generate a random UUID for the seller


    choice = None
    while choice != '7':
        choice = menu()
        if choice == '1':
            response = seller_client.register_seller()
            print("Received RegisterSeller response:", response.status==0)
        elif choice == '2':
            product_name = input("Enter product name: ")
            category = input("Enter category: ")
            quantity = int(input("Enter quantity: "))
            description = input("Enter description: ")
            price_per_unit = float(input("Enter price per unit: "))
            sell_response = seller_client.sell_item(product_name, category, quantity, description, price_per_unit)
            print(f"Received SellItem response: {sell_response.status==0}\nItem ID assigned: {sell_response.item_id}")
        elif choice == '3':
            item_id = input("Enter item ID to update: ")
            new_price = float(input("Enter new price: "))
            new_quantity = int(input("Enter new quantity: "))
            update_response = seller_client.update_item(item_id, new_price, new_quantity)
            print("Received UpdateItem response:", update_response.status==0)
        elif choice == '4':
            item_id = input("Enter item ID to delete: ")
            delete_response = seller_client.delete_item(item_id)
            print("Received DeleteItem response:", delete_response.status==0)
        elif choice == '5':
            display_response = seller_client.display_seller_items()
            print("Received DisplaySellerItems response:", display_response.status == 0)
            itemss = display_response.items.split("\n")
            itemss.pop(-1)
            items_dict = []
            for i in itemss:
                temp = i.split("\t")
                # for j in temp:
                temp_dict = {}
                temp_dict["Item ID"] = temp[0]
                temp_dict['Product Name'] = temp[1]
                temp_dict['Category'] = temp[2]
                temp_dict['Quantity'] = temp[3]
                temp_dict['Description'] = temp[4]
                temp_dict['Price per unit'] = temp[5]
                temp_dict['Rating'] = temp[6]
                items_dict.append(temp_dict)
            
            counter = 1
            for alpha in items_dict:
                print()
                print(counter)
                counter += 1
                for item_idd, item_infoo in alpha.items():
                    print(f"{item_idd}: {item_infoo}")

            print()        
                
        elif choice == '6':
            print("Following are the received Notifications")
            for i in range(len(Notifications)):
                print(f"{i + 1}) {Notifications[i]}")

        elif choice == '7':
            print("Exiting...")
        else:
            print("Invalid choice. Please enter a number from 1 to 7.")
