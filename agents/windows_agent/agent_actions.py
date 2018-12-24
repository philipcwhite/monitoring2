import os, platform, socket, ssl, sqlite3, time

class AgentSettings:
    agent_path = 'C:\\Progra~1\\monitoring\\agent\\'
    agent_time = None
    agent_name = None
    server = '127.0.0.1'
    port = 8888
    secure = 0
    log = None
    services = []

class AgentSQL():
    def sql_con():
        try:
            database = AgentSettings.agent_path + 'agent_sqlite.db'
            con = sqlite3.connect(database, isolation_level=None)
            return con
        except: pass

    def create_tables():
        try:
            sql_create_agent_data = r"CREATE TABLE IF NOT EXISTS AgentData (time integer,name text,monitor text,value integer,sent integer);" 
            sql_create_agent_events = r"CREATE TABLE IF NOT EXISTS AgentEvents (time integer,name text,monitor text,message text,status integer,severity integer, sent integer);"
            sql_create_agent_thresholds = r"CREATE TABLE IF NOT EXISTS AgentThresholds (monitor text,severity integer,threshold integer, compare text,duration integer);"
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_create_agent_data)
                c.execute(sql_create_agent_events)
                c.execute(sql_create_agent_thresholds)
            con.commit()
            con.close()
        except: pass

    def delete_thresholds():
        try:
            sql_query = r"DELETE FROM AgentThresholds"
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
            con.commit()
            con.close()
        except: pass

    def insert_thresholds(monitor, severity, threshold, compare, duration):
        try:
            sql_query = r"INSERT INTO AgentThresholds(monitor, severity, threshold, compare, duration) VALUES('" + monitor + "'," + severity + "," + threshold + ",'" + compare +  "'," + duration + ")"
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
            con.commit()
            con.close()
        except: pass

    def select_thresholds():
        try:
            output = ''
            sql_query = r"SELECT monitor, severity, threshold, compare, duration FROM AgentThresholds"
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
                rows = c.fetchall()
            con.commit()
            con.close()
            return rows
        except: pass

    def insert_agentdata(monitor, value):
        try:
            sql_query = r"INSERT INTO AgentData(time, name, monitor, value, sent) VALUES(" + AgentSettings.agent_time + ",'" + AgentSettings.agent_name + "','" + monitor + "','" + value +  "',0)"
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
            con.commit()
            con.close()
        except: pass

    def select_agent_data():
        try:
            output = ""
            sql_query = r"SELECT time, name, monitor, value FROM AgentData WHERE sent=0 AND monitor NOT LIKE '%perf.service%'"
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
                rows = c.fetchall()
                for time, name, monitor, value in rows:
                    output = output + str(time) + ";" + name + ";" + monitor + ";" + str(value) + "\n"
            con.commit()
            con.close()
            return output
        except: pass
    
    def select_agent_data_events(time, monitor):
        try:
            sql_query = r"SELECT value FROM AgentData WHERE monitor='" + monitor + "' AND time > " + str(time) 
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
                rows = c.fetchall()
            con.commit()
            con.close()
            return rows
        except: pass

    def update_agent_data():
        try:
            sql_query = r"UPDATE AgentData SET sent=1 WHERE sent=0"
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
            con.commit()
            con.close()
        except: pass

    def delete_agent_data():
        try:
            agent_time = str(time.time()-604800).split('.')[0]
            sql_query = r"DELETE FROM AgentData WHERE time<" + agent_time
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
            con.commit()
            con.close()
        except: pass

    def insert_agent_event(monitor, message, severity):
        try:
            sql_query = r"""UPDATE AgentEvents SET time=""" + str(AgentSettings.agent_time) + """, message='""" + message + """', severity=""" + str(severity) + """, sent=0 WHERE monitor='""" + monitor + """' AND """ + str(severity) + """ > 
            (SELECT MAX(severity) FROM AgentEvents WHERE monitor='""" + monitor + """' AND status=1)"""
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
            con.commit()
            con.close()
            sql_query = r"""INSERT INTO AgentEvents(time, name, monitor, message, status, severity, sent) SELECT """ + str(AgentSettings.agent_time) + ",'" + AgentSettings.agent_name + "','" + monitor + "','" + message + "',1," + str(severity) + """,0
            WHERE NOT EXISTS(SELECT 1 FROM AgentEvents WHERE monitor='""" + monitor + """' AND status=1)"""
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
            con.commit()
            con.close()
        except: pass
    
    def select_agent_event(monitor):
        try:
            sql_query = r"SELECT monitor FROM AgentEvents WHERE monitor='" + monitor + "' AND status = 1" 
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
                monitor = c.fetchone()
            con.commit()
            con.close()
            return monitor
        except: pass

    def close_agent_event(monitor, severity):
        try:
            sql_query =  r"UPDATE AgentEvents SET status=0, sent=0 WHERE monitor='" + monitor + "' AND severity = " + severity 
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
            con.commit()
            con.close()
        except: pass

    def select_open_agent_events():
        try:
            output = None
            sql_query = r"SELECT time, name, monitor, message, status, severity FROM AgentEvents WHERE sent = 0" 
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
                rows = c.fetchall()
                for time, name, monitor, message, status, severity in rows:
                    output = output + str(time) + ";" + name + ";event;" + monitor + ";" + message + ";" + str(status) + ";" + str(severity) + "\n"
            con.commit()
            con.close()
            return output
        except: pass

    def update_agent_events():
        try:
            sql_query = r"UPDATE AgentEvents SET sent=1 WHERE sent=0"
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
            con.commit()
            con.close()
        except: pass

    def delete_agent_events():
        try:
            sql_query = r"DELETE FROM AgentEvents WHERE status=0 AND sent=1"
            con = AgentSQL.sql_con()
            if con is not None:
                c = con.cursor()
                c.execute(sql_query)
            con.commit()
            con.close()
        except: pass

