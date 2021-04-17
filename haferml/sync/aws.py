import os
from awscli.clidriver import create_clidriver
import boto3


def aws_cli(*cmd):
    """
    aws_cli invokes the aws cli processes in python to execute awscli commands.

    !!! warning
        This is not the most elegant way of using awscli.
        However, it has been a convinient function in data science projects.

        This function is adapted from https://github.com/boto/boto3/issues/358#issuecomment-372086466


    AWS credential env variables should be configured before calling this function.
    The awscli command should be wrapped as a tuple. To download data from S3 to a local path, use

    ```
    >>> aws_cli(('s3', 'sync', 's3://s2-fpd/augmentation/', '/tmp/test'))
    Similarly, upload is done in the following way
    >>> # local_path = ''
    >>> # remote_path = ''
    >>> _aws_cli(('s3', 'sync', local_path, remote_path))
    ```

    :param *cmd: tuple of awscli command.
    """
    old_env = dict(os.environ)
    try:
        # Set up environment
        env = os.environ.copy()
        env["LC_CTYPE"] = "en_US.UTF"
        os.environ.update(env)

        # Run awscli in the same process
        exit_code = create_clidriver().main(*cmd)

        # Deal with problems
        if exit_code > 0:
            raise RuntimeError(f"AWS CLI exited with code {exit_code}")
    finally:
        os.environ.clear()
        os.environ.update(old_env)


def s3_download(path, folder):
    """
    `s3_download` downloads files from S3.

    ```
    >>> s3_download(config_path, base_folder)
    ```

    :param path: s3 uri
    :type path: str
    :param folder: destination folder
    :type folder: str
    """

    if not path.startswith("s3://"):
        raise Exception(f"{path} is not S3 uri!")
    else:
        # e.g., s3://mein-work/abc/performance/model_performance_log.json
        s3_bucket = path.split("/")[2]
        s3_filepath = "/".join(path.split("/")[3:])
        # get the name of the config file
        s3_filename = path.split("/")[-1]
        # local config path is constructed from base folder and filename
        path = os.path.join(folder, s3_filename)
        s3 = boto3.client("s3")
        s3.download_file(s3_bucket, s3_filepath, path)
