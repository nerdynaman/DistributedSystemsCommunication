import pika
import json
import sys

class User:
    """
    User class to subscribe to youtubers and receive notifications
    """
    def __init__(self, user_name, ip='localhost'):
        self.user_name = user_name

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(ip))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='user_requests')
        self.channel.queue_declare(queue=user_name)

    def update_subscription(self, youtuber, subscribe):
        """
        Update subscription of the user
        """
        request = {'user': self.user_name, 'youtuber': youtuber, 'subscribe': subscribe}
        self.channel.basic_publish(exchange='', routing_key='user_requests', body=json.dumps(request))
        print('SUCCESS')

    def user_login(self):
        """
        User login to the system
        """
        request = {'user': self.user_name}
        self.channel.basic_publish(exchange='', routing_key='user_requests', body=json.dumps(request))

    def receive_notifications(self):
        """
        Receive notifications from the queue about new videos
        """
        def callback(ch, method, properties, body):
            notification = json.loads(body.decode('utf-8'))
            youtuber = notification.get('youtuber')
            video_name = notification.get('video_name')
            print(f"New Notification: {youtuber} uploaded {video_name}")

        self.channel.basic_consume(queue=self.user_name, on_message_callback=callback, auto_ack=True)
        print(f"Waiting for notifications. To exit press CTRL+C")
        self.channel.start_consuming()

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print('Usage: python User.py <UserName> [s/u YoutuberName]')
    else:
        user_name = sys.argv[1]

        # Taking input of IP address of the RabbitMQ server
        ip = input("Enter the IP address of the RabbitMQ server: ")
        user = User(user_name, ip)

        if len(sys.argv) == 4:
            action = sys.argv[2].lower()
            youtuber_name = sys.argv[3]
            if action == 's':
                user.update_subscription(youtuber_name, subscribe=True)
            elif action == 'u':
                user.update_subscription(youtuber_name, subscribe=False)
        elif len(sys.argv) == 2:
            user.user_login()

        # Receive notifications after doing the required action
        user.receive_notifications()