class AgentWindows():
    def conf_memory_total():
        process = os.popen('wmic path Win32_ComputerSystem get TotalPhysicalMemory /value')
        result = process.read()
        process.close()
        result = result.replace('\n','').replace('TotalPhysicalMemory=','')
        result = round(int(result)  / 1024 / 1024, 0)
        AgentSQL.insert_agentdata('conf.memory.total', str(result))

    def perf_filesystem():
        process = os.popen('''wmic path Win32_PerfFormattedData_PerfDisk_LogicalDisk WHERE "Name LIKE '%:'" get Name,PercentFreeSpace,PercentIdleTime /format:csv''')
        result = process.read()
        process.close()
        result = result.replace('\n\n','\n')
        result_list = list(filter(None, result.split('\n')))
        for i in result_list:
            if not 'PercentFreeSpace' in i:
                ld_list = i.split(',')
                ld_name = ld_list[1].replace(':','').lower()
                ld_free = float(ld_list[2])
                ld_at = 100 - float(ld_list[3])
                AgentSQL.insert_agentdata('perf.filesystem.' + ld_name + '.percent.free', str(ld_free))
                AgentSQL.insert_agentdata('perf.filesystem.' + ld_name + '.percent.active', str(ld_at))

    def perf_memory():
        process = os.popen('wmic path Win32_OperatingSystem get FreePhysicalMemory,TotalVisibleMemorySize /value')
        result = process.read()
        process.close()
        result = result.replace('\n\n\n\n','').replace('\n\n',';')
        result_list = result.split(";")     
        FreeMem = int(result_list[0].replace('FreePhysicalMemory=',''))
        TotalMem = int(result_list[1].replace('TotalVisibleMemorySize=',''))
        PercentMem = ((TotalMem-FreeMem)/TotalMem)*100
        PercentMem = round(PercentMem,2)
        AgentSQL.insert_agentdata('perf.memory.percent.used', str(PercentMem))

    def perf_network():
        nw_br = 0
        nw_bs = 0
        process = os.popen('wmic path Win32_PerfFormattedData_Tcpip_NetworkInterface get BytesReceivedPersec,BytesSentPersec /format:csv')
        result = process.read()
        process.close()
        result = result.replace('\n\n','\n')
        result_list = list(filter(None, result.split('\n')))
        for i in result_list:
            if not 'BytesReceivedPersec' in i:
                nw_list = i.split(",")
                nw_br = nw_br + int(nw_list[1])
                nw_bs = nw_bs + int(nw_list[2])
        AgentSQL.insert_agentdata('perf.network.bytes.received', str(nw_br))
        AgentSQL.insert_agentdata('perf.network.bytes.sent', str(nw_bs))

    def perf_pagefile():
        process = os.popen('wmic path Win32_PerfFormattedData_PerfOS_PagingFile where name="_Total" get PercentUsage /value')
        result = process.read()
        process.close()
        result = result.replace('\n','').replace('PercentUsage=','')
        AgentSQL.insert_agentdata('perf.pagefile.percent.used', str(result))
    
    def perf_processor():
        process = os.popen('wmic path Win32_PerfFormattedData_PerfOS_Processor where name="_Total" get PercentProcessorTime /value')
        result = process.read()
        process.close()
        result = result.replace('\n','').replace('PercentProcessorTime=','')
        AgentSQL.insert_agentdata('perf.processor.percent.used', str(result))
    
    def perf_uptime():
        process = os.popen('wmic path Win32_PerfFormattedData_PerfOS_System get SystemUptime /value')
        result = process.read()
        process.close()
        result = result.replace('\n','').replace('SystemUpTime=','')
        AgentSQL.insert_agentdata('perf.system.uptime.seconds', str(result))
    
    def perf_services():
        if AgentSettings.services:
            for service in AgentSettings.services:
                process = os.popen('wmic path Win32_Service where name="' + service + '" get State /value')
                result = process.read()
                process.close()
                result = result.replace('\n','').replace('State=','')
                sname = 'perf.service.' + service.replace(' ','').lower() + '.state'
                if result == 'Running':
                    result = 1
                else:
                    result = 0
                AgentSQL.insert_agentdata(sname, str(result))

