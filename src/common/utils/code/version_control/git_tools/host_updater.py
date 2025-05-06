import os
import platform
import subprocess
import requests
from typing import List

class HostsUpdater:
    def __init__(self, hosts_url: str):
        """
        初始化 HostsUpdater 类
        :param hosts_url: 获取 hosts 内容的 URL
        """
        self.hosts_url = hosts_url
        # self.hosts_json_url = "https://raw.hellogithub.com/hosts.json"  # JSON 格式的 hosts URL
        self.hosts_json_url = "https://raw.hellogithub.com/hosts.json"  # JSON 格式的 hosts URL
        self.hosts_paths = {
            "Windows": r"C:\Windows\System32\drivers\etc\hosts",  # Windows 系统
            "Linux": "/etc/hosts",  # Linux 系统
            "Darwin": "/etc/hosts",  # Mac 系统
        }
        self.dns_flush_commands = {
            "Windows": ["ipconfig", "/flushdns"],  # Windows 刷新 DNS
            "Linux": ["sudo", "nscd", "restart"],  # Linux 刷新 DNS
            "Darwin": ["sudo", "killall", "-HUP", "mDNSResponder"],  # Mac 刷新 DNS
        }

    def get_hosts_content(self) -> List[str]:
        """从指定 URL 获取最新的 hosts 内容"""
        response = requests.get(self.hosts_url)  # 发送 HTTP 请求获取内容
        response.raise_for_status()  # 检查请求是否成功
        return response.text.splitlines()  # 将内容按行分割成列表

    def update_hosts_file(self, hosts_content: List[str]):
        """更新本机的 hosts 文件"""
        system = platform.system()  # 获取当前操作系统
        hosts_path = self.hosts_paths.get(system)  # 获取对应系统的 hosts 文件路径
        if not hosts_path:
            raise NotImplementedError(f"不支持的系统: {system}")  # 如果系统不支持，抛出异常

        # 备份现有的 hosts 文件内容
        with open(hosts_path, "r") as f:
            existing_content = f.read()

        # # 将新的 hosts 内容追加到文件末尾
        # with open(hosts_path, "a") as f:
        #     f.write("\n\n# GitHub520 Host Start\n")  # 添加起始标记
        #     f.write("\n".join(hosts_content))  # 写入新的 hosts 内容
        #     f.write("\n# GitHub520 Host End\n")  # 添加结束标记
        # 将新的 hosts 内容覆盖原文件内容
        with open(hosts_path, "w", encoding="utf-8") as f:
            f.write("\n\n# GitHub520 Host Start\n")  # 添加起始标记
            f.write("\n".join(hosts_content))  # 写入新的 hosts 内容
            f.write("\n# GitHub520 Host End\n")  # 添加结束标记
            

        print(f"Hosts 文件已更新，路径: {hosts_path}")

    def flush_dns(self):
        """根据系统刷新 DNS 缓存"""
        system = platform.system()  # 获取当前操作系统
        command = self.dns_flush_commands.get(system)  # 获取对应系统的 DNS 刷新命令
        if not command:
            raise NotImplementedError(f"不支持的系统: {system}")  # 如果系统不支持，抛出异常

        try:
            subprocess.run(command, check=True)  # 执行 DNS 刷新命令
            print("DNS 缓存已刷新。")
        except subprocess.CalledProcessError as e:
            print(f"刷新 DNS 缓存失败: {e}")  # 如果命令执行失败，打印错误信息

    def test_connectivity(self):
        """测试 GitHub 域名的连通性"""
        test_domains = ["github.com", "raw.githubusercontent.com"]  # 要测试的域名列表
        for domain in test_domains:
            try:
                subprocess.run(["ping", "-c", "1", domain], check=True)  # 使用 ping 命令测试连通性
                print(f"成功连接到 {domain}")
            except subprocess.CalledProcessError as e:
                print(f"无法连接到 {domain}: {e}")  # 如果连接失败，打印错误信息

    def run(self):
        """执行完整的 hosts 更新流程"""
        try:
            # 第一步：获取最新的 hosts 内容
            print("正在获取最新的 hosts 内容...")
            hosts_content = self.get_hosts_content()

            # 第二步：更新本机的 hosts 文件
            print("正在更新 hosts 文件...")
            self.update_hosts_file(hosts_content)

            # 第三步：刷新 DNS 缓存
            print("正在刷新 DNS 缓存...")
            self.flush_dns()

            # 第四步：测试连通性
            print("正在测试连通性...")
            self.test_connectivity()

            print("Hosts 文件更新和连通性测试已完成。")
        except Exception as e:
            print(f"发生错误: {e}")  # 如果出现异常，打印错误信息


if __name__ == "__main__":
    # 初始化时传入 hosts URL
    # hosts_updater = HostsUpdater(hosts_url="https://raw.hellogithub.com/hosts")
    hosts_updater = HostsUpdater(hosts_url="https://gitee.com/if-the-wind/github-hosts/raw/main/hosts")
    hosts_updater.run()  # 执行更新流程