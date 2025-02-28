import json

import multiprocessing
import subprocess
import os
import signal
import sys
import re
import time

### All Settings here
json_file = "run_config_mapping_local.json"
parentdir = '/cb/home/arunkp/ws/monolith_r2.4'
scrpt_str1 = """
cbrun -- srun -c 32 appliance_emulator -b ws_swmodel -n 1 -a -f /net/ankura-dev/srv/nfs/ankura-data/ws/monolith/src/infra/fabric/sdr_780x1191_cs3.json
"""


def read_mgmt_address(log_file):
    pattern = r'--mgmt_address (\d+\.\d+\.\d+\.\d+:\d+)'
    max_attempts = 30
    attempts = 0
    while attempts < max_attempts:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
                print(content)
                match = re.search(pattern, content)
                if match:
                    return match.group(1)
        time.sleep(5)
        print("attempts ", attempts)
        attempts += 1
    return None

def update_script2(script2_path, mgmt_address):
    with open(script2_path, 'r') as f:
        content = f.read()
    
    # Replace or add the management address
    if '--mgmt_address' in content:
        updated_content = re.sub(r'--mgmt_address \S+', f'--mgmt_address {mgmt_address}', content)
    else:
        updated_content = content.replace('\n', f' --mgmt_address {mgmt_address}\n', 1)
    
    with open(script2_path, 'w') as f:
        f.write(updated_content)

def run_script_cwd(script_name, log_file):
    if log_file:
        with open(log_file, 'w') as f:
            process = subprocess.Popen(['bash', script_name], 
                                       stdout=f, 
                                       stderr=subprocess.STDOUT, 
                                       start_new_session=True)
    else:
        process = subprocess.Popen(['bash', script_name], 
                                   start_new_session=True)
        
    return_status = process.wait()
    return return_status, process

def run_script(parent_dir, current_working_directory, script_name, log_file=None):

    os.chdir(parent_dir)

    if log_file:
        with open(log_file, 'w') as f:
            process = subprocess.Popen(['bash', script_name], 
                                       stdout=f, 
                                       stderr=subprocess.STDOUT, 
                                       start_new_session=True)
    else:
        process = subprocess.Popen(['bash', script_name], 
                                   start_new_session=True)
    os.chdir(current_working_directory)
    return process

def monitor_and_kill(log_compile_file, process_to_kill):

    os.killpg(os.getpgid(process_to_kill.pid), signal.SIGTERM)
    return 
    while(1):
        with open(log_compile_file, 'r') as f:
            content = f.read()
        if('RUN_COMPLETE' in content):
            os.killpg(os.getpgid(process_to_kill.pid), signal.SIGTERM)
            break
        time.sleep(60)


def run_cur_Script(parent_dir, current_working_directory, script1, script2):


    log_file = os.path.join(parent_dir,'script2_log.txt')

    # Start script1
    process1 = run_script (parent_dir, current_working_directory, script1, log_file=log_file)
   

    # Wait for management address to appear in the log
    mgmt_address = read_mgmt_address(log_file)
    if mgmt_address:
        print(f"Found management address: {mgmt_address}")
        update_script2(script2, mgmt_address)
    else:
        print("Failed to find management address. Running script2 without updates.")

    # Start script2
    log_complie_file = "logging_compile_file.txt"
    return_status,process2 = run_script_cwd(script2, log_complie_file)

    # Create a monitoring process for script1
    monitor = multiprocessing.Process(target=monitor_and_kill, args=(log_complie_file, process1))
    monitor.start()

    try:
        # Wait for both processes to finish
        process1.wait()
        #return_code = process2.wait()
    except KeyboardInterrupt:
        # Handle Ctrl+C
        print("Interrupted. Terminating processes...")
        os.killpg(os.getpgid(process1.pid), signal.SIGTERM)
        os.killpg(os.getpgid(process2.pid), signal.SIGTERM)
        monitor.terminate()
    finally:
        # Clean up
        monitor.join()
        process1.wait()
        #process2.wait()

    print("All processes finished.")
    return return_status



current_working_directory = os.getcwd()
print(current_working_directory)

# Read from JSON file
with open(json_file, 'r') as file:
    data = json.load(file)
print(data)
print(data['generated_run_scripts_local/run_1.sh'])



script1 = os.path.join(parentdir,'emulator_server.sh')
with open(script1, 'w') as file:
    file.write(scrpt_str1)


import subprocess

# Execute each run.sh script and record results
print(data.keys())

for run_sh_path in data.keys():
    cur_info = data[run_sh_path]
    cur_info["error_info"] = ""
    cur_info['Status'] = "Yet to Run"


# Write to JSON file
json_status_file = 'run_status.json'
with open(json_status_file, 'w') as file:
    json.dump( data, file, indent=4)

for run_sh_path in data.keys():
    cur_info = data[run_sh_path]
    try:
        # Make the script executable
        print("Compiling on CSX with Key Changes ", data[run_sh_path]["Combination"])
        cur_info['Status'] = "Started"
        with open(json_status_file, 'w') as file:
            json.dump( data, file, indent=4)

        
        subprocess.run(["chmod", "+x", run_sh_path], check=True)
        
        # Execute the script
        return_code = run_cur_Script(parentdir, current_working_directory, script1, run_sh_path)
        #result = subprocess.run([run_sh_path], capture_output=True, text=True, check=True)
        #cur_info["error_info"] = result.stdout
        if(return_code == 0):
            print(run_sh_path, "  Successfully Compiled")
            cur_info['Status'] = "Complied"
        else:
            print(run_sh_path, "  Failed Compilation")
            cur_info['Status'] = "Falied"

        
    except subprocess.CalledProcessError as e:
        print(run_sh_path, "  Failed to Compiled")
        cur_info['Status'] = "Failed"
        #cur_info["error_info"] = e.stderr
        #print(f"Error: {e.stderr}")

    with open(json_status_file, 'w') as file:
        json.dump( data, file, indent=4)
    break

# Display results



