import pika
import json

class YoutubeServer:
    """
    Server class to handle user and youtuber requests
    """
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='user_requests')
        self.channel.queue_declare(queue='youtuber_requests')

        self.channel.basic_consume(queue='user_requests', on_message_callback=self.callbackUser, auto_ack=True)
        self.channel.basic_consume(queue='youtuber_requests', on_message_callback=self.callbackYt, auto_ack=True)

        # Dictionary to store user queues
        self.user_queues = {}

        self.users = {}
        self.youtubers = {}

        # Start consuming requests
        self.channel.start_consuming()

    def callbackUser(self, ch, method, properties, body):
        """
        Callback function for user_requests queue
        """
        request = json.loads(body.decode('utf-8'))
        user = request.get('user')
        youtuber = request.get('youtuber')
        subscribe = request.get('subscribe')

        if user not in self.users:
            self.users[user] = []

        if youtuber is not None:
            if youtuber not in self.youtubers:
                print(f"{youtuber} added to youtubers list")
                self.youtubers[youtuber] = []

        if subscribe is not None:
            print(f"{user} logged in")
            if subscribe:
                if youtuber not in self.users[user]:
                    self.users[user].append(youtuber)
                    print(f"{user} subscribed to {youtuber}")
                else:
                    print(f"{user} is already subscribed to {youtuber}")
            else:
                if youtuber in self.users[user]:
                    self.users[user].remove(youtuber)
                    print(f"{user} unsubscribed from {youtuber}")
                else:
                    print(f"{user} is already unsubscribed to {youtuber}")
        else:
            print(f"{user} logged in")

        # Check if the user queue is not already declared
        if user not in self.user_queues:
            print(f"Declaring queue for user: {user}")
            self.channel.queue_declare(queue=user)
            self.user_queues[user] = True  # Mark the queue as declared

    def callbackYt(self, ch, method, properties, body):
        """
        Callback function for youtuber_requests queue
        """
        request = json.loads(body.decode('utf-8'))
        youtuber = request.get('youtuber')
        video_name = request.get('video_name')

        if youtuber not in self.youtubers:
            self.youtubers[youtuber] = []

        if video_name not in self.youtubers[youtuber]:
            self.youtubers[youtuber].append(video_name)
            print(f"{youtuber} uploaded {video_name}")

            # Notify users
            self.notify_users(youtuber, video_name)
        else:
            print(f"{youtuber} already uploaded {video_name}")

    def notify_users(self, youtuber, video_name):
        """
        Notify users about the new video uploaded by the youtuber
        """
        for user, subscriptions in self.users.items():
            if youtuber in subscriptions:
                print(f"Sending notification to {user}")
                notification = {'youtuber': youtuber, 'video_name': video_name}
                self.channel.basic_publish(exchange='', routing_key=user, body=json.dumps(notification))

if __name__ == '__main__':
    youtube_server = YoutubeServer()
