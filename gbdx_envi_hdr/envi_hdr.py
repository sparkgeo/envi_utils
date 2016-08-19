import os
import glob2

from gbdx_task_interface import GbdxTaskInterface


class EnviHdr(GbdxTaskInterface):

    def invoke(self):
        


if __name__ == "__main__":
    with AOPToEnviHdr() as task:
        task.invoke()
