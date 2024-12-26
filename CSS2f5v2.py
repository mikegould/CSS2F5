#!/usr/bin/python3
# Mike Gould
# This is expected to take an exported text CSS config and convert the content into virtual servers.
# This version will only provide groupings, future versions may incorporate tmsh commands.
# Copyright 2014 Me

class healthcheck():
    def __init__(self, poolMonitorName, healthcheckType, healthcheckPort, keepaliveRetryPeriod, maxfailure, keepaliveFrequency, server):
        self._Name = poolMonitorName
        self._Type = healthcheckType
        self._Port = healthcheckPort
        self._RetryPeriod = keepaliveRetryPeriod
        self._MaximumFailureCount = maxfailure
        self._Frequency = keepaliveFrequency
        self._Server = server # Reference to server._Name 
        
    def updateName(self, value):
        self._Name = value
        print(self._Name)
                
    def tmshAddMonitor(self):
        print('create ')
        
    def printHealthCheck(self):
        print('Health Monitor Name:\t\t\t\t\t{}'.format(self._Name))
        print('Generic monitor base:\t\t\t\t\t{}'.format(self._Type))
        print('Port to monitor:\t\t\t\t\t{}'.format(self._Port))
        print('Retry Period:\t\t\t\t\t\t{}'.format(self._RetryPeriod))
        print('Max retry count:\t\t\t\t\t{}'.format(self._MaximumFailureCount))
        print('Max frequency:\t\t\t\t\t\t{}'.format(self._Frequency))
        print('Target server:\t\t\t\t\t\t{}'.format(self._Server))


class server():
    def __init__(self, poolMemberName, nodeIP, poolMemberPort = 'any', poolMemberStatus = 'disabled'):
        self._Name = poolMemberName
        self._IP = nodeIP
        self._Port = poolMemberPort
        self._Status = poolMemberStatus
            
    def tmshAddNode(self):
        print('create node {} address {}'.format(self._Name, self._IP))

        
class pool():
    def __init__(self, poolname, loadbalancingMethod = 'leastconn', memberList = [], poolmon = 'none', primarySorryServer = 'none'):
        self._Name = poolname
        self._Monitor = poolmon # reference to healthcheck._Name
        self._Members = memberList # List of servers in Virtual server cluster
        self._LoadBalancing_method = loadbalancingMethod
        self._SorryServer = primarySorryServer
        
    def printPool(self):
        print('Pool named:\t\t{}'.format(self._Name))
        print('Monitored by: \t{}'.format(self._Monitor))
        print('uses LB method:\t{}'.format(self._LoadBalancing_method))
        print('The Primary sorry server is: {}'.format(self._SorryServer))
        print('Splits the load amongst:')
        for s in self._Members:
            print('server:\t{}'.format(s))
        print()
        
    def tmshAddPool(self, nodes):
        print('tmsh')
        print('ltm')
        print('create pool {} load-balancing-mode {} members add {{'.format(self._PoolName, self._LoadBalancing_method), end ='')
        for member in self._PoolMembers:
            for x in nodes:
                if x._Name == member:
                    print('{}:{} '.format(x._Name, x._Port), end = '')
        print(' }')
        print('quit\n')
    
    def updatePool(self, prop, value):
        #  Not sure this will work.  Not sure how to pass the name of the property that needs to change.
        self._[prop] = value
        print('{} was just updated'.format(self._[prop]))
        
