#!/usr/bin/python3
# Mike Gould
# This is expected to take an exported text CSS config and convert the content into virtual servers.
# This version will only provide groupings, future versions may incorporate tmsh commands.
from enum import unique

# This version removes duplicate nodes and replace all instances of the duplicate node name with a single unique node name.
#   This was done to remove the duplicate node errors that caused a loss of work time at last deployment


# Copyright 2015 Me

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
    
    def updateMonPort(self, value):
        self._Type = value
                
    def tmshAddMonitor(self):
        if self._Type == 'tcp':
            print('create monitor tcp-half-open {} destination *:{}'.format(self._Name, self._Port))
        elif self._Type == 'http':
            if self._Port == 'any':
                print('create monitor http {} destination *.80'.format(self._Name))
            else:
                print('create monitor http {} destination *.{}'.format(self._Name, self._Port))
        elif self._Type == 'ssl':
            if self._Port == 'any':
                print('create monitor https {} destination *.443'.format(self._Name))
            else:
                print('create monitor https {} destination *.{}'.format(self._Name, self._Port))
   
        
        
    def printHealthCheck(self):
        print('Health Monitor Name:\t\t\t\t\t{}'.format(self._Name))
        print('Generic monitor base:\t\t\t\t\t{}'.format(self._Type))
        print('Port to monitor:\t\t\t\t\t{}'.format(self._Port))
        print('Retry Period:\t\t\t\t\t\t{}'.format(self._RetryPeriod))
        print('Max retry count:\t\t\t\t\t{}'.format(self._MaximumFailureCount))
        print('Max frequency:\t\t\t\t\t\t{}'.format(self._Frequency))
        print('Target server:\t\t\t\t\t\t{}'.format(self._Server))

class trafficprofile():
    def __init__(self, ProfileName, ProfileParent, IdleTimeOut = 'Default', FallBackServer = 'none'):
        self._Name = ProfileName
        self._Type = ProfileParent
        self._FallBackServer = FallBackServer
        self._IdleTimeOut = IdleTimeOut
        
    def tmshAddProfile(self):
        print('create profile {} {} '.format(self._Type, self._Name), end = '')
        if str(self._IdleTimeOut) != 'Default':
             print('idle-timeout {}'.format(self._IdleTimeOut))
        if self._FallBackServer != 'none':
            print('fallback-server {}'.format(self._FallBackServer))
        
class server():
    def __init__(self, poolMemberName, nodeIP, poolMemberPort = 'any', poolMemberStatus = 'disabled', aliases = []):
        self._Name = poolMemberName
        self._IP = nodeIP
        self._Port = poolMemberPort
        self._Status = poolMemberStatus
        self._Aliases = aliases
        
    def addAlias(self, aliases):
        self._Aliases.append(aliases)
            
    def tmshAddNode(self, routeDomain):
        print('create node {} address {}{}'.format(self._Name, self._IP, routeDomain))
        if len(self._Aliases) > 0:
            for  each in self._Aliases:
                print('\t\t\t\t\t Alias: {}'.format(each)) 

        
class pool():
    def __init__(self, poolname, virtualPort, loadbalancingMethod = 'round-robin', memberList = [], poolmon = 'none', primarySorryServer = 'none'):
        self._Name = poolname
        self._Monitor = poolmon # reference to healthcheck._Name
        self._Members = memberList # List of servers in Virtual server cluster
        self._LoadBalancing_method = loadbalancingMethod
        self._SorryServer = primarySorryServer
        self._Poolport = virtualPort
        
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
        print('create pool {} load-balancing-mode {} members add {{ '.format(self._Name, self._LoadBalancing_method), end ='')
        for member in self._Members:
            # First check to see if the pool members name is listed as an alias for another node
            for singleNode in nodes:
                for nickname in singleNode._Aliases:
                    if member == nickname:
                        print(' {}:{} '.format(singleNode._Name, self._Poolport), end = '')
                        break
            for host in nodes:
                if member == host._Name:
                    print(' {}:{} '.format(member, self._Poolport), end = '')
        print(' }} monitor {}'.format(self._Monitor))
    
    def updatePool(self, prop, value):
        #  Not sure this will work.  Not sure how to pass the name of the property that needs to change.
        self._[prop] = value
        # print('{} was just updated'.format(self._[prop]))
        
