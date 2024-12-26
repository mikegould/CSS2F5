ltm node /PP-USR-WEB/PP-USR-WEB-01 {
    address 10.1.17.81
}
ltm node /PP-USR-WEB/PP-USR-WEB-02 {
    address 10.1.17.82
}
ltm node /PP-USR-WEB/PP-USR-WEB-03 {
    address 10.1.17.83
}
ltm node /PP-USR-WEB/PP-USR-WEB-04 {
    address 10.1.17.84
}
ltm node /PP-USR-WEB/PP-USR-WEB-05 {
    address 10.1.17.85
}
ltm node /PP-USR-WEB/PP-USR-WEB-06 {
    address 10.1.17.86
}


ltm pool /PP-USR-WEB/pl-PP-USR-WEB-443 {
   load-balancing-mode least-connections-member
   monitor /Common/tcp_half_open
   members {
	/PP-USR-WEB/PP-USR-WEB-01:https {
        address 10.1.17.81
	}
    /PP-USR-WEB/PP-USR-WEB-02:https {
		address 10.1.17.82
	}
    /PP-USR-WEB/PP-USR-WEB-03:https {
		address 10.1.17.83
	}
    /PP-USR-WEB/PP-USR-WEB-04:https {
		address 10.1.17.84
	}
    /PP-USR-WEB/PP-USR-WEB-05:https {
		address 10.1.17.85
	}
    /PP-USR-WEB/PP-USR-WEB-06:https {
		address 10.1.17.86
	}
   }
}
ltm pool /PP-USR-WEB/pl-PP-USR-WEB-80 {
   load-balancing-mode predictive-member
   monitor /Common/http
   members {
	/PP-USR-WEB/PP-USR-WEB-01:https {
        address 10.1.17.81
	}
    /PP-USR-WEB/PP-USR-WEB-02:https {
		address 10.1.17.82
	}
    /PP-USR-WEB/PP-USR-WEB-03:https {
		address 10.1.17.83
	}
    /PP-USR-WEB/PP-USR-WEB-04:https {
		address 10.1.17.84
	}
    /PP-USR-WEB/PP-USR-WEB-05:https {
		address 10.1.17.85
	}
    /PP-USR-WEB/PP-USR-WEB-06:https {
		address 10.1.17.86
	}   
   }
}

ltm virtual /PP-USR-WEB/vs-PP-USR-WEB-80 {
    destination /PP-USR-WEB/10.1.16.51:80
    ip-protocol tcp
    mask 255.255.255.255
    persist {
        /Common/cookie {
            default yes
        }
    }
    pool /PP-USR-WEB/pl-PP-USR-WEB-80
    profiles {
        /Common/http { }
        /Common/tcp { }
    }
	rules {
		/Common/_sys_https_redirect
	}
    source 0.0.0.0/0
    translate-address enabled
    translate-port enabled
}
ltm virtual /PP-USR-WEB/vs-PP-USR-WEB-VIP-443 {
    destination /PP-USR-WEB/10.1.16.51:443
    ip-protocol tcp
    mask 255.255.255.255
    persist {
        source_addr {
            default yes
        }
    }
    pool /PP-USR-WEB/pl-PP-USR-WEB-443
    profiles {
        /Common/http { }
        /Common/tcp { }
    }
    source 0.0.0.0/0
    source-address-translation {
        type automap
    }
    translate-address enabled
    translate-port enabled
}