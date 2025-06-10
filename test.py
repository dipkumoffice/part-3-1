import boto3
import logging
import json
import os
from datetime import datetime, timezone, timedelta
from botocore.exceptions import ClientError

# --- Configurable via env ---
REGION = os.getenv("AWS_REGION", "us-east-1")
DRY_RUN_MODE = os.getenv("DRY_RUN", "true").lower() == "true"


MAX_RUNNING_MINUTES = int(
    os.getenv("MAX_RUNNING_MINUTES", "10"))  # Default: 10 minutes
CPU_UTIL_THRESHOLD = float(
    os.getenv("CPU_UTIL_THRESHOLD", "0.01"))  # Default: 0.01%``
CPU_LOOKBACK_MINUTES = int(
    os.getenv("CPU_LOOKBACK_MINUTES", "15"))  # Check past 15 minutes

# --- Logging setup ---
logging.basicConfig(filename="ec2_test_audit.log", level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")

ec2 = boto3.client("ec2", region_name=REGION)
cw = boto3.client("cloudwatch", region_name=REGION)


def list_instances():
    try:
        res = ec2.describe_instances()
        return [i for r in res["Reservations"] for i in r["Instances"]]
    except Exception as e:
        logging.error(f"Unable to describe instances: {e}")
        return []


def get_uptime_minutes(launch_time):
    now = datetime.now(timezone.utc)
    return int((now - launch_time).total_seconds() / 60)


def is_not_permanent(tags):
    for tag in tags or []:
        if tag["Key"].lower() == "permanent" and tag["Value"].lower() == "true":
            return False
    return True


def get_recent_cpu_avg(instance_id):
    try:
        end = datetime.now(timezone.utc)
        start = end - timedelta(minutes=CPU_LOOKBACK_MINUTES)

        response = cw.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start,
            EndTime=end,
            Period=60,  # every minute
            Statistics=['Average']
        )

        datapoints = response.get('Datapoints', [])
        if not datapoints:
            return 100  # default to busy if no data

        avg_cpu = sum(dp['Average'] for dp in datapoints) / len(datapoints)
        return round(avg_cpu, 4)

    except Exception as e:
        logging.warning(f"Could not fetch CPU for {instance_id}: {e}")
        return 100


def stop_ec2_instance(instance_id):
    print("This EC2 instance will be stopped :", instance_id)
    try:
        ec2.stop_instances(InstanceIds=[instance_id], DryRun=DRY_RUN_MODE)
        logging.info(
            f"[DRY-RUN={DRY_RUN_MODE}] Requested stop for {instance_id}")
    except ClientError as e:
        if 'DryRunOperation' in str(e):
            logging.info(f"Dry-run passed for stopping {instance_id}")
        else:
            logging.error(f"Failed to stop {instance_id}: {e}")


def test_audit():
    results = []
    for inst in list_instances():
        iid = inst['InstanceId']
        print("EC2 instance ID", iid)
        age_mins = get_uptime_minutes(inst['LaunchTime'])
        print(age_mins)
        cpu_avg = get_recent_cpu_avg(iid)
        is_flagged = age_mins > MAX_RUNNING_MINUTES and cpu_avg < CPU_UTIL_THRESHOLD
        should_act = is_flagged and is_not_permanent(inst.get('Tags'))

        results.append({
            "InstanceId": iid,
            "AgeMinutes": age_mins,
            "CPU(%)": cpu_avg,
            "Flagged": is_flagged,
            "ActionTaken": should_act
        })

        if should_act:
            stop_ec2_instance(iid)

    with open("test_report.txt", "w") as f:
        for r in results:
            f.write(
                f"{r['InstanceId']} | Age: {r['AgeMinutes']}m | CPU: {r['CPU(%)']}% | Flagged: {r['Flagged']}\n")

    with open("test_output.json", "w") as jf:
        json.dump(results, jf, indent=2)

    print("Test audit complete. Results written to test_report.txt and test_output.json")


if __name__ == "__main__":
    test_audit()
