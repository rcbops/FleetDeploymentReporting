class JobRunningError(Exception):
    """Error for asynchronous task still running."""
    def __init__(self):
        super(JobRunningError, self).__init__('Job is still running.')


class JobError(Exception):
    """Error for asychronous task failed."""
    def __init__(self):
        super(JobError, self).__init__('Job failed.')
