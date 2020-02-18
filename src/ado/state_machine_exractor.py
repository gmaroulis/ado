import imp
import os

def generate_state_machine_template(args):
    """Process cmd args.

    Args:
        args (list): List of strings.
    Returns:
        dict: with the state machine template configuration.
    """
    basepath = args[0]
    flow = args[1]
    with os.scandir(basepath) as entries:
        for entry in entries:
            if entry.name == flow:
                flow_file = imp.load_source("flow", flow)
                source_flow = flow_file.Flow('', '')
                dependencies = get_dependencies(source_flow)


def get_dependencies(source_flow):
    dependencies = {}
    def get_dependency(name, activity, requires=[]):
        dependencies[activity.name] = [a.name for a in requires if a]
        activity.result = {}
        return activity
    source_flow.decider(get_dependency, {})
    print(dependencies)
    get_state_machine(dependencies, source_flow)
    return dependencies

def get_state_machine(dependencies, source_flow):
    state_machine = {
        'Comment': 'lol',
        'StartAt': None,
        'States': {}}
    for k in dependencies:
        if state_machine['StartAt'] is None:
            state_machine['StartAt'] = k
        state_machine['States'][k] = {
            'Type': 'Pass',
            'Result': 'lol',
            'End': 1
        }
    print(state_machine)
    return dependencies
