#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pexpect  #expect命令模拟
import sys
import struct, fcntl, os, sys, signal
import termios
import configparser

class SSHLogin(object):
    def __init__(self):
        self.child = None
        self.cmd_list = []                  # ssh登入成功，想要执行的命令，按顺序执行

        self.machine_login_command = ''     # ssh 登录命令
        self.machine_login_password = ''    # ssh 登录密码
        self.cmd_list = []                  # 登录后要执行的命令

    def __call__(self, section, ini_file_name = 'ssh.ini'):
        self.init(section, ini_file_name)
        self.login()
        self.runComand()
        self._setWindowSize()
        self._interact()

    def init(self, section, ini_file_name):

        cfg = configparser.ConfigParser()

        if ini_file_name not in cfg.read(ini_file_name):
            raise Exception("读取配置文件错误，请检查{}是否存在".format(ini_file_name))

        try:

            ssh_login_user = cfg[section]['ssh_login_user']      # ssh 登录用户
            ssh_login_host = cfg[section].get('ssh_login_host', '127.0.0.1')
            ssh_login_port = cfg[section].get('ssh_login_port', '22')

            self.ssh_login_cmd = "ssh {0}@{1} -p {2}".format(ssh_login_user, ssh_login_host,ssh_login_port)

            self.ssh_login_pwd = cfg[section]['ssh_login_pwd']      # ssh 登录密码

            if cfg[section].get('welcome_info', None) is not None:  # 打印欢迎信息
                print(cfg[section]['welcome_info'])

            if cfg[section].get('ssh_logined_cmd', None) is None:
                self.cmd_list = []
            else:
                self.cmd_list = cfg[section]['ssh_logined_cmd'].split(',')

        except KeyError as e:
            raise Exception("配置文件({0})中{1}不存在{2}的配置".format(ini_file_name, section, e.message))

    def login(self):
        """
        登录
        """
        self.child = pexpect.spawn(self.ssh_login_cmd)

        self.child.expect(r"password:")

        self.child.sendline(self.ssh_login_pwd)

    def runComand(self):
        for cmd in self.cmd_list:
            self.sendCommand(cmd)

    def sendCommand(self, cmd):
        self.child.expect([r'#']) #命令提示符
        self.child.sendline(cmd)

    def _setWindowSize(self):

        # 控制子进程窗口的大小，使之适应当前窗口，pexcept会默认更改为固定值，会导致窗口过小，并会导致超过一行的输入出现问题
        winsize = self._getwinsize();
        self.child.setwinsize(winsize[0], winsize[1])
        signal.signal(signal.SIGWINCH, self._sigwinch_passthrough)

    def _interact(self):
        self.child.interact()

    def _getwinsize(self):
        """This returns the window size of the child tty.
        The return value is a tuple of (rows, cols).
        """
        if 'TIOCGWINSZ' in dir(termios):
            TIOCGWINSZ = termios.TIOCGWINSZ
        else:
            TIOCGWINSZ = 1074295912 # Assume
        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s)
        return struct.unpack('HHHH', x)[0:2]

    def _sigwinch_passthrough (self, sig, data):
        winsize = getwinsize()
        self.child.setwinsize(winsize[0],winsize[1])


if __name__ == "__main__":
    try:
        ssh = SSHLogin()
        ssh('qcloud')
    except Exception as e:
        print(e.message)

