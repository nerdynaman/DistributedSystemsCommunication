# YouTube Application with RabbitMQ

## Overview

This project implements a simplified version of a YouTube application using RabbitMQ. The system consists of three components:

1. **YoutubeServer**: Manages user logins, subscription requests, and video uploads.
2. **Youtuber**: Represents the service for YouTubers to publish videos.
3. **User**: Represents the service for users to log in, subscribe/unsubscribe to YouTubers, and receive notifications.

## How to Run

1. **YoutubeServer.py**: Run the server to start consuming requests.

    ```bash
    $ python YoutubeServer.py
    ```

2. **Youtuber.py**: Run the Youtuber service to publish a video.
    
    **The Youtuber name should not be space separated**
    ```bash
    $ python Youtuber.py tuber1 video1
    ```

3. **User.py**: Run the User service to log in, subscribe/unsubscribe to a YouTuber, and receive notifications.

    ```bash
    $ python User.py user1 s tuber1
    $ python User.py user2 s tuber2
    $ python User.py user3
    ```

## Flow of Service

- Run `YoutubeServer.py` to start the server.
- Run `Youtuber.py` and `User.py` in any sequence multiple times and simultaneously.
- Users receive real-time notifications when their subscribed YouTubers upload a new video.

Note: Ensure that RabbitMQ is running locally on the default port (5672).

