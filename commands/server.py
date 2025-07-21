from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from .ratelimit import rate_limit
from .config import SSH_PORT
from commands.db import (
    add_server,
    get_servers_by_user,
    get_full_servers_by_user,
    delete_server_by_index,
    get_servers_with_ids,
    set_default_server,
    get_default_server,
)
import paramiko

SERVER_NAME, IP, USERNAME, PASSWORD = range(4)
SELECT_DELETE = 0
SELECT_CPU, SELECT_MEMORY, SELECT_DISK = range(4, 7)
SELECT_DEFAULT = 7
SELECT_PING = 8
SELECT_HEALTH = 9
@rate_limit
async def start_add_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["user_inputs"] = {}
    await update.message.reply_text("Please enter a name for your server:")
    return SERVER_NAME
@rate_limit
async def get_server_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("user_inputs", {})["server_name"] = update.message.text
    await update.message.reply_text("Enter the IP address of the server:")
    return IP
@rate_limit
async def get_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("user_inputs", {})["ip"] = update.message.text
    await update.message.reply_text("Enter the SSH username:")
    return USERNAME
@rate_limit
async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("user_inputs", {})["username"] = update.message.text
    await update.message.reply_text("Enter the SSH password:")
    return PASSWORD
@rate_limit
async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("user_inputs", {})["password"] = update.message.text
    inputs = context.user_data.get("user_inputs", {})
    add_server(
        update.effective_user.id,
        inputs.get("server_name"),
        inputs.get("ip"),
        inputs.get("username"),
        inputs.get("password")
    )
    context.user_data.pop("user_inputs", None)
    await update.message.reply_text("Server added successfully.")
    return ConversationHandler.END
@rate_limit
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END
@rate_limit
async def list_servers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    servers = get_servers_by_user(user_id)
    if not servers:
        await update.message.reply_text("You have no servers saved.")
        return
    message = "Your saved servers:\n\n"
    for i, (name, ip, username) in enumerate(servers, 1):
        message += f"{i}. Name: {name}\n   IP: {ip}\n   User: {username}\n\n"
    await update.message.reply_text(message[:4000])
@rate_limit
async def start_delete_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    servers = get_full_servers_by_user(user_id)
    if not servers:
        await update.message.reply_text("You have no servers saved.")
        return ConversationHandler.END
    context.user_data["servers"] = servers
    message = "Select the server number to delete:\n\n"
    for i, (name, ip, _, _) in enumerate(servers, 1):
        message += f"{i}. {name} ({ip})\n"
    await update.message.reply_text(message)
    return SELECT_DELETE
@rate_limit
async def handle_delete_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(update.message.text) - 1
        user_id = update.effective_user.id
        success = delete_server_by_index(user_id, index)
        if success:
            await update.message.reply_text("Server deleted successfully.")
        else:
            await update.message.reply_text("Invalid server number.")
    except Exception as e:
        await update.message.reply_text(f"Exception:\n{e}")
    return ConversationHandler.END
@rate_limit
async def start_get_cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    default = get_default_server(user_id)
    if default:
        _, ip, username, password = default
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip, port=SSH_PORT, username=username, password=password)
            _, stdout, _ = ssh.exec_command("top -bn1 | grep 'Cpu(s)'")
            cpu_line = stdout.read().decode()
            ssh.close()
            import re
            match = re.search(r'(\d+\.\d+)\s*id', cpu_line)
            if match:
                idle = float(match.group(1))
                used = 100 - idle
                await update.message.reply_text(f"CPU Usage: {used:.2f}%")
            else:
                await update.message.reply_text("Could not parse CPU usage.")
        except Exception as e:
            await update.message.reply_text(f"Exception:\n{e}")
        return ConversationHandler.END

    servers = get_full_servers_by_user(user_id)
    if not servers:
        await update.message.reply_text("You have no servers saved.")
        return ConversationHandler.END
    context.user_data["servers"] = servers
    message = "Select the server number to get CPU usage:\n\n"
    for i, (name, ip, _, _) in enumerate(servers, 1):
        message += f"{i}. {name} ({ip})\n"
    await update.message.reply_text(message)
    return SELECT_CPU