class virtualServer():
    def __init__(self,virtualServer, virtualIPAddress, poolMembers, virtualPort = 'any', virtualProtocol = 'tcp', 
                 virtualStatus = 'disabled', idleTimeOut = 'None', persistence_profile = 'none', 
                 persistence_timeout = 0, primarySorryServer = 'none'):
        self._VirtualName = virtualServer
        self._VirtualIPAddress = virtualIPAddress
        self._PoolMembers = poolMembers #list of members
        self._VirtualPort = virtualPort # Port the Virtual server will listen on.  Some may be any.
        self._VirtualProtocol = virtualProtocol
        self._VirtualStatus = virtualStatus
        self._Flow_timeout_multiplier = idleTimeOut
        self._Persistence_profile = persistence_profile
        self._PoolName = (self._VirtualName + '_pool')
        self._Persistence_timeout = persistence_timeout
        
    def printVirtualServer(self, poolMembers, pools, healthmonitors):
        print('New Virtual server named:  \t\t\t\t{}\n\tServing the IP address:  \t\t\t{}:{}({})'
          .format(self._VirtualName, self._VirtualIPAddress, self._VirtualProtocol, self._VirtualPort))
        print('New Pool named:\t\t\t\t\t\t{}'.format(self._PoolName))
        print('\tWhich includes server(s):')
        for server in self._PoolMembers:
            for x in poolMembers:
                if x._Name == server:
                    if len(server) < 8:
                        print('{} with the IP of:\t\t\t\t\t{}:{}'.format(server, x._IP, self._VirtualPort))
                    elif len(server) < 16:
                        print('{} with the IP of:\t\t\t\t{}:{}'.format(server, x._IP, self._VirtualPort))
                    elif len(server) < 24:
                        print('{} with the IP of:\t\t\t{}:{}'.format
                              (server, x._IP, self._VirtualPort))
                    elif len(server) < 32:
                        print('{} with the IP of:\t\t{}:{}'.format(server, x._IP, self._VirtualPort))    
                    else:
                        print('{} with the IP of:\t\t{}:{}'.format(server, x._IP, self._VirtualPort))
        for check in healthmonitors:
            if check._Server == server:
                healthcheck.printHealthCheck(check)

        
def getService(cssConfig, words):
    nodes = [] # List of Real server objects.healthmonitor
    healthmonitor = []
    nodeName = words[1]
    poolMonitorName = nodeName + '_mon'    
    nodeCount = 0
    keepaliveRetryPeriod = '30'
    poolKeepaliveType = 'tcp'
    maxfailure = '2'
    keepaliveFrequency = '30'
    for nextline in cssConfig:
        words2 = nextline.split()
        if words2:
            if words2[0] == 'ip':
                nodeIP = words2[2]
            elif words2[0] == 'keepalive':
                poolMonitorName = nodeName + '_mon'
                if words2[1] == 'port':
                    poolMemberPort = words2[2]
                elif words2[1] == 'type':
                    if words2[2] == 'script':
                        #  There are multiple 'scripted' health monitors in CSS.  They should map to generic LTM health monitors
                        if words2[3] == 'ap-kal-smtp':
                            poolKeepaliveType = 'smtp'
                        elif words2[3] == 'ap-kal-ldap':
                            poolKeepaliveType = 'ldap'
                        elif words2[3] == 'ap-kal-pinglist':
                            poolKeepaliveType = 'icmp'                       
                    elif words2[2] == 'tcp':
                        poolKeepaliveType = words2[2]
                    elif words2[2] == 'http':
                        poolKeepaliveType = words2[2]
                    elif words2[2] == 'ssl':
                        poolKeepaliveType = words2[2]
                elif words2[1] == 'retryperiod':
                    keepaliveRetryPeriod = words2[2]
                elif words2[1] == 'maxfailure':
                    maxfailure = words2[2]
                elif words2[1] == 'frequency':
                    keepaliveFrequency = words2[2]
                elif words2[1] == 'tcp-close':
                    poolKeepaliveType = 'tcp-half-open'
                                                
            elif words2[0] == 'active':
                poolMemberStatus = 'active'
            elif words2[0] == 'service':
                # Add new server to server list
                nodes.append(server(nodeName, nodeIP, poolMemberPort, poolMemberStatus))
                
                # Add new health monitor named after the pool unless it is a generic monitor                
                healthmonitor.append(healthcheck(poolMonitorName, poolKeepaliveType, poolMemberPort, keepaliveRetryPeriod, maxfailure, keepaliveFrequency, nodeName))
                nodeCount = nodeCount + 1

  
                #  Reset variables to defaults for next line of code
                nodeName = words2[1]
                poolKeepaliveType = 'tcp'
                nodeIP = ''
                poolMemberPort = 'any'
                poolMemberStatus = 'disabled'
                keepaliveRetryPeriod = '30'
                maxfailure = '2'
                keepaliveFrequency = '30'
                poolMonitorName = 'tcp'
            elif words2[0] == 'content':
                nodes.append(server(nodeName, nodeIP, poolMemberPort, poolMemberStatus))
                break
 
    return healthmonitor, nodes, nodeCount+1, words2

