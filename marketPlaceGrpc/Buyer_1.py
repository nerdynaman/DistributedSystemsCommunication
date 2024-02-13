'''
The buyer interacts with the market to search for products and buy them. 
Buyers can also wishlist a product to receive notifications from the Market whenever the seller updates their wish-listed product 
(this scenario simulates the pub-sub pattern).
'''
import grpc
import market_pb2
import market_pb2_grpc
from threading import Thread
import concurrent.futures
from collections import defaultdict
import Buyer_pb2
import Buyer_pb2_grpc

Notifications = []

class BuyerNotification:
    def Notification_Print(self, request, context):
        print(f"\n Notification Received: {request.Notification}")
        response = Buyer_pb2.NotificationResponse()
        response.status = Buyer_pb2.NotificationResponse.Status.SUCCESS
        Notifications.append(request.Notification)
        return response


class BuyerClient:
    def __init__(self, market_address, Buyer_address):
        # Initialize gRPC channel with the market address
        self.market_channel = grpc.insecure_channel(market_address)
        # Initialize stub for market server
        self.market_stub = market_pb2_grpc.MarketStub(self.market_channel)
        # Notification server address for the current buyer
        self.Buyer_address = Buyer_address

    def search_item(self, item_name="", category="ANY"):
        # Search for items on the market
        request = market_pb2.SearchItemRequest(item_name=item_name, category=category)
        response = self.market_stub.SearchItem(request)
        return response

    def buy_item(self, item_id, quantity):
        # Buy an item from the market
        request = market_pb2.BuyItemRequest(item_id=item_id, quantity=quantity, buyer_address=self.Buyer_address)
        response = self.market_stub.BuyItem(request)
        return response

    def add_to_wishlist(self, item_id):
        # Add an item to wishlist
        request = market_pb2.AddToWishlistRequest(item_id=item_id, buyer_address=self.Buyer_address)
        response = self.market_stub.AddToWishlist(request)
        return response

    def rate_item(self, item_id, rating):
        # Rate an item
        request = market_pb2.RateItemRequest(item_id=item_id, buyer_address=self.Buyer_address, rating=rating)
        response = self.market_stub.RateItem(request)
        return response

    def get_Buyer_address(self):
        # Return notification server address for the current buyer
        return self.Buyer_address

    def receive_notification(self, context = None):
        # Method to receive notifications from the market
        server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
        Buyer_pb2_grpc.add_BuyerServicer_to_server(BuyerNotification(), server)
        server.add_insecure_port(f'{self.Buyer_address}')  # Market service port remains 50051
        server.start()
        server.wait_for_termination()
        # print("Received notification:", request.notification)



def add_to_wishlist(buyer_client):
    # Add item to wishlist
    item_id = input("Enter item ID:")
    response = buyer_client.add_to_wishlist(item_id)
    print("Received AddToWishlist response:", response.status == 0)

def menu():
    print("Menu:")
    print("1. Search for items")
    print("2. Buy an item")
    print("3. Add an item to wishlist")
    print("4. Rate an item")
    print("5. Notifications")
    print("6. Exit")

    choice = input("Enter your choice: ")
    return choice

def search_item(buyer_client):
    item_name = input("Enter item name (leave blank for any): ")
    category = input("Enter category (leave blank for any): ")
    response = buyer_client.search_item(item_name=item_name, category=category)
    print("Received SearchItem response:")
    for item in response.items:
        print("Item ID:", item.item_id)
        print("Price:", item.price_per_unit)
        print("Name:", item.product_name)
        print("Category:", item.category)
        print("Description:", item.description)
        print("Quantity Remaining:", item.quantity)
        print("Rating:", item.rating)
        print("Seller:", item.seller_address)
        print()

def buy_item(buyer_client):
    item_id = input("Enter item ID: ")
    quantity = int(input("Enter quantity: "))
    response = buyer_client.buy_item(item_id, quantity)
    print("Received BuyItem response:", response.status == 0)

def rate_item(buyer_client):
    item_id = input("Enter item ID: ")
    rating = int(input("Enter rating (1-5): "))
    response = buyer_client.rate_item(item_id, rating)
    print("Received RateItem response:", response.status == 0)

if __name__ == '__main__':
    market_address = input("Enter market address:")
    self_address = input("Enter buyer address:")
    buyer_client = BuyerClient(market_address, self_address)
    Thread(target=buyer_client.receive_notification).start()
    choice = None
    while choice != '6':
        choice = menu()
        if choice == '1':
            search_item(buyer_client)
        elif choice == '2':
            buy_item(buyer_client)
        elif choice == '3':
            add_to_wishlist(buyer_client)
        elif choice == '4':
            rate_item(buyer_client)
        elif choice == '5':
            print("Following are the received Notifications")
            for i in range(len(Notifications)):
                print(f"{i + 1}) {Notifications[i]}")
        elif choice == '6':
            print("Exiting...")
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")
