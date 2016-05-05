import os, time
from threading import Lock
import neovim
import rospy
from rosgraph_msgs.msg import Log

LOG_LEVEL_NAMES = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
LOG_LEVEL_DICT = {Log.__dict__[name]: name for name in LOG_LEVEL_NAMES}
CONSOLE_BUFFER_NAME = 'ROS Console'

@neovim.plugin
class RosConsole(object):
    def __init__(self, nvim):
        rospy.init_node('neovim', anonymous=True)
        self._nvim = nvim
        self._nvim_lock = Lock()
        rospy.Subscriber('rosout', Log, self.add_log_message)

    def add_log_message(self, log_msg):
        print(log_msg.msg)
        log_line = '[{}] {}'.format(
                LOG_LEVEL_DICT[log_msg.level],
                log_msg.msg)
        with self._nvim_lock:
            for buf in self._nvim.buffers:
                print(str([buf.name, buf.valid]))
                # Neovim prepends the working directory to the buffer name, so we
                # ignore that and just check the end.
                if buf.valid and buf.name[-len(CONSOLE_BUFFER_NAME):] == CONSOLE_BUFFER_NAME:
                    buf.append(log_line)

    @neovim.command('RosConsole', range='', nargs='*', sync=True)
    def ros_console(self, args, range):
        self._nvim.current.buffer.name = CONSOLE_BUFFER_NAME

nvim = neovim.attach('socket', path=os.environ['NVIM_LISTEN_ADDRESS'])
console = RosConsole(nvim)
while True:
    time.sleep(1.0)