def getContent(cssConfig, words, healthmonitors):
    virtualServerObject = []
    poolObjects = []
    virtualServerName = words[1] # Needs to be here to make sure the name is captured from words
    virtualServerCount = 0
    virtualProtocol = 'tcp'
    virtualPort = 'any'
    idleTimeOut = 'none'
    persistence_profile = 'none'
    persistence_timeout = 0
    loadbalancingMethod = 'leastconn'
    primarySorryServer = 'none'
    virtualStatus = 'disabled'
    poolMembers = []
    for vsline in cssConfig:
        words = vsline.split()
        if words:
            if words[0] == 'flow-timeout-multiplier':
                idleTimeOut = words[1]
            elif words[0] == 'vip':
                virtualIPAddress = words[2]
            elif words[0] == 'port':
                virtualPort = words[1]
            elif words[0] == 'protocol':
                virtualProtocol = words[1]
            elif words[0] == 'add':
                poolMembers.append(words[2])
            elif words[0] == 'primarySorryServer':
                poolMembers.append(words[1])
                loadbalancingMethod = "SorryServer"
                primarySorryServer = words[1]
            elif words[0] == 'active':
                virtualStatus = 'active'
            elif words[0] == 'advanced-balance' and words[1] == 'sticky-srcip':
                persistence_profile = 'SourceIP'
            elif words[0] == 'sticky-inact-timeout':
                persistence_timeout = words[1]          
            elif words[0] == 'content':
                #  Create a Virtual Server Object and add it to the virtualServerObject list
                virtualServerObject.append(virtualServer(virtualServerName, virtualIPAddress, poolMembers,
                                                          virtualPort, virtualProtocol, virtualStatus, 
                                                          idleTimeOut, persistence_profile, 
                                                          persistence_timeout))
                #  Create a new pool for each virtual server
                
                poolObjects.append(pool(virtualServerName + '_pool', loadbalancingMethod, poolMembers, primarySorryServer ))
                for node in poolMembers:
                    for node2 in healthmonitors:     
                        if node == node2._Server:
                            node2.updateName(virtualServerName + '_mon')
                            break                    
                            
                #  Reset variables
                poolMembers = []
                virtualServerCount = virtualServerCount + 1
                virtualServerName = words[1]
                virtualProtocol = 'tcp'
                virtualPort = 'any'
                idleTimeOut = 'none'
            elif words[0] == '!***************************':
                virtualServerObject.append(virtualServer(virtualServerName, virtualIPAddress, poolMembers, 
                                                         virtualPort, virtualProtocol, virtualStatus, 
                                                         idleTimeOut, persistence_profile, 
                                                         persistence_timeout))
                poolObjects.append(pool(virtualServerName + '_pool', loadbalancingMethod, poolMembers, primarySorryServer ))
                break
    return virtualServerObject, poolObjects, healthmonitors, virtualServerCount+1


def main():

    import sys
    configFile = str(sys.argv[1])
    cssConfig = open(configFile)
    virtualServerObject = []
    healthmonitors = []
    report = 0
    code = 0
    for line in cssConfig:
        words = line.split()
        if words:
                        
            if words[0] == 'content':
                virtualServerObject, pools, healthmonitors, vsCount = getContent(cssConfig, words, healthmonitors)               
                
            elif words[0] == 'service':
                healthmonitors, nodes, hostCount, words = getService(cssConfig, words)
                if words[0] == 'content':
                    virtualServerObject, pools, healthmonitors, vsCount = getContent(cssConfig, words, healthmonitors)



#
#                    TMSH Command Generator templates Below
#     print('\t\tHere is a listing of all the commands needed to add the real servers with their port to the F5:\n')
#     print('tmsh')
#     print('ltm')
#     for z in pools:
#         z.tmshAddNode()
#     print('quit\n')
#     print()
#   This will create a report of each virtual server as well as print the commands to create the pool...  More to follow
#     print()

#     This is used to print each pool entry
#     for x in pools:
#         pool.printPool(x)
        
#    This will print out a listing for the health checks obtained from the pool and member function
    for z in healthmonitors:
        healthcheck.printHealthCheck(z)
        print()


#     print('\t\t\t----------  Virtual Server Configs begin here  ----------')
#     for y in virtualServerObject:
#         print('\t\tExisting Site Summary:\n')
#         y.printVirtualServer(nodes, pools, healthmonitors)
#         print()

#         print(' Here are the TMSH commands to run to recreate the existing site on an F5\n')
#         y.tmshAddPool(nodes)
 
    print('There are {} real servers defined'.format(hostCount))
    print('There are {} Virtual Servers defined'.format(vsCount))

    cssConfig.close()
    
if __name__ == "__main__": main()
