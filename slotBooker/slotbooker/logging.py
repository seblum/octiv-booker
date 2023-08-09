import os
import sys
from datetime import datetime


def setup_log_dir() -> str:
    """
    Creates a directory for logs if it doesn't exist and generates a log file path based on the current date and time.

    Returns:
        str: Path to the generated log file.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    exact_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dir_log_file = f'{log_dir}/logs_{exact_datetime}.log'
    return dir_log_file

def start_logging() -> tuple[object, object]:
    """Start logging by redirecting stdout to a log file.

    This function creates a log directory named 'logs' if it doesn't exist and sets up
    logging to a new log file with a filename containing the current date and time.

    Returns:
        tuple: A tuple containing three objects: the log file object, the original stdout object,
        and the path of the created log file.

    Example:
        To start logging, call the function and capture the returned objects:

        >>> log_file, original_stdout, log_file_path = start_logging()
        >>> print("This message will be written to the log file.")
        >>> log_file.close()
        >>> sys.stdout = original_stdout  # Restore the original stdout after logging is done.
    """
    dir_log_file = setup_log_dir()
    orig_stdout = sys.stdout
    file = open(dir_log_file, "a+")
    sys.stdout = file
    print("-" * 5, datetime.now(), "-" * 5)
    print("\n<>")
    return file, orig_stdout, dir_log_file


def stop_logging(file: object, orig_stdout: object) -> None:
    """Stop logging and restore the original stdout.

    This function closes the log file and restores the original stdout so that subsequent
    print statements are displayed in the console as usual.

    Args:
        file (object): The log file object that was returned from 'start_logging'.
        orig_stdout (object): The original stdout object that was returned from 'start_logging'.

    Returns:
        None: This function does not return anything.

    Example:
        To stop logging and restore the original stdout, call the function with the log file object
        and the original stdout object obtained from 'start_logging':

        >>> stop_logging(log_file, original_stdout)
    """
    print("<>")
    sys.stdout = orig_stdout
    file.close()