class virtualServer():
    def __init__(self,virtualServer, virtualIPAddress, poolMembers, profiles, virtualPort = 'any', virtualProtocol = 'tcp', 
                 virtualStatus = 'disabled', idleTimeOut = 'Default', persistence_profile = 'none', 
                 persistence_timeout = 0, primarySorryServer = 'none'):
        self._VirtualName = virtualServer
        self._VirtualIPAddress = virtualIPAddress
        self._PoolMembers = poolMembers #list of members
        self._VirtualPort = virtualPort # Port the Virtual server will listen on.  Some may be any.
        self._VirtualProtocol = virtualProtocol
        self._VirtualStatus = virtualStatus
        self._Flow_timeout_multiplier = idleTimeOut # roughly maps the CSS session timeout to the idle timeout value for tcp profile.
        #                                             CSS values is in multiples of 16 seconds.
        self._Persistence_profile = persistence_profile
        self._Profiles = profiles
        self._PoolName = (self._VirtualName + '_pool')
        self._Persistence_timeout = persistence_timeout
        
    def printVirtualServer(self, poolMembers, pools, healthmonitors, routeDomain):
        print('New Virtual server named:  \t\t\t\t{}\n\tServing the IP address:  \t\t\t{}{}:{}({})'
          .format(self._VirtualName, self._VirtualIPAddress, routeDomain, self._VirtualProtocol, self._VirtualPort))
        print('New Pool named:\t\t\t\t\t\t{}'.format(self._PoolName))
        print('\tWhich includes server(s):')
        for server in self._PoolMembers:
            for x in poolMembers:
                if x._Name == server:
                    if len(server) < 8:
                        print('{} with the IP of:\t\t\t\t\t{}{}:{}'.format(server, x._IP, routeDomain, self._VirtualPort))
                    elif len(server) < 16:
                        print('{} with the IP of:\t\t\t\t{}{}:{}'.format(server, x._IP, routeDomain, self._VirtualPort))
                    elif len(server) < 24:
                        print('{} with the IP of:\t\t\t{}{}:{}'.format
                              (server, x._IP, routeDomain, self._VirtualPort))
                    elif len(server) < 32:
                        print('{} with the IP of:\t\t{}{}:{}'.format(server, x._IP, routeDomain, self._VirtualPort))    
                    else:
                        print('{} with the IP of:\t\t{}{}:{}'.format(server, x._IP, routeDomain, self._VirtualPort))
                for aka in x._Aliases:
                    if server == aka:
                        if len(server) < 8:
                            print('{} with the IP of:\t\t\t\t\t{}{}:{}'.format(x._Name, x._IP, routeDomain, self._VirtualPort))
                        elif len(server) < 16:
                            print('{} with the IP of:\t\t\t\t{}{}:{}'.format(x._Name, x._IP, routeDomain, self._VirtualPort))
                        elif len(server) < 24:
                            print('{} with the IP of:\t\t\t{}{}:{}'.format
                                  (x._Name, x._IP, routeDomain, self._VirtualPort))
                        elif len(server) < 32:
                            print('{} with the IP of:\t\t{}{}:{}'.format(x._Name, x._IP, routeDomain, self._VirtualPort))    
                        else:
                            print('{} with the IP of:\t\t{}{}:{}'.format(x._Name, x._IP, routeDomain, self._VirtualPort))

        if self._Flow_timeout_multiplier != 'Default':
            timeout = int(self._Flow_timeout_multiplier) * 16
            print('and a idle timeout value of: \t\t\t\t{} seconds\n'.format(timeout))
        for check in healthmonitors:
            if check._Server == server:
                healthcheck.printHealthCheck(check)


    def tmshVirtualServer(self, routeDomain):
        #  First create a virtual address and disable ARP so there are no conflicts.
        #  Then create the virtual server and assign a pool
        print('create virtual {} {{ destination {}{}:{} profiles add {{ '.format(self._VirtualName, self._VirtualIPAddress, routeDomain, self._VirtualPort), end='')
        #
        # Check to see if there are any specific profiles to assign to virtual server
        #
        if len(self._Profiles) <= 1:
            print('tcp }', end='')
        else:
            for each in self._Profiles:
                print('{} '.format(each), end='')
            print('}', end='')
        #
        # Add the pool to the end of the virtual server  creation
        #
        if self._Persistence_profile != 'none':
            print(' persist replace-all-with { source_addr } ', end = '')
        print(' source-address-translation { type automap } ', end = '')
        print(' pool {} }}'.format(self._PoolName))


        
