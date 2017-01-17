from zork.gw.plugins.pluginManager import matcher, command, reactor

@matcher
def default_matcher(client_name):
    if not client_name.startswith('david'):
        return 'test'

@command('test')
def activate_foo(client_name):
    return {'command': 'run_eval', 'args': 'foo()'}

@reactor('test')
def process_foo(client_name, output):
    if output == 'foo':
        return 'Big success, Client return foo as expected.'
    return 'Failure, Client return {} instead of foo'.format(output)