@rate_limit
async def handle_get_cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(update.message.text) - 1
        servers = context.user_data.get("servers", [])
        if index < 0 or index >= len(servers):
            await update.message.reply_text("Invalid server number.")
            return ConversationHandler.END
        _, ip, username, password = servers[index]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=SSH_PORT, username=username, password=password)
        _, stdout, _ = ssh.exec_command("top -bn1 | grep 'Cpu(s)'")
        cpu_line = stdout.read().decode()
        ssh.close()
        import re
        match = re.search(r'(\d+\.\d+)\s*id', cpu_line)
        if match:
            idle = float(match.group(1))
            used = 100 - idle
            await update.message.reply_text(f"CPU Usage: {used:.2f}%")
        else:
            await update.message.reply_text("Could not parse CPU usage.")
    except Exception as e:
        await update.message.reply_text(f"Exception:\n{e}")
    return ConversationHandler.END@rate_limit

@rate_limit
async def start_get_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    default = get_default_server(user_id)
    if default:
        _, ip, username, password = default
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip, port=22, username=username, password=password)
            _, stdout, _ = ssh.exec_command("free -m | grep Mem")
            mem_line = stdout.read().decode()
            ssh.close()

            parts = mem_line.split()
            total = int(parts[1])
            used = int(parts[2])
            usage_percent = (used / total) * 100

            await update.message.reply_text(
                f"Memory Usage:\nUsed: {used} MB\nTotal: {total} MB\nPercent: {usage_percent:.2f}%"
            )
        except Exception as e:
            await update.message.reply_text(f"Exception:\n{e}")
        return ConversationHandler.END

    servers = get_full_servers_by_user(user_id)
    if not servers:
        await update.message.reply_text("You have no servers saved.")
        return ConversationHandler.END
    context.user_data["servers"] = servers
    message = "Select the server number to get Memory usage:\n\n"
    for i, (name, ip, _, _) in enumerate(servers, 1):
        message += f"{i}. {name} ({ip})\n"
    await update.message.reply_text(message)
    return SELECT_MEMORY
@rate_limit
async def handle_get_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(update.message.text) - 1
        servers = context.user_data.get("servers", [])
        if index < 0 or index >= len(servers):
            await update.message.reply_text("Invalid server number.")
            return ConversationHandler.END
        _, ip, username, password = servers[index]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=22, username=username, password=password)
        _, stdout, _ = ssh.exec_command("free -m | grep Mem")
        mem_line = stdout.read().decode()
        ssh.close()

        parts = mem_line.split()
        total = int(parts[1])
        used = int(parts[2])
        usage_percent = (used / total) * 100

        await update.message.reply_text(
            f"Memory Usage:\nUsed: {used} MB\nTotal: {total} MB\nPercent: {usage_percent:.2f}%"
        )
    except Exception as e:
        await update.message.reply_text(f"Exception:\n{e}")
    return ConversationHandler.END
@rate_limit
async def start_set_default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    servers = get_servers_with_ids(user_id)
    if not servers:
        await update.message.reply_text("You have no servers saved.")
        return ConversationHandler.END
    context.user_data["servers_with_ids"] = servers
    message = "Select the server number to set as default:\n\n"
    for i, (_, name, ip, _, _) in enumerate(servers, 1):
        message += f"{i}. {name} ({ip})\n"
    await update.message.reply_text(message)
    return SELECT_DEFAULT
