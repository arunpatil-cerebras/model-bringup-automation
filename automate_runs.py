import json

json_file = "run_config_mapping.json"

# Read from JSON file
with open(json_file, 'r') as file:
    data = json.load(file)

print(data['generated_run_scripts/run_1.sh'])

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
        result = subprocess.run([run_sh_path], capture_output=True, text=True, check=True)
        #cur_info["error_info"] = result.stdout
        print(run_sh_path, "  Successfully Compiled")
        cur_info['Status'] = "Complied"
        
    except subprocess.CalledProcessError as e:
        print(run_sh_path, "  Failed to Compiled")
        cur_info['Status'] = "Failed"
        #cur_info["error_info"] = e.stderr
        #print(f"Error: {e.stderr}")

    with open(json_status_file, 'w') as file:
        json.dump( data, file, indent=4)


# Display results



