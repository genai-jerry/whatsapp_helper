from xmlrpc.server import SimpleXMLRPCServer

def execute_script(function_name, mobile_number, script, variables):
    try:
        print(mobile_number)
        # Create a dictionary for local variables
        locals_dict = {}
        
        # Execute the script in the context of locals_dict
        exec(script, globals(), locals_dict)

        # Call the function named 'main' in the script and pass variables
        if function_name in locals_dict and callable(locals_dict[function_name]):
            result = locals_dict[function_name](*variables)
            return result
        else:
            return f"Function {function_name} not found or not callable in the script."
    except Exception as e:
        return f"Error executing script: {str(e)}"

if __name__ == "__main__":
    server = SimpleXMLRPCServer(("localhost", 8000))
    server.register_function(execute_script, "execute_script")
    print("Server listening on port 8000...")
    server.serve_forever()