@rate_limit
async def start_get_disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    default = get_default_server(user_id)
    if default:
        _, ip, username, password = default
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip, port=SSH_PORT, username=username, password=password)
            _, stdout, _ = ssh.exec_command("df -h / | tail -n 1")
            disk_line = stdout.read().decode()
            ssh.close()

            parts = disk_line.split()
            total = parts[1]
            used = parts[2]
            percent = parts[4]

            await update.message.reply_text(
                f"Disk Usage:\nUsed: {used}B\nTotal: {total}B\nPercent: {percent}"
            )
        except Exception as e:
            await update.message.reply_text(f"Exception:\n{e}")
        return ConversationHandler.END

    servers = get_full_servers_by_user(user_id)
    if not servers:
        await update.message.reply_text("You have no servers saved.")
        return ConversationHandler.END
    context.user_data["servers"] = servers
    message = "Select the server number to get Disk usage:\n\n"
    for i, (name, ip, _, _) in enumerate(servers, 1):
        message += f"{i}. {name} ({ip})\n"
    await update.message.reply_text(message)
    return SELECT_DISK
@rate_limit
async def handle_get_disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(update.message.text) - 1
        servers = context.user_data.get("servers", [])
        if index < 0 or index >= len(servers):
            await update.message.reply_text("Invalid server number.")
            return ConversationHandler.END
        _, ip, username, password = servers[index]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=SSH_PORT, username=username, password=password)
        _, stdout, _ = ssh.exec_command("df -h / | tail -n 1")
        disk_line = stdout.read().decode()
        ssh.close()

        parts = disk_line.split()
        total = parts[1]
        used = parts[2]
        percent = parts[4]

        await update.message.reply_text(
            f"Disk Usage:\nUsed: {used}B\nTotal: {total}B\nPercent: {percent}"
        )
    except Exception as e:
        await update.message.reply_text(f"Exception:\n{e}")
    return ConversationHandler.END
@rate_limit
async def handle_set_default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(update.message.text) - 1
        servers = context.user_data.get("servers_with_ids", [])
        if index < 0 or index >= len(servers):
            await update.message.reply_text("Invalid server number.")
            return ConversationHandler.END
        rowid, name, *_ = servers[index]
        set_default_server(update.effective_user.id, rowid)
        await update.message.reply_text(f"Default server set to {name}.")
    except Exception as e:
        await update.message.reply_text(f"Exception:\n{e}")
    return ConversationHandler.END
@rate_limit
async def start_get_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    default = get_default_server(user_id)
    if default:
        _, ip, _, _ = default
        try:
            import subprocess
            result = subprocess.run(["ping", "-c", "4", ip], capture_output=True, text=True)
            if result.returncode == 0:
                await update.message.reply_text(f"Ping results for {ip}:\n{result.stdout}")
            else:
                await update.message.reply_text(f"Error pinging {ip}:\n{result.stderr}")
        except Exception as e:
            await update.message.reply_text(f"Exception:\n{e}")
        return ConversationHandler.END

    servers = get_full_servers_by_user(user_id)
    if not servers:
        await update.message.reply_text("You have no servers saved.")
        return ConversationHandler.END
    context.user_data["servers"] = servers
    message = "Select the server number to ping:\n\n"
    for i, (name, ip, _, _) in enumerate(servers, 1):
        message += f"{i}. {name} ({ip})\n"
    await update.message.reply_text(message)
    return SELECT_PING

@rate_limit
async def handle_get_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(update.message.text) - 1
        servers = context.user_data.get("servers", [])
        if index < 0 or index >= len(servers):
            await update.message.reply_text("Invalid server number.")
            return ConversationHandler.END
        _, ip, _, _ = servers[index]
        import subprocess
        result = subprocess.run(["ping", "-c", "4", ip], capture_output=True, text=True)
        if result.returncode == 0:
            await update.message.reply_text(f"Ping results for {ip}:\n{result.stdout}")
        else:
            await update.message.reply_text(f"Error pinging {ip}:\n{result.stderr}")
    except Exception as e:
        await update.message.reply_text(f"Exception:\n{e}")
    return ConversationHandler.END
