# model-bringup-automation
Tools to enable testing multiple combinations of  configs for different models/tools and host a status page for the same

# Steps
1. python automate_configs.py
2. run python automate_runs.py and python backend_serve_status.py parallely

# Generate Configs and Run Commands
python automate_configs.py

## Modify automate_configs.py As Needed : Choose a Base Config
    base_config_file = 'exp_fp16_ND_difft_csx.yaml'

## Choose a base run Command
    base_run_sh = """#!/bin/bash
    config={config_file} 
    outdir={log_dir}
    mkdir -p $outdir
    mountdirs="/cra-614"
    namespace="cra-614-240"
    mode="train"

    HDF5_USE_FILE_LOCKING='FALSE' python run.py CSX \
        --params $config \
        --mode $mode \
        --model_dir $outdir \
        --mgmt_namespace $namespace \
        --mount_dirs $mountdirs \
        --disable_version_check \
        --compile_only 
    """

## Define parameters and options
    param_dict = {}
    param_dict['trainer.init.model.attention_module'] = ['diff_attention', 'aiayn_attention']
    param_dict['trainer.init.model.attention_activation'] = ['softmax', 'sigmoid']
    param_dict['trainer.init.model.num_hidden_layers'] = [12,4]
    param_dict['trainer.init.model.num_heads'] =  [12,4]
    param_dict['trainer.init.model.position_embedding_type'] = ['learned', 'alibi', {'position_embedding_type':'rotary', 'rope_theta':500000, 'rotary_dim':64}]
    param_dict['trainer.fit.train_dataloader.batch_size'] = [256,128,64,8]

## Define Exclusion Combinations
    exclusions = []
    exclusions.append({'trainer.init.model.attention_module': 'diff_attention', 'trainer.init.model.position_embedding_type': 'alibi'})