def getService(cssConfig, words):
    nodes = [] # List of Real server
    healthmonitor = []
    aliases = []  # list of other servernames the node is listed as
    nodeName = words[1]
    poolMonitorName = nodeName + '_mon'    
    nodeCount = 0
    keepaliveRetryPeriod = '30'
    poolKeepaliveType = 'tcp'
    maxfailure = '2'
    keepaliveFrequency = '30'
    poolMemberPort = 'any'
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
                # Add new server to server list if it is unique otherwise add name to aliases list!!
                #
                uniqueServer = 'yes'
                for host in nodes:
                    if host._IP == nodeIP:
                        uniqueServer = 'no'
                        host.addAlias(nodeName)
                        break
                if uniqueServer == 'yes':
                    nodes.append(server(nodeName, nodeIP, poolMemberPort, poolMemberStatus, aliases))
                
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
                keepaliveFrequency = 'Default'
                poolMonitorName = 'tcp'
                aliases = []
            elif words2[0] == 'content':
                nodes.append(server(nodeName, nodeIP, poolMemberPort, poolMemberStatus, aliases))
                break
 
    return healthmonitor, nodes, nodeCount+1, words2

def getContent(cssConfig, words, healthmonitors, routeDomain):
    virtualServerObject = []
    poolObjects = []
    virtualServerName = words[1] # Needs to be here to make sure the name is captured from words
    virtualServerCount = 0
    profiles = ['tcp',]
    profileName = ''
    CustomProfiles = []             # list of all the custom profiles found.  TCP is default
    virtualProtocol = 'tcp'
    virtualPort = 'any'
    idleTimeOut = 'Default'
    persistence_profile = 'none'
    persistence_timeout = 0
    loadbalancingMethod = 'round-robin'
    primarySorryServer = 'none'
    virtualStatus = 'disabled'
    poolmon = 'none'
    poolMembers = []
    for vsline in cssConfig:
        words = vsline.split()
        if words:
            if words[0] == 'flow-timeout-multiplier':
                idleTimeOut = words[1]
                profileName = virtualServerName + '-tcp-profile'
                profiles.append(profileName)
                CustomProfiles.append(trafficprofile(profileName, virtualProtocol, idleTimeOut, primarySorryServer))
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
                profileName = virtualServerName + '-http-profile'
                virtualProtocol = 'http'
                profiles.append(profileName)
                primarySorryServer = words[1]
                CustomProfiles.append(trafficprofile(profileName, virtualProtocol, idleTimeOut, primarySorryServer))
            elif words[0] == 'active':
                virtualStatus = 'active'
            elif words[0] == 'advanced-balance' and words[1] == 'sticky-srcip':
                persistence_profile = 'SourceIP'
            elif words[0] == 'sticky-inact-timeout':
                persistence_timeout = words[1]          
            elif words[0] == 'content':
                #  Create a Virtual Server Object and add it to the virtualServerObject list
                virtualServerObject.append(virtualServer(virtualServerName, virtualIPAddress, poolMembers, profiles,
                                                          virtualPort, virtualProtocol, virtualStatus, 
                                                          idleTimeOut, persistence_profile, 
                                                          persistence_timeout))
                #  Create a new pool for each virtual server
                
                for node in poolMembers:
                    for node2 in healthmonitors:     
                        if node == node2._Server:
                            if virtualPort == 'any' and node2._Port == 'any':
                                poolmon = 'gateway-icmp'
                            else:
                                poolmon = virtualServerName + '_mon'
                            node2.updateName(poolmon)
                            break    
                        
                        
                poolObjects.append(pool(virtualServerName + '_pool', virtualPort, loadbalancingMethod, poolMembers, poolmon, primarySorryServer ))
                CustomProfiles.append(trafficprofile(profileName, virtualProtocol, idleTimeOut, primarySorryServer))
                
                            
                #  Reset variables
                poolMembers = []
                virtualServerCount = virtualServerCount + 1
                virtualServerName = words[1]
                virtualProtocol = 'tcp'
                virtualPort = 'any'
                idleTimeOut = 'Default'
                primarySorryServer = 'none'
                profiles = ['tcp',]
                persistence_profile = 'none'
            elif words[0] == '!***************************':
                virtualServerObject.append(virtualServer(virtualServerName, virtualIPAddress, poolMembers, profiles,
                                                         virtualPort, virtualProtocol, virtualStatus, 
                                                         idleTimeOut, persistence_profile, 
                                                         persistence_timeout))
                poolObjects.append(pool(virtualServerName + '_pool', virtualPort, loadbalancingMethod, poolMembers, poolmon, primarySorryServer))
                break
    return virtualServerObject, poolObjects, healthmonitors, virtualServerCount+1, CustomProfiles


