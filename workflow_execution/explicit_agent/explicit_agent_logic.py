
# -----------------------------------------------------------------------------
# SECTION: Imports
# -----------------------------------------------------------------------------


import logging
import os
from typing import Any, Dict, List

from agents.generic_agent import generic_agent
from utils.helper_functions import load_explicit_functions

#------------------------------------------------------
# SECTION : Explicit agent logic execution
#------------------------------------------------------
def explicit_logic_exec(
    task_outputs: List[Dict],
    user_input: str,
    query_list: List[str],
    conversation: str,
    user_details: Dict[str, Any],
    total_input_tokens_count: int,
    total_output_tokens_count: int,user
):
    explicit_functions = load_explicit_functions()

    print("Loading Explicit functions")
    print("*"*50)
    print(explicit_functions)
    print("*"*50)
    
    generic_agent_outputs = []
    task_id = 0
    explicit_task_outputs = []
    input_tokens_count = 0
    output_tokens_count = 0
    check = False

    param_name = None

    
    #---------------------------------------------------------------
    # SECTION: Reading feilds of explicit functions from YAML files
    #---------------------------------------------------------------
    if explicit_functions is not None:
        for functions in explicit_functions:
            task_id += 1
            prev_agents_required = []
            inputs ={}
            depends = False
            for function_name in functions.keys():
                for params in functions[function_name]['input_params']:
                    for key in params.keys():
                        input_params = params[key]['param_name']
                        variable = params[key]['variable_name']
                        if variable == 'task_outputs':
                            check = True
                            param_name = input_params
                        if variable in locals():
                            inputs[input_params] = locals().get(variable)
                        elif variable in globals():
                            inputs[input_params] = globals().get(variable)
                if functions[function_name]['depends_on'] is not None:
                    depends=True
            if not depends:
                if check and len(task_outputs)>1:
                    for i in range(len(task_outputs)):
                        # print(param_name)
                        input = {}
                        for key in inputs.keys():
                            if key != param_name:
                                input[key] = inputs[key]
                            else:
                                input[key] = inputs[key][i]
                        scratchpad, input_tokens_count, output_tokens_count = generic_agent(function_name,input,user)
                        explicit_task_outputs.append({
                            "task_id": i,
                            "function_name": function_name,
                            "output": scratchpad
                        })

                        conversation["present_conversation"].append({function_name: scratchpad})
                
                else:
                    print(function_name,inputs)
                    scratchpad, input_tokens_count, output_tokens_count = generic_agent(function_name,inputs,user)

                    explicit_task_outputs.append({
                        "task_id": task_id,
                        "function_name": function_name,
                        "output": scratchpad
                    })
                    conversation["present_conversation"].append({function_name: scratchpad})
            else:
                continue
        
            total_input_tokens_count += input_tokens_count
            total_output_tokens_count += output_tokens_count
                
    print(explicit_task_outputs)

    explicit_tasks_outputs = {
            "output": explicit_task_outputs
        }
    
    return explicit_tasks_outputs,total_input_tokens_count,total_output_tokens_count,conversation

# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------