import yaml
import copy

base_config_file = 'exp_fp16_ND_difft.yaml'

base_run_sh = """
#!/bin/bash 
python3 run.py CSX --params {config_file} --model_dir {log_dir} --mode train --compile_only --num_act_servers 1 --mgmt_address localhost:9000
"""

# Define parameters and options
param_dict = {}
param_dict['trainer.init.model.attention_module'] = ['diff_attention', 'aiayn_attention']
param_dict['trainer.init.model.attention_activation'] = ['softmax', 'sigmoid']
param_dict['trainer.init.model.num_hidden_layers'] = [12,4]
param_dict['trainer.init.model.num_heads'] =  [12,4]
param_dict['trainer.init.model.position_embedding_type'] = ['learned', 'alibi', {'position_embedding_type':'rotary', 'rope_theta':500000, 'rotary_dim':64}]
param_dict['trainer.fit.train_dataloader.batch_size'] = [256,128,64,8]

# Exclusion list
exclusions = []
#exclusions.append({'trainer.init.model.attention_module': 'diff_attention', 'trainer.init.model.position_embedding_type': 'alibi'})

# if any of the higher values susceed, dont iterate throgh lower values
stop_criteria_params = ['trainer.fit.train_dataloader.batch_size', 'trainer.init.model.num_heads' , 'trainer.init.model.num_hidden_layers']



def read_yaml_file(filename):
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
    return data

# Example usage

yaml_data = read_yaml_file(base_config_file)
print(yaml_data['trainer']['fit']['train_dataloader'])


from itertools import product
import yaml
import os


# Generate all combinations of parameters
keys, values = zip(*param_dict.items())
all_combinations = [dict(zip(keys, v)) for v in product(*values)]
#for combo in all_combinations: 
#    print(combo)#

# Function to update nested dictionary
def update_nested_dict(ref_config, combo_key, combo_value):

    #print("looking for combo_key ", combo_key)
    new_dict = {}

    for key, value in ref_config.items():

        #print("iterating through",  key)
        if isinstance(value, dict):
            #print("nested parse",  key)
            new_dict[key] = update_nested_dict(ref_config[key], combo_key, combo_value)
            
        
        elif(key == combo_key):
            #print("Match Found ", key, value)
            if isinstance(combo_value, dict):
                for k, v in combo_value.items():
                    new_dict[k] = v
                    print("inserted : ", k, ":", v)
            else:
                new_dict[combo_key] = combo_value
                #print("inserted : ", combo_key, ":", combo_value)
        
        else:
            new_dict[key] = value
    
    return new_dict



    #return ref_config



# Filter out combinations that match any exclusion
valid_combinations = []
for combination in all_combinations:
    exclude = False
    for exclusion in exclusions:
        if all(combination.get(k) == v for k, v in exclusion.items()):
            exclude = True
            break
    if not exclude:
        valid_combinations.append(combination)

# Directory to save generated config files
config_dir = "generated_configs_local"
os.makedirs(config_dir, exist_ok=True)

# Save each valid combination as a YAML config file
combo_mapping = {}
for i, combination in enumerate(valid_combinations):
    #print("processing  combo : ", combination)
    new_config = copy.deepcopy(yaml_data)
    for key, value in combination.items():
        #print("inserting from Combo ", key, value)
        key_list = key.split('.')
        cur_conf  = new_config
        for key_cur in key_list[:-1]:
            cur_conf = cur_conf[key_cur]
        
        if isinstance(value, dict):
            for k, v in value.items():
                cur_conf[k] = v
        else:
            cur_conf[key_list[-1]] = value


    
    config_filename = os.path.join(config_dir, f"config_{i+1}.yaml")
    combo_mapping[f"config_{i+1}.yaml"] = combination


    with open(config_filename, 'w') as file:
        yaml.dump(new_config, file, default_flow_style=False)
        #print(new_config['trainer']['fit']['train_dataloader'])
    #break

print(f"Generated {len(valid_combinations)} config files in the '{config_dir}' directory.")




# generate run.sh files


# Directory to save run.sh files
run_sh_dir = "generated_run_scripts_local"
os.makedirs(run_sh_dir, exist_ok=True)

# Directory for logs/checkpoints
log_dir_main = "logs"
os.makedirs(log_dir_main, exist_ok=True)

# Generate run.sh files
run_mapping = {}
for k, config_file in enumerate(sorted(os.listdir(config_dir))):
    config_idx = int(config_file.split('.')[0].split('_')[-1])
    print(config_idx, config_file)
    logging_folder = os.path.join(log_dir_main , "log_" + str(config_idx))
    run_sh_content = base_run_sh.format(config_file=os.path.join(config_dir, config_file), log_dir=logging_folder)
    run_sh_filename = os.path.join(run_sh_dir, f"run_{config_idx}.sh")
    with open(run_sh_filename, 'w') as file:
        file.write(run_sh_content)
    run_log_file = os.path.join(logging_folder, "latest_run.log")
    run_mapping[run_sh_filename] = {"Config": config_file, "Run_Log_file":run_log_file, "Combination":combo_mapping[config_file]}

import json
# Write to JSON file
json_file = 'run_config_mapping_local.json'
with open(json_file, 'w') as file:
    json.dump(run_mapping, file, indent=4)
print(f"JSON file '{json_file}' has been created.")