def main():

    import sys
    configFile = str(sys.argv[1])
    cssConfig = open(configFile)
    virtualServerObject = []
    healthmonitors = []
    customProfiles = []
    report = 0
    code = 0
    routeDomain = '%' + str(sys.argv[2])
    for line in cssConfig:
        words = line.split()
        if words:
                        
            if words[0] == 'content':
                virtualServerObject, pools, healthmonitors, vsCount, customProfiles = getContent(cssConfig, words, healthmonitors, routeDomain)               
                
            elif words[0] == 'service':
                healthmonitors, nodes, hostCount, words = getService(cssConfig, words)
                if words[0] == 'content':
                    virtualServerObject, pools, healthmonitors, vsCount, customProfiles = getContent(cssConfig, words, healthmonitors, routeDomain)



#
#                    TMSH Command Generator templates Below
#     print('\t\tHere is a listing of all the commands needed to add the real servers with their port to the F5:\n')
#     print('tmsh')
#     print('ltm')
#     for z in pools:
#         z.tmshAddNode(routeDomain)
#     print('quit\n')
#     print()
#   This will create a report of each virtual server as well as print the commands to create the pool...  More to follow
#     print()

#     This is used to print each pool entry
#     for x in pools:
#         pool.printPool(x)
        
#    This will print out a listing for the health checks obtained from the pool and member function
#    for z in healthmonitors:
#        healthcheck.printHealthCheck(z)
#        print()


    print('\t\t\t----------  Virtual Server Configs begin here  ----------')
    
    print('\t\tNodes listing\n')    
    for n in nodes:
        n.tmshAddNode(routeDomain)
    print()
    
    print('\t\tExisting Health Monitors\n')
    
    seen = []
    found = []
    for h in healthmonitors:
        if h._Name not in seen:
            seen.append(h._Name)
            found.append(h._Name)
            h.tmshAddMonitor()
    print()
    
    print('\t\tCustom traffic profiles\n')
    
    seen = []
    found = []
    for tp in customProfiles:
        if tp._Name not in seen:
            seen.append(tp._Name)
            found.append(tp._Name)
            tp.tmshAddProfile()
    print()
    

    print('\t\tExisting Pools\n')
    for p in pools:
        p.tmshAddPool(nodes)
    print()
    
 
    print('\t\tExisting Site Summary:\n')
    for y in virtualServerObject:
#        y.printVirtualServer(nodes, pools, healthmonitors, routeDomain)
        y.tmshVirtualServer(routeDomain)
        print()


# Summary of number of hosts and Virtual servers 
    print('There are {} real servers defined'.format(hostCount))
    print('There are {} Virtual Servers defined'.format(vsCount))

    cssConfig.close()
    
if __name__ == "__main__": main()
