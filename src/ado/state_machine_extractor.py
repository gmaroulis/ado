import importlib
import json
import os
import sys

ENV = os.getenv('Environment', 'dev')


def process_args(args):
    """Process cmd args.

    Args:
        args (list): List of strings.
    Returns
        tuple with the processed args.
    """
    sfn_name = ''
    aws_account = ''

    if args.aws:
        aws_account = args.aws[0]
    if args.name:
        sfn_name = args.name[0]

    return sfn_name, aws_account


def generate_state_machine_template(args):
    """Generate state machine template.

    Args:
        args (list): List of strings.
    Returns:
        dict: with the state machine template configuration.
    """
    sfn_name, aws_account = process_args(args)

    flow_path = os.path.abspath(sfn_name)
    sys.path.insert(1, flow_path)

    source_flow = importlib.import_module('flow')
    try:
        source_flow = source_flow.Flow('', '')
    except Exception:
        source_flow = source_flow.Flow()

    dependencies = get_dependencies(source_flow)
    state_machine = get_state_machine(dependencies, source_flow, sfn_name, aws_account)
    print(json.dumps(state_machine[0]))


def get_dependencies(source_flow):
    """Get the dependencies."""
    dependencies = {}

    def get_dependency(name, activity, requires=[]):
        dependencies[activity.name] = [a.name for a in requires if a]
        activity.result = {}
        return activity
    try:
        source_flow.decider(get_dependency, {})  # Some projects are passing various params to the decider
    except Exception:
        source_flow.decider(get_dependency)

    return dependencies


def build_states(dependencies):
    """Build the state flow."""
    filled_reqs = []
    reqs_to_add = dependencies
    stages = {}
    stage_num = 0

    while len(reqs_to_add) > 0:
        stage = []
        for key in reqs_to_add:
            if(len(reqs_to_add[key]) == 0 or set(reqs_to_add[key]).issubset(filled_reqs)):
                stage.append(key)

        for a in stage:
            filled_reqs.append(a)
            del reqs_to_add[a]

        stages['Stage {}'.format(stage_num)] = stage
        stage_num += 1

    return stages


def get_state_machine(dependencies, source_flow, sfn_name, aws_account):
    """Get the State Machine."""
    state_machine = {
        'Comment': sfn_name,
        'StartAt': None,
        'States': {}}
    lambdas = []
    lambda_arn_template = 'arn:aws:lambda:us-east-1:{aws_account}:function:{env}-{k}'

    print(dependencies)
    states = build_states(dependencies)
    list_stages = list(states.keys())

    for i, k in enumerate(states):
        lambda_function_arn = lambda_arn_template.format(env=ENV, k=k, aws_account=aws_account)
        lambdas.append(lambda_function_arn)
        job_definition = "arn:aws:batch:us-east-1:103233932089:job-definition/vikash-hello-world-garcon:1"
        job_queue = "arn:aws:batch:us-east-1:103233932089:job-queue/vikash-hello-world"

        key = k

        if len(states[k]) == 1:
            key = states[k][0]

        if state_machine['StartAt'] is None:
            state_machine['StartAt'] = key

        if (len(states.values()) - 1 == i):
            if len(states[k]) == 1:
                state_machine['States'][key] = {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::batch:submitJob.sync",
                    "Parameters": {
                        "JobDefinition": job_definition,
                        "JobName": key,
                        "JobQueue": job_queue,
                        "ContainerOverrides": {
                            "command": ["garcon-activity-local -i flow -c Flow run {}".format(key)]
                            }
                        },
                    "End": True
                    }
            else:
                branches = []
                for branch in states[k]:

                    new_branch = {
                        "StartAt": branch,
                        "States": {}
                    }
                    new_branch['States'][branch] = {
                        "Type": "Task",
                        "Resource": "arn:aws:states:::batch:submitJob.sync",
                        "Parameters": {
                            "JobDefinition": job_definition,
                            "JobName": branch,
                            "JobQueue": job_queue,
                            "ContainerOverrides": {
                                "command": ["garcon-activity-local -i flow -c Flow run {}".format(branch)]
                            }
                            },
                        "End": True
                    }

                    branches.append(new_branch)

                state_machine['States'][key] = {
                    "Type": "Parallel",
                    "End": True,
                    "Branches": branches
                    }

        else:
            next_key = list_stages[i+1]
            if len(states[next_key]) == 1:
                next_key = states[next_key][0]
            if len(states[k]) == 1:
                state_machine['States'][key] = {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::batch:submitJob.sync",
                    "Parameters": {
                        "JobDefinition": job_definition,
                        "JobName": key,
                        "JobQueue": job_queue,
                        "ContainerOverrides": {
                            "command": ["garcon-activity-local -i flow -c Flow run {}".format(key)]
                            }
                        },
                    "Next": next_key
                    }
            else:
                branches = []
                for branch in states[k]:

                    new_branch = {
                        "StartAt": branch,
                        "States": {}
                    }
                    new_branch['States'][branch] = {
                        "Type": "Task",
                        "Resource": "arn:aws:states:::batch:submitJob.sync",
                        "Parameters": {
                            "JobDefinition": job_definition,
                            "JobName": branch,
                            "JobQueue": job_queue,
                            "ContainerOverrides": {
                                "command": ["garcon-activity-local -i flow -c Flow run {}".format(branch)]
                            }
                            },
                        "End": True
                    }

                    branches.append(new_branch)

                state_machine['States'][key] = {
                    "Type": "Parallel",
                    "Next": next_key,
                    "Branches": branches
                    }

    return state_machine, lambdas
