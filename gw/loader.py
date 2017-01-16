import os

matchers = []
commands = {}
reactors = {}

def command(command_name):
    def command_decorator(command_function):
        if command_name in commands:
            raise ValueError('Command {command} is already exists.'.format(command=command_name))
        commands[command_name] = command_function
        return command_function
    return command_decorator

def reactor(reactor_name):
    def reactor_decorator(reactor_function):
        if reactor_name in reactors:
            raise ValueError('Reactor {reactor} is already exists.'.format(reactor_name))
        reactors[reactor_name] = reactor_function
        return reactor_function
    return reactor_decorator

def matcher(matcher_function):
    matchers.append(matcher_function)
    return matcher_function

def import_plugins(path):
    for file in os.listdir(path):
        if file.startswith('plugin_'):
            clean_filename = os.path.splitext(file)[0]
            import clean_filename
			for attr in dir(clean_filename):
				item = getattr(clean_filename, attr)
				if callable(item):
					item()
