from xmlrpc.client import ServerProxy
import inspect

# Connect to the server
server = ServerProxy("http://localhost:8000/")

# Define the Python script as text
def add(x, y):
    return x + y + 10

script = source_code = inspect.getsource(add)

# Specify variables to pass to the script
variables = (5, 3)
# add_function = add
# script = inspect.getsource(add_function)
print(f'{script} with {variables}')

# Call the execute_script function on the server
print(f'Executing function script on {server} with {variables}')
result = server.execute_script('add', '9900180339', script, variables)
print("Result:", result)
