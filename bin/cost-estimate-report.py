import math
from math import isclose
from decimal import *
import argparse

# ## Overview
#
# This script analyzes metrics from Cassandra (or Amazon Keyspaces) by using the outputs of:
# - `nodetool tablestats`
# - `nodetool info`
# - A custom row size sampler.
#
# It then generates a report summarizing:
# - Compressed and uncompressed data sizes
# - Compression ratios
# - Read/write request units per second
# - TTL delete counts per second
#
# These metrics can help estimate Amazon Keyspaces costs and inform capacity planning.
# python3 cost-estimate-report.py \
#   --report-name "Keyspaces Cost Analysis" \
#   --table-stats-file tablestats_output.txt \
#   --info-file info_output.txt \
#   --row-size-file row_size_info.txt \
#   --number-of-nodes 6


# Parse row size file
def parse_row_size_info(lines):

    result = {}

    for line in lines:
        line = line.strip()
        # Skip lines that don't contain '=' or look like error lines
        if '=' not in line or 'NoHostAvailable' in line:
            continue

        # Split keyspace.table from the rest
        left, right = line.split('=', 1)
        key_name = left.strip()

        # The right side should be something like:
        # { lines: 1986, columns: 12, average: 849 bytes, ... }
        right = right.strip()
        if not right.startswith('{') or not right.endswith('}'):
            continue

        # Remove the braces
        inner = right[1:-1].strip()

        # Split by commas that separate fields
        # Each field looks like "lines: 1986" or "average: 849 bytes"
        fields = inner.split(',')

        value_dict = {}
        for field in fields:
            field = field.strip()
            if ': ' not in field:
                # Skip malformed fields
                continue
            k, v = field.split(':', 1)
            key = k.strip()
            val = v.strip()
            # Store as is (string), cast later as needed.
            value_dict[key] = val

        result[key_name] = value_dict

    return result
def parse_nodetool_info(lines):
    """
    Parse nodetool info output lines to extract the node's uptime in seconds.
    Returns the uptime as a Decimal.
    """
    uptime_seconds = Decimal(1)

    for line in lines:
        line = line.strip()
        # Look for the line containing "Uptime (seconds)"
        if "Uptime (seconds)" in line:
            # Format is something like: "Uptime (seconds): X"
            parts = line.split(':', 1)
            if len(parts) == 2:
                space_used_str = parts[1].strip()
                try:
                    uptime_seconds = Decimal(space_used_str)
                except ValueError:
                    # If parsing fails, default to one second
                    uptime_seconds = Decimal(1)
    # If not found, return 1 by default (1 second)
    return uptime_seconds


def parse_nodetool_output(lines):
    """
    Parse the nodetool cfstats/tablestats output and return a dictionary of keyspaces and their tables.
    The structure returned is:
    {
        keyspace_name: [
            (table_name, space_used (Decimal), compression_ratio (Decimal), write_count (Decimal), read_count (Decimal)),
            ...
        ],
        ...
    }

    We collect:
    - space_used: The live space used by the table (in bytes)
    - compression_ratio: The SSTable compression ratio (unitless)
    - write_count: The total number of local writes recorded
    - read_count: The total number of local reads recorded

    Assumes that each table block starts after a line "Keyspace : <ks>" and "Table: <tablename>"
    When all data is collected for a table, it is appended to the keyspace's list.
    """
    data = {}
    current_keyspace = None
    current_table = None
    space_used = None
    compression_ratio = None
    write_count = None
    read_count = None

    for line in lines:
        line = line.strip()

        # Identify when we start a new keyspace block
        if line.startswith("Keyspace"):
            # Format: "Keyspace : keyspace_name"
            parts = line.split(':', 1)
            if len(parts) == 2:
                current_keyspace = parts[1].strip()
                # Initialize the keyspace in the dictionary if new
                if current_keyspace not in data:
                    data[current_keyspace] = []
            else:
                current_keyspace = None
            current_table = None

        # Identify when we start a new table block within the current keyspace
        if current_keyspace and (line.startswith("Table:") or line.startswith("Table (index):")):
            # Format: "Table: table_name"
            parts = line.split(':', 1)
            if len(parts) == 2:
                current_table = parts[1].strip()
                # Reset collected stats for this new table
                space_used = None
                compression_ratio = None
                write_count = None
                read_count = None

        # For lines within a table block, parse the required stats
        if current_keyspace and current_table:
            if "Space used (live):" in line:
                # Format: "Space used (live): X"
                parts = line.split(':', 1)
                if len(parts) == 2:
                    space_used_str = parts[1].strip()
                    try:
                        space_used = Decimal(space_used_str)
                    except ValueError:
                        space_used = Decimal(0)

            elif "SSTable Compression Ratio:" in line:
                # Format: "SSTable Compression Ratio: X"
                parts = line.split(':', 1)
                if len(parts) == 2:
                    ratio_str = parts[1].strip()
                    try:
                        compression_ratio = Decimal(ratio_str)
                    except ValueError:
                        compression_ratio = Decimal(1)

            elif "Local read count:" in line:
                # Format: "Local read count: X"
                parts = line.split(':', 1)
                if len(parts) == 2:
                    read_str = parts[1].strip()
                    try:
                        read_count = Decimal(read_str)
                    except ValueError:
                        read_count = Decimal(0)

            elif "Local write count:" in line:
                # Format: "Local write count: X"
                parts = line.split(':', 1)
                if len(parts) == 2:
                    write_str = parts[1].strip()
                    try:
                        write_count = Decimal(write_str)
                    except ValueError:
                        write_count = Decimal(0)

                # After identifying a write_count line, we expect that we now have all necessary metrics.
                # Only store the table data once all required fields (space_used, compression_ratio, read_count, write_count) are found.
                if (space_used is not None and
                        compression_ratio is not None and
                        read_count is not None and
                        write_count is not None):
                    data[current_keyspace].append(
                        (current_table, space_used, compression_ratio, read_count, write_count))

                    # Reset for the next table
                    current_table = None
                    space_used = None
                    compression_ratio = None
                    write_count = None
                    read_count = None

    return data


