import os
from awscli.clidriver import create_clidriver


def aws_cli(*cmd):
    """
    aws_cli invokes the aws cli processes in python to execute awscli commands.

    .. warning::
        This is not the most elegant way of using awscli.
        However, it has been a convinient function in data science projects.

    :param *cmd: tuple of awscli command.

    .. admonition:: Examples
       :class: info
       AWS credential env variables should be configured before calling this function.
       The awscli command should be wrapped as a tuple. To download data from S3 to a local path, use
       >>> aws_cli(('s3', 'sync', 's3://s2-fpd/augmentation/', '/tmp/test'))
       Similarly, upload is done in the following way
       >>> # local_path = ''
       >>> # remote_path = ''
       >>> _aws_cli(('s3', 'sync', local_path, remote_path))

    .. admonition:: References
       :class: info
       This function is adapted from https://github.com/boto/boto3/issues/358#issuecomment-372086466
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
