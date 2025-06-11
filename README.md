This script helps audit and optionally stop AWS EC2 instances that have been running too long with very low CPU usage

## What it does

- Scans all EC2 instances in a region
- Flags instances that:
- Have been running for longer than a configured time (MAX_RUNNING_MINUTES)
- Have average CPU usage below a threshold (CPU_UTIL_THRESHOLD)
- Are not marked as "Permanent=true" in their tags
- Optionally stops these instances
- Logs all decisions and outputs both a text and JSON report
- Supports dry-run mode for safe testing


## 🛠️ Dependencies
- Python 3.x
- boto3 (pip install boto3)

##

| Variable               | Default     | Description                                          |
| ---------------------- | ----------- | ---------------------------------------------------- |
| `AWS_REGION`           | `us-east-1` | AWS region to run the audit                          |
| `DRY_RUN`              | `true`      | If `"true"`, no actual stop actions are performed    |
| `MAX_RUNNING_MINUTES`  | `10`        | Max allowed uptime (in minutes)                      |
| `CPU_UTIL_THRESHOLD`   | `0.01`      | Max allowed average CPU usage (%) over recent period |
| `CPU_LOOKBACK_MINUTES` | `15`        | How far back to check CPU metrics                    |




## Example: Run in Dry Mode
```
export MAX_RUNNING_MINUTES=10
export CPU_UTIL_THRESHOLD=0.01
export CPU_LOOKBACK_MINUTES=15
export AWS_REGION=us-east-1
export DRY_RUN=true
python3 ec2_audit.py
```

## Example: Run in Real Mode
```
export MAX_RUNNING_MINUTES=10
export CPU_UTIL_THRESHOLD=0.01
export CPU_LOOKBACK_MINUTES=15
export AWS_REGION=us-east-1
python3 ec2_audit.py
```


## 📁 Output Files
- test_report.txt: Human-readable summary
- test_output.json: Structured report of all evaluated instances
- ec2_test_audit.log: Detailed logs of the audit and actions



## 🔍 Sample Output (Text Report)

- i-0abcd1234ef5678gh | Age: 34m | CPU: 0.0012% | Flagged: True
- i-0abcd9876ef5432xy | Age: 5m  | CPU: 0.9021% | Flagged: False

## 🛑 Important Tag
To protect an instance from being stopped, tag it like this:
```
Key:    Permanent
Value:  true
```