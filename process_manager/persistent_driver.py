import threading
import time

class PersistentWebDriver:

    def __init__(self, driver):
        self.driver = driver
        self.lock = threading.Lock()
        self.last_active = time.time()

    def perform_activity(self):
        # Add your code for performing any necessary activity
        # For example, navigating to a specific page or clicking a button
        with self.lock:
            self.driver.refresh()

    def get_lock(self):
        return self.lock
    
    def get_driver(self):
        return self.driver
    
    def record_activity(self):
        try:
            print(f'Recording new activity')
            print(f'Last activity ')
            self.last_active = time.time()
            print(f'Time is {self.last_active}')
        except Exception as e:
            print(str(e))

    def keep_alive(self):
        interval_seconds=3600
        print('Keeping Alive')
        time.sleep(interval_seconds)
        # Function to keep the driver alive by performing activity at regular intervals
        while True:
            try:
                inactive_interval = time.time() - self.last_active 
                if inactive_interval >= interval_seconds:
                    print(f'Refreshing to keep alive.')
                    self.perform_activity()
                else:
                    print(f'Skip refresh as recently active.')
            except Exception as e:
                print(f"Error during keep-alive activity: {str(e)}")
                return
            time.sleep(interval_seconds)

