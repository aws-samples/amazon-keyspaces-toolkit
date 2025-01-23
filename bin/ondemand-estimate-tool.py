import re
import boto3
from datetime import datetime, timedelta, timezone
import statistics
import json
import argparse
from decimal import Decimal, getcontext


#
# --- HELPERS ---
#

"""
    Retrieve data points for a single CloudWatch metric (e.g. 'WriteThrottleEvent')
    within the specified time range, at the specified period (defaults to 1 hour).
    
    Returns a list of the chosen statistic (e.g., average) values for each period.
    """
def get_operation_metric_data_points(
    cloudwatch_client,
    metric_name,
    keyspace_name,
    table_name,
    operation,
    start_time,
    end_time,
    period=3600,
    statistic='Average'
):
    # Get the metric data points
    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/Cassandra',
        MetricName=metric_name,
        Dimensions=[{'Name': 'TableName', 'Value': table_name}, {'Name': 'Keyspace', 'Value': keyspace_name}, {'Name': 'Operation', 'Value': operation}],
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=[statistic]
    )

    # Sort datapoints by timestamp just in case
    data_points = sorted(response.get('Datapoints', []), key=lambda d: d['Timestamp'])

    # Extract the values from the data points
    values = [dp[statistic] for dp in data_points]
    return values

"""
    Retrieve data points for a single CloudWatch metric (e.g. 'ProvisionedReadCapacityUnits')
    within the specified time range, at the specified period (defaults to 1 hour).
    
    Returns a list of the chosen statistic (e.g., average) values for each period.
    """
def get_table_metric_data_points(
    cloudwatch_client,
    metric_name,
    keyspace_name,
    table_name,
    start_time,
    end_time,
    period=3600,
    statistic='Average'
):
    # Get the metric data points
    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/Cassandra',
        MetricName=metric_name,
        Dimensions=[{'Name': 'TableName', 'Value': table_name}, {'Name': 'Keyspace', 'Value': keyspace_name}],
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=[statistic]
    )

    # Sort datapoints by timestamp just in case
    data_points = sorted(response.get('Datapoints', []), key=lambda d: d['Timestamp'])

    # Extract the values from the data points
    values = [Decimal(dp[statistic]) for dp in data_points]
    return values

"""
    Total the number of throttles for all operations.
    """
def sum_all_throttles(insert_throttles, update_throttles, delete_throttles, select_throttles):
    
    total = 0;

    total += sum(insert_throttles) + sum(update_throttles) + sum(delete_throttles) + sum(select_throttles)
    
    # Cost = (RCU * read_rate + WCU * write_rate) * hours
    return (total)

"""
    Estimate cost in US$ for capacity over 'hours' hours.
    rcu, wcu are capacity units. 
"""
def estimate_cost(vals, price):
  
    return sum(val * price for val in vals)

def get_keyspaces_throughput_mode(client, keyspace_name, table_name):
    """
    Retrieve the throughputMode ('PAY_PER_REQUEST' or 'PROVISIONED') 
    for the specified Amazon Keyspaces table.
    """
 
    response = client.get_table(
        keyspaceName=keyspace_name,
        tableName=table_name
    )
    
    # Navigate into the response to find the throughputMode
    # The structure is: response['table']['capacitySpecification']['throughputMode']
    # table_info = response['capacitySpecification']
    capacity_spec = response.get('capacitySpecification', {})
    
    throughput_mode = capacity_spec.get('throughputMode', 'UNKNOWN')

    return throughput_mode

