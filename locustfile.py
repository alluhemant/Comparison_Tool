# here we are configuring for load testing

from locust import HttpUser, task, between


class XmlCompareUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def compare_responses(self):
        self.client.get("/compare")

# locust -f locustfile.py --headless --users 100 --spawn-rate 10 --run-time 1m
