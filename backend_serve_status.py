from flask import Flask, render_template_string, send_file, abort
import json
import os

app = Flask(__name__)

# Path to your JSON file
JSON_FILE_PATH = 'run_status.json'

# Directory containing config files
CONFIG_DIR = '/cra-614/home/arunkp/research/modelzoos/arun/modelzoo/models/nlp/gpt2/generated_configs'

#Log File
LOG_DIR = '/cra-614/home/arunkp/research/modelzoos/arun/modelzoo/models/nlp/gpt2'




@app.route('/')
def home():
    with open(JSON_FILE_PATH, 'r') as f:
        data = json.load(f)
    
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Run Status Table</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            tr:hover { background-color: #f5f5f5; }
            a { color: #1a73e8; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
        <script>
        setTimeout(function(){
            location.reload();
        }, 30000); // Refresh every 30 seconds
        </script>
    </head>
    <body>
        <h1>Run Status Table</h1>
        <table>
            <tr>
                <th>Run Script</th>
                <th>Config File</th>
                <th>Run Log File</th>
                <th>Status</th>
                <th>Combination</th>
                <th>Error Info</th>
            </tr>
            {% for run_script, run_data in data.items() %}
            <tr>
                <td>{{ run_script }}</td>
                <td><a href="{{ url_for('serve_file', file_type='config', filename=run_data.Config) }}">{{ run_data.Config }}</a></td>
                <td><a href="{{ url_for('serve_file', file_type='log', filename=run_data.Run_Log_file) }}">{{ run_data.Run_Log_file }}</a></td>
                <td>{{ run_data.Status }}</td>
                <td>{{ run_data.Combination | tojson }}</td>
                <td>{{ run_data.error_info }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    '''
    
    return render_template_string(html, data=data)

@app.route('/file/<file_type>/<path:filename>')
def serve_file(file_type, filename):
    if file_type == 'config':
        file_path = os.path.join(CONFIG_DIR, filename)
    elif file_type == 'log':
        file_path = os.path.join(LOG_DIR, filename)
    else:
        abort(400, description="Invalid file type")
    
    if not os.path.isfile(file_path):
        abort(404, description="File not found")
    
    return send_file(file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

