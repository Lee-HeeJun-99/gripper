# Next checkpoint

Use external-drive workspace and Python `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`.
Read PROGRESS/STATUS and generated campaign summaries before running anything.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/research_build.py
$PY tools/research_trial.py profile --profile
```

Commands refuse existing output names;do not rerun unchanged failed prototypes.
After mathematical/API success and profile,compare history.01/.005/.0025/.00125,
Beam11/21/41 anddt without pooling compiled versions. Retain1%/.1% criteria,
including same-time friction loss,not only motion. Default4GiB/480s/max4children.
Actual experiment output/identity and current Git log identify the checkpoint.
