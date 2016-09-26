import paramiko
import multiprocessing


genLocation = "C:/workspace/aggScript/src/test/resources/"
ssh = paramiko.SSHClient()

def worker(server, password, base_node, node):

    print("Connecting to " + server)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username="dms", password=password)

    #Connect to base node. We need a definite location to store the logs.
    print("Connecting to " + base_node)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("ssh " + base_node)

    #Connect to node being evaluated
    print("Connecting to " + node)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("ssh " + node)

    # Check if scripts exist
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("[ -d /apps/dms/installScript ] && echo true")

    if (ssh_stdout.readlines()):
        print(node + ": running chk scripts")

        # Run chk-log
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("/apps/dms/installScript/bin/chk-log.sh")

        # Save to file
        f = open(genLocation + node + ".chk-log.log", 'w')
        lines = ssh_stdout.readlines()
        for line in lines:
            f.write(line)
        f.close()

        # Run chk-data
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("/apps/dms/installScript/bin/chk-data.sh")

        # Save to file
        f = open(genLocation + node + ".chk-data.log", 'w')
        lines = ssh_stdout.readlines()
        for line in lines:
            f.write(line)
        f.close()
    else:
        print(node + ": Scripts don't exist on this server.")

        # We can add the scripts ourselves .. but not right now :)
    print("Exited " + node)
    return


if __name__ == '__main__':
    servers = ['dms-v2-dev2.cmc.ec.gc.ca', 'dw-dev1.cmc.ec.gc.ca']

    nodeMap = {}
    nodeMap['dms-v2-dev2.cmc.ec.gc.ca'] = ["dms-dev-host1","dms-dev-host2","dms-dev-host3","dms-dev-host4"]
    nodeMap['dw-dev1.cmc.ec.gc.ca'] = ["dw-dev1-host1", "dw-dev1-host2"]

    credentialMap = {}
    credentialMap['dms-v2-dev2.cmc.ec.gc.ca'] = ""
    credentialMap['dw-dev1.cmc.ec.gc.ca'] = ""
    jobs = []

    for server in servers:
        baseNode = nodeMap[server][0]
        password = credentialMap[server]
        for node in nodeMap[server]:
            p = multiprocessing.Process(target=worker, args=(server, password, baseNode, node))
            jobs.append(p)
            p.start()

