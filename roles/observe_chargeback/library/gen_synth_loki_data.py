import logging
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Union

# --- Configure logging with a default level that can be changed ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger()

# --- Define constants for template placeholders ---
PLACEHOLDER_NANO = "NANOSECONDS"
PLACEHOLDER_START = "STARTTIME"
PLACEHOLDER_END = "ENDTIME"

def _format_timestamp(epoch_seconds: float) -> str:
    """
    Converts an epoch timestamp into a human-readable UTC string.

    Args:
        epoch_seconds (float): The timestamp in seconds since the epoch.

    Returns:
        str: The formatted datetime string (e.g., "2023-10-26T14:30:00 UTC").
    """
    try:
        dt_object = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
        return dt_object.strftime("%Y-%m-%dT%H:%M:%S %Z")
    except (ValueError, TypeError):
        logger.warning(f"Invalid epoch value provided: {epoch_seconds}")
        return "INVALID_TIMESTAMP"

def generate_loki_data(
    header_path: Path,
    template_path: Path,
    footer_path: Path,
    output_path: Path,
    start_time: datetime,
    end_time: datetime,
    time_step_seconds: int
):
    """
    Generates synthetic Loki log data from templates and writes it to a file.

    Args:
        header_path (Path): Path to the header template file.
        template_path (Path): Path to the log entry template file.
        footer_path (Path): Path to the footer template file.
        output_path (Path): Path for the generated output JSON file.
        start_time (datetime): The start time for data generation.
        end_time (datetime): The end time for data generation.
        time_step_seconds (int): The duration of each log entry in seconds.
    """
    # --- Step 1: Load template files ---
    try:
        logger.info(f"Loading header template from: {header_path}")
        header_template = header_path.read_text()

        logger.info(f"Loading log template from: {template_path}")
        log_template = template_path.read_text()

        logger.info(f"Loading footer template from: {footer_path}")
        footer_template = footer_path.read_text()
    except FileNotFoundError as e:
        logger.error(f"Error loading template file: {e}. Aborting.")
        raise # Re-raise the exception to be caught in main()

    # --- Step 2: Generate data and write to file ---
    logger.info(
        f"Generating data from {start_time.strftime('%Y-%m-%d')} to "
        f"{end_time.strftime('%Y-%m-%d')} with a {time_step_seconds}s step."
    )
    start_epoch = int(start_time.timestamp())
    end_epoch = int(end_time.timestamp())
    logger.debug(f"Time range in epoch seconds: {start_epoch} to {end_epoch}")

    try:
        with output_path.open('w') as f_out:
            f_out.write(header_template)

            # Loop through the time range and generate each log entry
            for current_epoch in range(start_epoch, end_epoch, time_step_seconds):
                end_of_step_epoch = current_epoch + time_step_seconds - 1

                # Prepare replacement values
                nanoseconds = int(current_epoch * 1_000_000_000)
                start_str = _format_timestamp(current_epoch)
                end_str = _format_timestamp(end_of_step_epoch)

                logger.debug(f"Processing epoch: {current_epoch} -> nanoseconds: {nanoseconds}")
                logger.debug(f"  - Start time: {start_str}")
                logger.debug(f"  - End time:   {end_str}")

                # Perform replacement on the template
                log_entry = log_template.replace(PLACEHOLDER_NANO, str(nanoseconds))
                log_entry = log_entry.replace(PLACEHOLDER_START, start_str)
                log_entry = log_entry.replace(PLACEHOLDER_END, end_str)

                f_out.write(log_entry)
            
            # Append the footer at the end of the file
            f_out.write(footer_template)

        logger.info(f"Successfully generated synthetic data to '{output_path}'")
    except IOError as e:
        logger.error(f"Failed to write to output file '{output_path}': {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during generation: {e}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic Loki log data from templates.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # --- Required File Path Arguments ---
    parser.add_argument("-o", "--output", required=True, help="Path to the output file.")
    parser.add_argument("--header", required=True, help="Path to the header template file.")
    parser.add_argument("--template", required=True, help="Path to the log entry template file.")
    parser.add_argument("--footer", required=True, help="Path to the footer template file.")

    # --- Optional Generation Arguments ---
    parser.add_argument("--days", type=int, default=30, help="How many days of data to generate, ending today.")
    parser.add_argument("--step", type=int, default=300, help="Time step in seconds for each log entry.")
    
    # --- Optional Utility Arguments ---
    parser.add_argument("--debug", action="store_true", help="Enable debug level logging for verbose output.")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled.")

    # Define the time range for data generation
    end_time_utc = datetime.now(timezone.utc)
    start_time_utc = end_time_utc - timedelta(days=args.days)
    logger.debug(f"Time range calculated: {start_time_utc} to {end_time_utc}")

    # Run the generator
    try:
        generate_loki_data(
            header_path=Path(args.header),
            template_path=Path(args.template),
            footer_path=Path(args.footer),
            output_path=Path(args.output),
            start_time=start_time_utc,
            end_time=end_time_utc,
            time_step_seconds=args.step
        )
    except FileNotFoundError:
        logger.error("Process aborted because a template file was not found.")
    except Exception as e:
        logger.critical(f"A critical, unhandled error stopped the script: {e}")


if __name__ == "__main__":
    main()