@rate_limit
async def start_get_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    default = get_default_server(user_id)
    if default:
        name, ip, username, password = default
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=ip, port=SSH_PORT, username=username, password=password)
            _, cpu_stdout, _ = ssh.exec_command("top -bn1 | grep 'Cpu(s)'")
            _, mem_stdout, _ = ssh.exec_command("free -m | grep Mem")
            _, disk_stdout, _ = ssh.exec_command("df -h / | tail -n 1")
            cpu_line = cpu_stdout.read().decode()
            mem_line = mem_stdout.read().decode()
            disk_line = disk_stdout.read().decode()
            ssh.close()

            import re
            cpu_match = re.search(r'(\d+\.\d+)\s*id', cpu_line)
            cpu_usage = None
            if cpu_match:
                idle = float(cpu_match.group(1))
                cpu_usage = 100 - idle

            mem_parts = mem_line.split()
            mem_total = int(mem_parts[1])
            mem_used = int(mem_parts[2])
            mem_percent = (mem_used / mem_total) * 100

            disk_parts = disk_line.split()
            disk_total = disk_parts[1]
            disk_used = disk_parts[2]
            disk_percent = disk_parts[4]

            message = "Server ALL:\n"
            if cpu_usage is not None:
                message += f"CPU Usage: {cpu_usage:.2f}%\n"
            else:
                message += "CPU Usage: N/A\n"
            message += (
                f"Memory: {mem_used} MB / {mem_total} MB ({mem_percent:.2f}%)\n"
            )
            message += (
                f"Disk: {disk_used}B / {disk_total}B ({disk_percent})"
            )
            await update.message.reply_text(message)
        except Exception as e:
            await update.message.reply_text(f"Exception:\n{e}")
        return ConversationHandler.END

    servers = get_full_servers_by_user(user_id)
    if not servers:
        await update.message.reply_text("You have no servers saved.")
        return ConversationHandler.END
    context.user_data["servers"] = servers
    message = "Select the server number to check ALL:\n\n"
    for i, (name, ip, _, _) in enumerate(servers, 1):
        message += f"{i}. {name} ({ip})\n"
    await update.message.reply_text(message)
    return SELECT_HEALTH

@rate_limit
async def handle_get_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(update.message.text) - 1
        servers = context.user_data.get("servers", [])
        if index < 0 or index >= len(servers):
            await update.message.reply_text("Invalid server number.")
            return ConversationHandler.END
        name, ip, username, password = servers[index]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=SSH_PORT, username=username, password=password)
        _, cpu_stdout, _ = ssh.exec_command("top -bn1 | grep 'Cpu(s)'")
        _, mem_stdout, _ = ssh.exec_command("free -m | grep Mem")
        _, disk_stdout, _ = ssh.exec_command("df -h / | tail -n 1")
        cpu_line = cpu_stdout.read().decode()
        mem_line = mem_stdout.read().decode()
        disk_line = disk_stdout.read().decode()
        ssh.close()

        import re
        cpu_match = re.search(r'(\d+\.\d+)\s*id', cpu_line)
        cpu_usage = None
        if cpu_match:
            idle = float(cpu_match.group(1))
            cpu_usage = 100 - idle

        mem_parts = mem_line.split()
        mem_total = int(mem_parts[1])
        mem_used = int(mem_parts[2])
        mem_percent = (mem_used / mem_total) * 100

        disk_parts = disk_line.split()
        disk_total = disk_parts[1]
        disk_used = disk_parts[2]
        disk_percent = disk_parts[4]

        message = f"ALL for {name}:\n"
        if cpu_usage is not None:
            message += f"CPU Usage: {cpu_usage:.2f}%\n"
        else:
            message += "CPU Usage: N/A\n"
        message += (
            f"Memory: {mem_used} MB / {mem_total} MB ({mem_percent:.2f}%)\n"
        )
        message += (
            f"Disk: {disk_used}B / {disk_total}B ({disk_percent})"
        )
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Exception:\n{e}")
    return ConversationHandler.END