def print_data(report_name, data, uptime_sec, row_size_data, number_of_nodes=Decimal(1), filter_keyspace=None):
    """
    Print the requested output. The output format is:

    For each keyspace (or just the filtered one, if provided):
      - Print a header row
      - For each table:
          Keyspace, Table, Compressed Bytes, Ratio, Uncompressed Bytes, Writes RPS, Reads RPS
      - Print a subtotal row for the keyspace in GB

    After printing all keyspaces:
      - Print a summary row for system keyspaces and user keyspaces.

    System keyspaces are predefined in a set and are aggregated separately from user keyspaces.

    RPS (Requests Per Second) is calculated using the total reads/writes divided by the cluster uptime.
    """
    # Define a set of system keyspaces that we want to sum separately from application tables
    system_keyspaces = {
        'OpsCenter', 'dse_insights_local', 'solr_admin',
        'dse_system', 'HiveMetaStore', 'system_auth',
        'dse_analytics', 'system_traces', 'dse_audit', 'system',
        'dse_system_local', 'dsefs', 'system_distributed', 'system_schema',
        'dse_perf', 'dse_insights', 'system_backups', 'dse_security',
        'dse_leases'
    }

    # Initialize counters for system keyspaces
    total_system_compressed = Decimal(0)
    total_system_uncompressed = Decimal(0)
    total_system_writes = Decimal(0)
    total_system_reads = Decimal(0)

    # Initialize counters for user (non-system) keyspaces
    total_dev_compressed = Decimal(0)
    total_dev_uncompressed = Decimal(0)
    total_dev_writes = Decimal(0)
    total_dev_reads = Decimal(0)
    total_dev_ttls = Decimal(0)

    # Determine which keyspaces to print based on filter_keyspace
    keyspaces_to_print = [filter_keyspace] if filter_keyspace else data.keys()

    for keyspace in keyspaces_to_print:
        # If the keyspace doesn't exist in data or has no tables, skip it
        if keyspace not in data or not data[keyspace]:
            continue

        # Print header for this keyspace
        header = (f"{'Keyspace':40s} {'Table':100s} {'Compressed Bytes':<20s} "
                  f"{'Ratio':<10s} {'Uncompressed Bytes':<25s} {'Writes Unit p/s':<20s} {'Reads Unit p/s':<20s} {'TTL deletes p/s':<20s} {'Row size bytes':<10s}")
        print(header)
        print("-" * len(header))

        # Counters for the current keyspace
        total_compressed = Decimal(0)
        total_uncompressed = Decimal(0)
        total_writes = Decimal(0)
        total_reads = Decimal(0)
        total_ttls = Decimal(0)

        for (table, space_used, ratio, read_count, write_count) in data[keyspace]:
            # Handle invalid or zero compression ratio by using 1
            if ratio <= 0 or isclose(ratio, 0):
                ratio = Decimal(1)

            # Uncompressed size = compressed size / ratio
            uncompressed_size = space_used / ratio

            # Update keyspace totals
            total_compressed += space_used
            total_uncompressed += uncompressed_size

            fully_qualified_table_name = keyspace + "." + table;

            if fully_qualified_table_name in row_size_data:
                # Get the average string, e.g. "849 bytes"
                avg_str = row_size_data[fully_qualified_table_name].get('average', '0 bytes')

                # Parse out the number before 'bytes'
                # This assumes the format is always "<number> bytes"
                avg_number_str = avg_str.split()[0]
                average_bytes = Decimal(avg_number_str)

                ttl_str = row_size_data[fully_qualified_table_name].get('default-ttl', 'y')
                has_ttl = (ttl_str.strip() == 'n')
            else:
                has_ttl = False
                average_bytes = Decimal(0)

            if average_bytes < 1024:
                write_unit_per_write = Decimal(1)
            else:
                write_unit_per_write = math.ceil(average_bytes/Decimal(1024))

            if average_bytes < 4096:
                read_unit_per_read = Decimal(1)
            else:
                read_unit_per_read = math.ceil(average_bytes/Decimal(4096))

            write_units = write_count * write_unit_per_write
            ttl_units   = write_units if has_ttl else 0

            read_units = read_count * read_unit_per_read

            total_writes += write_units
            total_reads += read_units
            total_ttls += ttl_units
            # Print per-table line
            # Writes RPS and Reads RPS for individual tables are not shown individually here,
            # but we do show cumulative totals divided by uptime for the keyspace after all tables are processed.
            print(f"{keyspace:40s} {table:100s} {space_used:<20} {ratio:<14.5f} "
                  f"{uncompressed_size:<25.0f}{(write_units / uptime_sec):<20.0f}{(read_units / uptime_sec):<20.0f}{ttl_units/uptime_sec:<20.0f} {average_bytes:<10.0f}")

        print("-" * len(header))

        # Add this keyspace's totals to system or user totals
        if keyspace in system_keyspaces:
            total_system_compressed += total_compressed
            total_system_uncompressed += total_uncompressed
            total_system_writes += total_writes
            total_system_reads += total_reads
        else:
            total_dev_compressed += total_compressed
            total_dev_uncompressed += total_uncompressed
            total_dev_writes += total_writes
            total_dev_reads  += total_reads
            total_dev_ttls   += total_ttls

        # Compute a safe average ratio for the keyspace
        safe_avg_ratio = 1 if total_uncompressed <= 0 else (total_compressed / total_uncompressed)

        # Convert totals to GB for printing subtotals
        total_compressed_gb = total_compressed / Decimal(1000000000)
        total_uncompressed_gb = total_uncompressed / Decimal(1000000000)

        # Print keyspace subtotal line
        print(f"{'':100s} {keyspace + ' subtotal (GB)':<40s} {total_compressed_gb.normalize() :<21.4f}"
              f"{safe_avg_ratio:<15.5f}{total_uncompressed_gb.normalize():<25.4f}"
              f"{total_writes/uptime_sec:<20.0f}{total_reads/uptime_sec:<20.0f}{total_ttls/uptime_sec:<20.0f} \n")

    # After printing all keyspaces, print a summary row

    print("\n")
    summary_header = (f"{'Summary':109s} {'Node total': <30s} {'Compressed (GB)':<20s} "
                      f"{'Ratio(avg)':<14s} {'Uncompressed Size (GB)':<25s}{'Writes unit p/s':<20s} {'Reads unit p/s':<20s} {'TTL deletes p/s':<20s}")
    print(summary_header)
    print("-" * len(summary_header))

    # Calculate system totals in GB and average ratio
    avg_system_compression_ratio = total_system_compressed / total_system_uncompressed if total_system_uncompressed > 0 else Decimal(
        1)
    total_system_compressed_gb = total_system_compressed / Decimal(1000000000)
    total_system_uncompressed_gb = total_system_uncompressed / Decimal(1000000000)

    # Print system keyspaces summary line
    print(f"{'':110s}{'system':<30} {total_system_compressed_gb:<20.2f} {avg_system_compression_ratio:<14.5f} "
          f"{total_system_uncompressed_gb:<25.2f}{(total_system_writes / uptime_sec):<20.0f}{(total_system_reads / uptime_sec):<20.0f} \n")

    # Calculate user totals in GB and average ratio
    avg_dev_compression_ratio = total_dev_compressed / total_dev_uncompressed if total_dev_uncompressed > 0 else Decimal(
        1)
    total_dev_compressed_gb = total_dev_compressed / Decimal(1000000000)
    total_dev_uncompressed_gb = total_dev_uncompressed / Decimal(1000000000)

    # Print user keyspaces summary line
    print(f"{'':110s}{'user':<30} {total_dev_compressed_gb:<20.2f} {avg_dev_compression_ratio:<15.5f}"
          f"{total_dev_uncompressed_gb:<25.2f}{(total_dev_writes / uptime_sec):<20.0f}{(total_dev_reads / uptime_sec):<20.0f}{(total_dev_ttls / uptime_sec):<20.0f} \n")

    print("\n")

    summary_header = (f"{report_name +' Summary':109s} {'Cluster of nodes:' + str(number_of_nodes): <30s} {'Compressed (GB)':<20s} "
                      f"{'Ratio(avg)':<14s} {'Uncompressed Size (GB)':<25s}{'Writes unit p/s':<20s} {'Reads unit p/s':<20s} {'TTL deletes p/s':<20s}")
    print(summary_header)
    print("-" * len(summary_header))

    cluster_dev_compressed_gb = (total_dev_compressed_gb* number_of_nodes)/Decimal(3)
    cluster_dev_uncompressed_gb = (total_dev_uncompressed_gb*number_of_nodes)/Decimal(3)
    cluster_dev_writes = ((total_dev_writes * number_of_nodes)/uptime_sec)/Decimal(3)
    cluster_dev_ttls = ((total_dev_ttls * number_of_nodes) / uptime_sec) / Decimal(3)
    cluster_dev_reads = ((total_dev_reads * number_of_nodes) / uptime_sec) / Decimal(3)

    print(f"{'':110s}{'user':<30} {cluster_dev_compressed_gb:<20.2f} {avg_dev_compression_ratio:<15.5f}"
          f"{cluster_dev_uncompressed_gb:<25.2f}{cluster_dev_writes:<20.0f}{cluster_dev_reads:<20.0f} {cluster_dev_ttls:<20.0f}\n")