class AgentProcess():
    def load_config():
        #Set name and create SQL database
        try:
            AgentSettings.agent_name = socket.gethostname().lower()
            AgentSQL.create_tables()
            AgentSQL.delete_thresholds()
        except: pass
        # Load configuration
        try:
            f = open(AgentSettings.agent_path + 'settings.cfg', 'r')
            fl = f.read().split('\n')
            for i in fl:
                if i.startswith('server:'): AgentSettings.server = i[7:].replace(' ','')
                if i.startswith('port:'): AgentSettings.port = int(i[5:].replace(' ',''))
                if i.startswith('secure:'): AgentSettings.secure = int(i[7:].replace(' ',''))
                if i.startswith('log:'): AgentSettings.log = i[4:].replace(' ','')
                if i.startswith('services:'): AgentSettings.services = i[9:].replace(' ','').split(',')
                if i.startswith('thresh:'):
                    thresh = i[7:].replace(' ','').split(',')
                    AgentSQL.insert_thresholds(thresh[0], thresh[1], thresh[2], thresh[3], thresh[4])
        except: pass

    def data_process():
        try:
            osplatform = platform.system()
            osarchitecture = platform.architecture()[0]
            osbuild = platform.win32_ver()[1]
            ipaddress = socket.gethostbyname(socket.gethostname())
            domain = socket.getfqdn().split('.', 1)[1]
            processors = str(os.cpu_count())
            AgentSQL.insert_agentdata('conf.os.name', osplatform)
            AgentSQL.insert_agentdata('conf.os.architecture', osarchitecture)
            AgentSQL.insert_agentdata('conf.os.build', osbuild)
            AgentSQL.insert_agentdata('conf.ipaddress', ipaddress)
            AgentSQL.insert_agentdata('conf.domain', domain)
            AgentSQL.insert_agentdata('conf.processors', processors)
            AgentWindows.conf_memory_total()
            AgentWindows.perf_filesystem()
            AgentWindows.perf_memory()
            AgentWindows.perf_network()
            AgentWindows.perf_pagefile()
            AgentWindows.perf_processor()
            AgentWindows.perf_uptime()
            AgentWindows.perf_services()
        except: pass
        output = AgentSQL.select_agent_data()
        return output

    def event_create(monitor, severity, threshold, compare, duration, status):
        print('event create')
        try:
            message = monitor.replace('perf.', '').replace('.', ' ').capitalize()
            message = message + ' ' + compare + ' ' + str(threshold) + ' for ' + str(round(duration/60)) + ' minutes'
            # Check open messages
            check_monitor = AgentSQL.select_agent_event(monitor)
            if not check_monitor is None: check_monitor=check_monitor[0]
            # Create, update, and queue events for dispatch
            if check_monitor is None and status == 1:
                AgentSQL.insert_agent_event(monitor, message, severity)
            elif check_monitor == monitor and status == 0:
                AgentSQL.close_agent_event(monitor, severity)
            else: pass
        except: pass
        
    def event_process():
        try:
            agent_time_int = int(AgentSettings.agent_time)
            agent_thresholds = AgentSQL.select_thresholds()
            a_val = 0
            b_val = 0
            for i in agent_thresholds:
                monitor = i[0]
                severity = i[1]
                threshold = int(i[2])
                compare = i[3]
                duration = i[4]
                time_window = agent_time_int - duration
                agent_data = AgentSQL.select_agent_data_events(time_window, monitor)
                a_val = 0
                b_val = 0
                for i in agent_data:
                    value = i[0]
                    if compare == '>':
                        if value > threshold:
                            a_val += 1
                            b_val += 1
                        else: b_val += 1
                    elif compare == '<':
                        if value < threshold:
                            a_val += 1
                            b_val += 1
                        else: b_val += 1
                    elif compare == '=':
                        if value == 0 and threshold == 0:
                            a_val += 1
                            b_val += 1
                        else: b_val += 1
                if a_val == b_val and b_val != 0 :
                    AgentProcess.event_create(monitor, severity, threshold, compare, duration, 1)
                else:
                    AgentProcess.event_create(monitor, severity, threshold, compare, duration, 0)
            output = AgentSQL.select_open_agent_events()
            if output is None: output = ''
            return output
        except: pass

    def send_data(message):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            if AgentSettings.secure == 1:
                context = ssl.create_default_context()
                context.options |= ssl.PROTOCOL_TLSv1_2
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                conn = context.wrap_socket(sock, server_hostname = AgentSettings.server)
                conn.connect((AgentSettings.server, AgentSettings.port))
                byte=str(message).encode()
                conn.send(byte)
                data = conn.recv(1024).decode()
                if data == 'Received':
                    AgentSQL.update_agent_data()
                    AgentSQL.update_agent_events()
                conn.close()
            else:
                sock.connect((AgentSettings.server, AgentSettings.port))
                byte = str(message).encode()
                sock.send(byte)
                data = sock.recv(1024)
                if data == 'Received':
                    AgentSQL.update_agent_data() 
                    AgentSQL.update_agent_events()
                sock.close()
        except: pass

    def run_process():
        AgentSettings.agent_time = str(time.time()).split('.')[0]
        send_message = AgentProcess.data_process()
        event_message = AgentProcess.event_process()
        #print(send_message, event_message)
        message = send_message + event_message
        AgentProcess.send_data(message)
        AgentSQL.delete_agent_data()
        AgentSQL.delete_agent_events()

#AgentProcess.load_config()
#AgentProcess.run_process()