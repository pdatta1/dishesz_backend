

from django.utils.translation import gettext_lazy as _

class AllowedHosts(object): 
    """
        Allowed Hosts handle the memory storage of all
        allowed hosts for django traffic
    """
    def __init__(self): 

        # hosts list 
        self.hosts = list() 

    
    def add_host(self, host_name): 
        """
            add_host adds a string host_name to the hosts list 
            if not exists 
            :param host_name: host_name to be added
        """

        if host_name in self.hosts: 
            raise ValueError(_('Host Name is already in list'))

        self.hosts.append(host_name)


    def remove_host(self, host_name): 
        """
            remove_host removes the string host_name from the hosts list
            if host_length is 0 or host_name is in hosts raise value
        """
        host_length = len(self.hosts)
        
        if host_length == 0: 
            raise ValueError(_('Host is empty, nothing to remove'))

        if not host_name in self.hosts:
            raise ValueError(_('Host Name is not in hosts'))

        self.hosts.remove(host_name)

    
    def get_allowed_hosts(self): 
        return self.hosts