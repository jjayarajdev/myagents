import yaml
import os




def get_dboconfig(agent_name,user):
    functions_path = os.path.join(os.getcwd(),'user_config_files', user, 'supervisor_functions.yaml')
    #loading of the YAML file
    with open(functions_path,encoding="utf-8") as file:
        try:
            yaml.preserve_quotes = True
            prompts = yaml.safe_load(file)
        
        except yaml.YAMLError as exc:
            return exc
        dboconfig = None
        functions = prompts['functions']
        for func in functions:
            key = func.keys()
            if list(key)[0] == agent_name:
                dboconfig =func[agent_name]['db_config']
                
    return dboconfig