def get_keyspaces_pricing(pricing_client, region_name):
    
    response = pricing_client.get_products(
        ServiceCode='AmazonMCS',
        Filters=[
            {
                'Type': 'TERM_MATCH',
                'Field': 'regionCode',
                'Value': region_name
            }
        ],
        MaxResults=100
    )

    # The response includes 'PriceList', a list of JSON or stringified-JSON documents
    # describing the terms. You can parse it as needed.
    results = {}
    for price_item_json in response['PriceList']:
        price_item = json.loads(price_item_json)
        usageType = price_item.get('product', {}).get('attributes', {}).get('usagetype', '')
        pattern = r'^[A-Za-z0-9]{2}-|^[A-Za-z0-9]{3}-|^[A-Za-z0-9]{4}-'
        # Replace that pattern (if it exists at the beginning) with nothing.
        usageType = re.sub(pattern, '', usageType)

        for one_value in iter(price_item.get('terms', {}).get('OnDemand', {}).values()):
            for one_dimension in iter(one_value.get('priceDimensions', {}).values()):
                price =  one_dimension.get('pricePerUnit', {}).get('USD', '0.0')
                results.update({usageType: Decimal(price)})
        

    return results

"""
By default, analyzes the last 'days' (7) days of metrics for 
all tables in the specified region. 
"""
def main():
    # Set decimal precision to 10
    getcontext().prec = 10

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Generate a report from nodetool tablestats and nodetool info and row size sampler outputs.'
    )

   
    parser.add_argument('--number-of-days', help='Number of days in the past to look back', type=int, default=7)
    parser.add_argument('--region-name', help='The AWS region where you have Amazon Keyspaces usage',type=str, default='us-east-1')
    parser.add_argument('--single-keyspace', type=str, default=None,
                        help='Calculate a single keyspace. Leave out all other keyspaces')

    # Parse arguments
    args = parser.parse_args()

    region_name = args.region_name
    days = args.number_of_days
    single_keyspace = args.single_keyspace

    print(f"Estimating Amazon Keyspaces OnDemand costs using CloudWatch metrics for region {region_name} and {days} days")

    # Check if the region is China
    if region_name in ['cn-north-1', 'cn-northwest-1']:
        print("Amazon Keyspaces pricing is not available in China regions through the pricing api")
        exit(1)

    
    service_client = boto3.client('keyspaces', region_name=region_name)
    cloudwatch = boto3.client('cloudwatch', region_name=region_name)
    pricing_client = boto3.client('pricing', region_name=('ap-south-1' if region_name == 'ap-south-1' else 'us-east-1'))

    price_dictionary = get_keyspaces_pricing(pricing_client, region_name)

    # Determine default time range if none provided
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days)
    
    # List all tables
    all_tables = []

    ks_paginator = service_client.get_paginator('list_keyspaces')
    tbl_paginator = service_client.get_paginator('list_tables')

    # Iterate over all keyspaces and tables.
    # If a single keyspace is specified, only that keyspace is analyzed.
    # filter system tables
    # capture Provisioned tables
    for page in ks_paginator.paginate():
        for one_keyspace in page["keyspaces"]:
            one_keyspace_name = one_keyspace['keyspaceName']
            if single_keyspace == None or one_keyspace_name == single_keyspace:
                if one_keyspace_name not in ['system', 'system_auth', 'system_distributed', 'system_schema', 'system_traces', 'system_schema_mcs', 'system_multiregion_info' ]:
                    for table_page in tbl_paginator.paginate(keyspaceName=one_keyspace_name):
                        for one_table in table_page["tables"]:
                            one_table_name = one_table["tableName"]
                            throughput_mode = get_keyspaces_throughput_mode(client=service_client, keyspace_name=one_keyspace_name, table_name=one_table_name)
                            if(throughput_mode == 'PROVISIONED'):
                                all_tables.append({'keyspaceName': one_keyspace_name, 'tableName': one_table["tableName"], 'throughputMode': throughput_mode})

    
    if not all_tables:
        print("No provisioned capacity mode tables found in this account/region/keyspace")
        return

    period = 3600  # 1-hour granularity
    # total_hours = (end_time - start_time).total_seconds() / 3600.0

    print(f"Analyzing tables in region {region_name} from {start_time} to {end_time}")
    
    print(
            f"{'Keyspace':20s} "
            f"{'Table':30s} "
            f"{'current mode':17s} "
            f"{'provisioned reads':>17s}  "
            f"{'provisioned writes':>17s}  "
            f"{'ondemand reads':>17s}  "
            f"{'ondemand writes':>17s}  "
            f"{'provision estimate':>17s}  "
            f"{'ondemand estimate':>17s}  "
            f"{'total throttles':>17s}  "
            f"{'ondemand savings':>17s}  "
        )
    # For each table, gather data
    for one_table in all_tables:
        table_name = one_table["tableName"]
        keyspace_name = one_table["keyspaceName"]
        throughput_mode = one_table["throughputMode"]

        # Fetch Provisioned & Consumed metrics
        prov_read_vals = get_table_metric_data_points(cloudwatch, 'ProvisionedReadCapacityUnits', keyspace_name, table_name, start_time, end_time, period)
        prov_write_vals = get_table_metric_data_points(cloudwatch, 'ProvisionedWriteCapacityUnits', keyspace_name, table_name, start_time, end_time, period)
        cons_read_vals = get_table_metric_data_points(cloudwatch, 'ConsumedReadCapacityUnits', keyspace_name, table_name, start_time, end_time, period, 'Sum')
        cons_write_vals = get_table_metric_data_points(cloudwatch, 'ConsumedWriteCapacityUnits', keyspace_name, table_name, start_time, end_time, period, 'Sum')

        # Fetch Throttle metrics
        total_insert_throttles = get_operation_metric_data_points(cloudwatch, 'WriteThrottleEvents', keyspace_name, table_name, 'INSERT', start_time, end_time, period, 'Sum')
        total_update_throttles = get_operation_metric_data_points(cloudwatch, 'WriteThrottleEvents', keyspace_name, table_name, 'UPDATE', start_time, end_time, period, 'Sum')
        total_delete_throttles = get_operation_metric_data_points(cloudwatch, 'WriteThrottleEvents', keyspace_name, table_name, 'DELETE', start_time, end_time, period, 'Sum')
        total_select_throttles = get_operation_metric_data_points(cloudwatch, 'ReadThrottleEvents', keyspace_name, table_name, 'SELECT', start_time, end_time, period, 'Sum')
        
        # Calculate total throttles
        total_throttles = sum_all_throttles(total_insert_throttles, total_update_throttles, total_delete_throttles, total_select_throttles)
        
        # Estimate provisioned costs
        provision_read_cost = estimate_cost(prov_read_vals, price_dictionary.get('ReadCapacityUnit-Hrs'))
        provision_write_cost = estimate_cost(prov_write_vals, price_dictionary.get('WriteCapacityUnit-Hrs'))

        # Estimate on-demand costs
        ondemand_read_cost = estimate_cost(cons_read_vals, price_dictionary.get('ReadRequestUnits'))
        ondemand_write_cost = estimate_cost(cons_write_vals, price_dictionary.get('WriteRequestUnits'))

        # Calculate total costs
        provision_total_cost = provision_read_cost + provision_write_cost
        ondemand_total_cost  = ondemand_read_cost + ondemand_write_cost

        # Difference = On-Demand total minus Provisioned total
        # Negative => on-demand is cheaper
        ondemand_difference = (( provision_total_cost - ondemand_total_cost ) / provision_total_cost) * 100 if provision_total_cost > 0.0 else 0.0
        
        # Print one CSV row
        print(
            f"{keyspace_name:<20s} "
            f"{table_name:<30s} "
            f"{throughput_mode:<17s} "
            f"{provision_read_cost:>17.2f} $"
            f"{provision_write_cost:>17.2f} $"
            f"{ondemand_read_cost:>17.2f} $"
            f"{ondemand_write_cost:>17.2f} $"
            f"{provision_total_cost:>17.2f} $"
            f"{ondemand_total_cost:>17.2f} $"
            f"{total_throttles:>17.0f} "
            f"{ondemand_difference:>17.2f} %"
        )
        
#
# --- RUN EXAMPLE ---
#
if __name__ == '__main__':
    # Default: last 7 days, US East-1
    main()

