import imp
import os
import json
from functools import reduce
import operator

ENV = os.getenv('Environment', 'dev')

def process_args(args):
    """Process cmd args

    Args:
        args (list): List of strings.
    Returns
        tuple with the processed args
    """
    basepath = ''
    sfn_name = ''
    aws_account = ''

    if len(args.names):
        basepath = args[0]
        sfn_name = args[1]
        aws_account = args[2]

    if args.aws:
        aws_account = args.aws[0]
    if args.path:
        basepath = args.path[0]
    if args.name:
        sfn_name = args.name[0]

    return basepath, sfn_name, aws_account


def generate_state_machine_template(args):
    """Generate state machine template.

    Args:
        args (list): List of strings.
    Returns:
        dict: with the state machine template configuration.
    """
    basepath, sfn_name, aws_account = process_args(args)
    flow = 'flow.py'
    flow_file_path = '{basepath}/{flow}'.format(basepath=basepath, flow=flow)

    with os.scandir(basepath) as entries:
        for entry in entries:
            if entry.name == flow:
                flow_file = imp.load_source(flow, flow_file_path)
                try:
                    source_flow = flow_file.Flow('', '')
                except Exception as exc:
                    source_flow = flow_file.Flow()

                dependencies = get_dependencies(source_flow)
                state_machine = get_state_machine(dependencies, source_flow, sfn_name, aws_account)
                print(json.dumps(state_machine[0]))
                print('Lambdas to create:', state_machine[1])


def get_dependencies(source_flow):
    dependencies = {}
    def get_dependency(name, activity, requires=[]):
        dependencies[activity.name] = [a.name for a in requires if a]
        activity.result = {}
        return activity
    try:
        source_flow.decider(get_dependency, {}) # Some projects are passing various params to the decider
    except Exception:
        source_flow.decider(get_dependency)

    return dependencies

def get_state_machine(dependencies, source_flow, sfn_name, aws_account):
    state_machine = {
        "Comment": sfn_name,
        "StartAt": None,
        "States": {}}
    lambdas = []
    list_dependencies = list(dependencies.keys())
    lambda_arn_template = "arn:aws:lambda:us-east-1:{aws_account}:function:{env}-{k}"


    for i, k in enumerate(dependencies):
        lambda_function_arn = lambda_arn_template.format(env=ENV, k=k, aws_account=aws_account)
        lambdas.append(lambda_function_arn)

        if state_machine["StartAt"] is None:
            state_machine["StartAt"] = k

        if (len(dependencies.values()) - 1 == i):
            state_machine["States"][k] = {
                "Type": "Task",
                "Resource": lambda_function_arn,
                "End": True
            }
        else:
            state_machine["States"][k] = {
                "Type": "Task",
                "Resource": lambda_function_arn,
                "Next": list_dependencies[i+1]
            }

    return state_machine, lambdas
