import pika
import json
import sys
import time

class Youtuber:
    """
    Youtuber class to publish videos to the queue.
    """
    def __init__(self, youtuber_name, video_name):
        self.youtuber_name = youtuber_name
        self.video_name = video_name

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='youtuber_requests')

    def publish_video(self):
        """
        Publish video to the queue.
        """
        # print(f"DEBUG: {self.youtuber_name} uploads {self.video_name}")
        request = {'youtuber': self.youtuber_name, 'video_name': self.video_name}
        self.channel.basic_publish(exchange='', routing_key='youtuber_requests', body=json.dumps(request))
        print('SUCCESS')
    
    """
    # This is an alternative BUGGY implementation of publish_video that waits for acknowledgment from the server
    def publish_video(self, youtuber, video_name):
        message = {"youtuber": youtuber, "video_name": video_name}
        correlation_id = str(time.time())  # Use timestamp as correlation_id

        self.channel.basic_publish(
            exchange='',
            routing_key='youtuber_requests',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make the message persistent
                correlation_id=correlation_id,
            )
        )
        print(f'Waiting for confirmation from the server...')

        # Use a timeout for waiting for acknowledgment (adjust as needed)
        timeout = 5  # seconds
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check if an acknowledgment with the correlation_id has been received
            if self.connection.process_data_events():
                print('SUCCESS: Received acknowledgment from the server')
                self.connection.close()
                return

            time.sleep(0.1)  # Sleep for a short interval to avoid busy-waiting

        print('FAIL: Did not receive acknowledgment from the server within the timeout')
        self.connection.close()
    """

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python Youtuber.py <YoutuberName> <VideoName>')
        sys.exit(1)
    else:
        youtuber_name = sys.argv[1]
        video_name = ' '.join(sys.argv[2:])
        youtuber = Youtuber(youtuber_name, video_name)
        youtuber.publish_video()
