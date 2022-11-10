## Running examples

In order to test pysnmp functionalities, you can run SNMP simulators on your local environment.

One of possible ways to do it is to use [this project](https://github.com/tandrup/docker-snmpsim) to run docker container and map port 161 to the port of your choice, for example:

```commandline
docker run -d -p 163:161/udp tandrup/snmpsim 
```