def main():
    # Set decimal precision if needed
    getcontext().prec = 10

    parser = argparse.ArgumentParser(
        description='Generate a report from nodetool tablestats and nodetool info and row size sampler outputs.'
    )
    parser.add_argument('--report-name', help='Name of the generated report', default='Amazon Keyspaces sizing')
    parser.add_argument('--table-stats-file', help='Path to the nodetool tablestats output file', required=True)
    parser.add_argument('--info-file', help='Path to the nodetool info output file', required=True)
    parser.add_argument('--row-size-file', help='Path to the file containing row size information', required=True)
    parser.add_argument('--number-of-nodes', type=Decimal,
                        help='Number of nodes in the cluster (must be a number)', required=True)
    parser.add_argument('--single-keyspace', type=str, default=None,
                        help='Calculate a single keyspace. Leave out to calculate all keyspaces')

    # Parse arguments
    args = parser.parse_args()

    number_of_nodes = args.number_of_nodes
    report_name = args.report_name

    # Print parameters for debugging
    print("Parameters:", report_name, args.table_stats_file, args.info_file, args.row_size_file,
          number_of_nodes)

    # Read the tablestats output file
    with open(args.table_stats_file, 'r') as f:
        tablestat_lines = f.readlines()

    # Read the info output file
    with open(args.info_file, 'r') as f:
        info_lines = f.readlines()

    # Read the row size file
    with open(args.row_size_file, 'r') as f:
        row_size_lines = f.readlines()


    # Parse the nodetool cfstats data
    tablestats_data = parse_nodetool_output(tablestat_lines)
    # Parse the nodetool info data (to get uptime)
    info_data = parse_nodetool_info(info_lines)
    # Parse the rowsize data (to get uptime)
    row_size_data = parse_row_size_info(row_size_lines)

    # Print the compiled data
    print_data(report_name, tablestats_data, info_data, row_size_data, number_of_nodes)

if __name__ == "__main__":
    main()
