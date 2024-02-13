'''
It maintains all the seller accounts, the items they sell, quantity, transaction logs, reviews, and so on. 
The central platform is also responsible for sending out notifications to buyers in cases where the seller updates an item, 
and sellers receive notifications when someone buys their products.
'''


#Notification System


import grpc
import uuid
import Buyer_pb2
import Buyer_pb2_grpc
import market_pb2
import market_pb2_grpc
import concurrent.futures
from collections import defaultdict 

# gRPC server implementation for the Market
registered_sellers = {}  # Store registered sellers' addresses and UUIDs
seller_items = {}  # Store items listed by each seller
transaction_logs = []  # Store transaction logs
buyer_wishlist = {}  # Store buyer's wishlist for notifications
rating_dict = {}

# gRPC server implementation for the Market
class MarketServicer(market_pb2_grpc.MarketServicer):
    def RegisterSeller(self, request, context):
        # Process RegisterSeller request
        print(f"Received!\nSeller join request received from {request.address}")

        # Process request and return response
        response = market_pb2.RegisterSellerResponse()
        if request.address not in registered_sellers:
            registered_sellers[request.address] = request.uuid
            seller_items[request.address] = {}
            response.status = market_pb2.RegisterSellerResponse.Status.SUCCESS
        else:
            response.uuid = registered_sellers[request.address]
            response.status = market_pb2.RegisterSellerResponse.Status.FAILED
        if response.status == 0:
            print(f"Accepted!\nSeller join request accepted from {request.address}")
        else:
            print(f"Rejected!\nSeller join request rejected from {request.address} as it's already connected.")
        return response

    def SellItem(self, request, context):
        # Process SellItem request
        print(f"Sell Item request from {request.address}")

        # Process request and return response
        response = market_pb2.SellItemResponse()
        if request.address in registered_sellers:
            item_id = str(uuid.uuid4())
            item_details = {
                "Product Name": request.product_name,
                "Category": request.category,
                "Quantity": request.quantity,
                "Description": request.description,
                "Price per unit": request.price_per_unit,
                "Seller Address": request.address,
                "Seller UUID": request.uuid,
                "Item ID": item_id,
                "Rating": 0
            }
            seller_items[request.address][item_id] = item_details
            response.status = market_pb2.SellItemResponse.Status.SUCCESS
            response.item_id = item_id
        else:
            response.status = market_pb2.SellItemResponse.Status.FAILED

        print(f"Sending Sell Item response to request from {request.address}: {response.status}")
        # print(seller_items)
        return response

    def BuyItem(self, request, context):
        # Process BuyItem request
        print("Received BuyItem request:", request)

        # Process request and return response
        response = market_pb2.BuyItemResponse()
        item_id = request.item_id
        quantity = request.quantity
        buyer_id = request.buyer_address

        # if item_id in buyer_wishlist and buyer_id in buyer_wishlist[item_id]:
        #     # Item is in wishlist, notify buyer
        #     response.notification = f"Item {item_id} is in your wishlist. It's now available for purchase."
        #     del buyer_wishlist[item_id][buyer_id]
        seller_found = False
        # print(1)
        selleesss = 0
        # print(seller_items.items())
        # print()
        # print(seller_items)
        for selll, itemm in seller_items.items():
            # print(2)
            if item_id in itemm:
                    # print(3)
                    selleesss = selll
                    item = itemm[item_id]
                    # print(item["Quantity"], type(item["Quantity"]))
                    # print(quantity, type(quantity))
                    if item["Quantity"] >= quantity:
                        seller_found = True
                        # print(4)
                        # Update item quantity
                        item["Quantity"] -= quantity
                        # Add transaction log
                        transaction_logs.append({
                            "Item ID": item_id,
                            "Quantity": quantity,
                            "Buyer ID": buyer_id,
                            "Seller Address": selll
                        })
                        response.status = market_pb2.BuyItemResponse.Status.SUCCESS
                        break
                    else:
                        response.status = market_pb2.BuyItemResponse.Status.FAILED
        if not seller_found:
            response.status = market_pb2.BuyItemResponse.Status.ITEM_NOT_AVAILABLE
        if seller_found:
            self.NotifySellers(item_id, buyer_id, quantity, selleesss)
        print("Sending BuyItem response:", response.status == 0)
        return response

    def AddToWishlist(self, request, context):
        # Process AddToWishlist request
        print("Received AddToWishlist request:", request)

        # Process request and return response
        response = market_pb2.AddToWishlistResponse()
        item_id = request.item_id
        buyer_address = request.buyer_address

        response.status = market_pb2.AddToWishlistResponse.Status.ITEM_NOT_AVAILABLE
        for sellls in seller_items.values():
            # print(1)
            if item_id in sellls:
                # print(2)
                if item_id not in buyer_wishlist:
                    buyer_wishlist[item_id] =[]
                buyer_wishlist[item_id].append(buyer_address)
                # print(3)
                response.status = market_pb2.AddToWishlistResponse.Status.SUCCESS
                # print(4)
                break

        print("Sending AddToWishlist response:", response.status == 0)
        return response

    def NotifySellers(self, item_id, buyer_id, quantity, seller_id):
        Info = f"{buyer_id} has bought {quantity} nos of {item_id}."
        # print(Info)
        # print(1)
                # print(3)
        buyer_channel = grpc.insecure_channel(seller_id)
                # print(7)
        buyer_stub = Buyer_pb2_grpc.BuyerStub(buyer_channel)
                # print(6)
        request = Buyer_pb2.NotificationRequest(Notification = Info)
                # print(4)
        response = buyer_stub.Notification_Print(request)
                # print(5)
        print(f"Sent notification to {seller_id} for {item_id}:", response.status == 0)
        
        return 1

    def UpdateItem(self, request, context):
        # Process UpdateItem request
        print(f"Update Item {request.item_id} request from {request.address}")

        # print(seller_items)
        # Process request and return response
        response = market_pb2.UpdateItemResponse()
        seller_info = registered_sellers.get(request.address)
        if seller_info and seller_info == request.uuid:
            item_id = request.item_id
            # print("Done 1")
            if item_id in seller_items[request.address].keys():
                # print("Done 2")
                # Update item details
                item = seller_items[request.address][item_id]
                item["Price per unit"] = request.new_price
                item["Quantity"] = request.new_quantity
                response.status = market_pb2.UpdateItemResponse.Status.SUCCESS
                response.item_id = request.item_id
                
                # print("Naman")
                # Notify buyers interested in this item about the update
                # self.NotifySellers(item_id)
            else:
                response.status = market_pb2.UpdateItemResponse.Status.ITEM_NOT_FOUND
        else:
            response.status = market_pb2.UpdateItemResponse.Status.UNAUTHORIZED

        # print(99)
        (self.NotifyBuyer(request.item_id, request.new_price, request.new_quantity, request.address))
        print(f"Sending Update Item response for request from {request.address} for Item {response.item_id}:", response.status == 0)
        # print(seller_items)
        return response
    
    def DisplaySellerItems(self, request, context):
        print(f"Received DisplaySellerItems Request from {request.address}")

        # Create a DisplaySellerItemsResponse instance and set the status
        response = market_pb2.DisplaySellerItemsResponse()
        response.status = market_pb2.DisplaySellerItemsResponse.Status.SUCCESS

        # print(1)
        # Add items to the response
        # print(seller_items[request.address])
        response.items = ""
        for item_id, item_info in seller_items[request.address].items():
            # print(2)
            item_variable = ""
            item_variable += str(item_id) + "\t"
            item_variable += str(item_info['Product Name']) + "\t"
            item_variable += str(item_info['Category']) + "\t"
            item_variable += str(item_info['Quantity']) + "\t"
            item_variable += str(item_info['Description']) + "\t"
            item_variable += str(item_info['Price per unit']) + "\t"
            # item_variable.seller_address = item_info['Seller Address']
            item_variable += str(item_info['Rating']) + "\t"  # Set the rating as needed
            # item_variable.seller_uuid = item_info['Seller UUID']
            # print(3)
            response.items += item_variable + "\n"

        # Serialize the response to send it
        # bytes_data = response.SerializeToString()
        # print(4)
        print("Sending DisplaySellerItems response:", response.status == 0)
        # print(5)
        return response

    def DeleteItem(self, request, context):
        print(f"Received request to delete item {request.item_id} from  seller {request.address}.")
        
        response = market_pb2.DeleteItemResponse()
        if request.item_id in seller_items[request.address].keys():
            del seller_items[request.address][request.item_id]
            response.status = market_pb2.DeleteItemResponse.Status.SUCCESS
        else:
            response.status = market_pb2.DeleteItemResponse.Status.INVALID

        return response

    def DisplayTransactionLogs(self, request, context):
        # Process DisplayTransactionLogs request
        print("Received DisplayTransactionLogs request:", request)

        # Process request and return response
        response = market_pb2.DisplayTransactionLogsResponse()
        response.logs.extend(transaction_logs)

        print("Sending DisplayTransactionLogs response:", response)
        return response

    def RateItem(self, request, context):
        # Process RateItem request
        print("Received RateItem request:", request)

        # Process request and return response
        response = market_pb2.RateItemResponse()
        item_id = request.item_id
        buyer_id = request.buyer_address
        rating = request.rating

        response.status = market_pb2.RateItemResponse.Status.ITEM_NOT_FOUND
        for seller_it in seller_items.values():
            # print(1)
            if item_id in seller_it:
                # print(2)
            # Check if the buyer has already bought the item
                item_bought = False
                for log in transaction_logs:
                    # print(3)
                    if log["Item ID"] == item_id and log["Buyer ID"] == buyer_id:
                        # print(4)
                        item_bought = True
                        if log["Buyer ID"] in rating_dict:
                            # print(5)
                            if log["Item ID"] in rating_dict[log["Buyer ID"]]:
                                # print(6)
                                item_bought = False
                            else:
                                # print(7)
                                rating_dict[log["Buyer ID"]].append(log["Item ID"])
                        else:
                            # print(8)
                            rating_dict[log["Buyer ID"]] = []
                            rating_dict[log["Buyer ID"]].append(log["Item ID"])
                        break
                if item_bought:
                    # print(9)
                    # Update the rating for the item
                    for seller_address, items in seller_items.items():
                        # print(10)
                        if item_id in items:
                            # print(11)
                            item = items[item_id]
                            item["Rating"] = rating
                            response.status = market_pb2.RateItemResponse.Status.SUCCESS
                            break
            else:
                # print(12)
                response.status = market_pb2.RateItemResponse.Status.UNAUTHORIZED

        print("Sending RateItem response:", response)
        return response

    def SearchItem(self, request, context):
        # Process SearchItem request
        print("Received SearchItem request:", request)

        # Process request and return response
        response = market_pb2.SearchItemResponse()
        for seller_address, items in seller_items.items():
            for item_id, item_details in items.items():
                if request.item_name.lower() in item_details["Product Name"].lower():
                    item_info = response.items.add()
                    item_info.item_id = item_id
                    item_info.product_name = item_details["Product Name"]
                    item_info.category = item_details["Category"]
                    item_info.quantity = item_details["Quantity"]
                    item_info.description = item_details["Description"]
                    item_info.price_per_unit = item_details["Price per unit"]
                    item_info.seller_address = item_details["Seller Address"]
                    item_info.rating = item_details.get("Rating", 0)  # If rating is not available, set to 0
                    # item_info.seller_uuid = item_details["Seller UUID"]

        print("Sending SearchItem response:", response)
        return response

    def NotifyBuyer(self, item_id, price, quantity, seller_id):
        Info = f"{seller_id} has changed {item_id} price to {price} and quantity to {quantity}"
        # print(Info)
        # print(1)
        if item_id in buyer_wishlist:
            # print(2)
            for buyer_id in buyer_wishlist[item_id]:
                # print(3)
                buyer_channel = grpc.insecure_channel(buyer_id)
                # print(7)
                buyer_stub = Buyer_pb2_grpc.BuyerStub(buyer_channel)
                # print(6)
                request = Buyer_pb2.NotificationRequest(Notification = Info)
                # print(4)
                response = buyer_stub.Notification_Print(request)
                # print(5)
                print(f"Sent notification to {buyer_id} for {item_id}:", response.status == 0)
        return 1

def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    market_pb2_grpc.add_MarketServicer_to_server(MarketServicer(), server)
    server.add_insecure_port('0.0.0.0:50051')  # Market service port remains 50051
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
