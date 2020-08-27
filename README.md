# INT-filter: Mitigating Data Collection Overhead for High-Resolution In-band Network Telemetry

Fine-grained, network-wide visibility is vital to reliably maintaining and troubleshooting high-density, mega-scale modern data center networks to accommodate heterogeneous mission-critical applications. However, traditional management protocols, such as SNMP, fall short of highresolution monitoring for highly dynamic data center networks due to the inefficient controller-driven, per-device polling mechanism. With end host-launched full-mesh pings, Pingmesh is capable of providing the maximum latency measurement coverage. Pingmesh is excellent but still flawed. It cannot extract hop-by-hop latency or look into the queue depth inside switches for in-depth analysis, but, for network applications such as load balancing, failure localization and management automation, these underlying information is increasingly insightful. In-band Network Telemetry (INT), one of the killer applications of P4, allows probe or data packets to query device-internal states, such as queue depth and queuing latency, when they pass through the data plane pipeline, which is considered promising and has been embedded into several venders’ latest merchant silicon. As a chip-level primitive, INT simply defines the interaction between the incoming packets and the device-internal states for monitoring. For network-wide telemetry, further orchestration on top of INT is needed.

There are two design patterns to achieve network-wide measurement coverage based on INT, that is, distributed probing and centralized probing. HULA follows the distributed probing and adopts the ToR switches to flood the probes into data center network’s multi-rooted topology for measurement coverage. Since each probe sender does not have the global view of the network to make any coordination, one link will be repetitively monitored by many probes simultaneously with huge bandwidth overhead. For high-resolution monitoring, the bandwidth waste will get even worse. To overcome this limitation, centralized probing relies on the SDN controller to make optimized probing path planning. For example, INT-path collects the network topology and generates non-overlapped probing paths that cover the entire network with a minimum path number using an Euler trail-based algorithm. INT-path is theoretically perfect but still has deployment flaws. First, it still explicitly relies on bandwidth-occupying probe packets. Besides, it embeds source routing into the probe packet to specify the route the probe takes. This makes the probe header even bloated especially for a longer probing path. 

![Image text](https://github.com/Ng-95/INT-filter/blob/master/Experiment%20result/fig3/Architecture.png)

To tackle the above problems, in this work, we propose INT-label, an ultra-lightweight In-band Network-Wide Telemetry architecture. Distinct from previous work, INT-label follows a “probeless” architecture, that is, the INT-label-capable device periodically labels device-internal states onto data packets rather than explicitly introducing probe packets. Specifically, on each outgoing port of the device, the packets will be sampled according to a predefined label interval T and labelled with the instant device-internal states. As a result, INT-label can still achieve network-wide coverage with finegrained telemetry resolution while introducing minor bandwidth overhead. Along the forwarding path consisting of different devices, the same packet will be labelled independently simply according to the local sample decision, that is to say, INT-label is completely stateless without involving any probing path-related dependency. Therefore, there is no need to leverage the SDN controller for conducting centralized path planning. 

INT-label is decoupled from the topology, allowing seamless adaptation to link failures. Like INT, INT-label also relies on the programmability of data plane provided by P4 and the in-network labelling is designed to be transparent to the end hosts. The INT information will be extracted and sent to the SDN controller at the last-hop network device for network-wide telemetry data analysis. To avoid telemetry resolution degradation due to potential loss of labelled packets on some unreliable links, we further design a feedback mechanism to adaptively change the label frequency when the controller gets aware of the packet loss by analyzing the telemetry result.

# Experiment result
Experiment result contains preliminary experimental results data and figures.

## Fig.1
Upload rates under different probe intervals (INT-path vs. HULA).

## Fig.2
Upload rates under different network sizes of FatTree topology.

## Fig.3
The architecture of INT-filter.

## Fig.4
The impact of degree of polynomial fitting on the upload decrease.

## Fig.5
The impact of data plane probe frequency on upload rate.

## Fig.6
The impact of prediction window size on the computational complexity and upload rate.

## Fig.7
The impact of threshold on the computational complexity and upload rate.

# INT-filter
We build an emulation-based network prototype to demonstrate INT-label performance. The hardware configuration is 20*2Ghz CPU and 64GB memory with Ubuntu 16.04 OS. The prototype is based on Mininet and consists of 1 controller, 4 Spine switches, 4 Leaf switches, 4 ToR switches and 8 servers.
The INT_filter include five modules:topology, flow_table, p4_source_code, packet, controller and args.

## topology
Establish a mininet topology and start the packet send&receive process.

### clos.py
First, compile p4 program.
Establish a mininet topology. Here we can control the link bandwidth, delay, maximum queue length, etc.
And initialize the database and start the packet send&receive process.

## flow_table
Initialize the OpenFlow Pipeline of each OVS.

### flow_table_gen.py
Generate the flow table.

### command.sh
Update the flow table.

### flow_table
Include OpenFlow Pipeline.

## p4_source_code
Include p4 source code, implemented SR-based INT function and data plane labelling function of INT-label.

### my_int.p4
Include Headers, Metadatas, parser, deparser and checksum calculator.
SR-based INT function and data plane labelling function are implemented in the program.

### my_int.json
The json file that compiled from my_int.p4 by p4c compiler.

### run.sh
For compiling the my_int.p4.

## packet
Implement send&receive packet on the server.

### send
Send packet.

#### send_int_probe.py
Based on SR and INT-path, each host send probe packet to a host which is not in the same pod.

### send_data.py
Based on SR, server1, server3, server6 and server8 send randomly-generated traffic (packet size = 1kB) to the other servers.

### receive
Receive packet and parse it.

#### parse.py
Extract the INT information.

#### predict.py
Predict the state using historical data.

#### receive_basic.py
Receive packets and parse them using parse.py. And write the latest INT information into the database without filtering.

#### receive_filter.py
Filter the uploaded data and update the historical state database.

## controller 
Implement controller-driven adaptive labelling function and calculate the coverage rate.

### read_redis.py
Read experimental results.

## args
Store global variable of the prediction window size.

# How to run INT-filter
If you installed the dependencies and configured the database successfully, then you can run the system with commands below:

## Base
```
cd topology/
python clos.py
```

You can change bandwidth, max queue size and background traffic rate in clos.py to test INT-filter under different conditions.
If you change the topology, you need to modify packet/send/send.py.
You can view the results of the experiment through controller/read_redis.py.

# HULA
We reproduce the code of HULA.
Its the role of each file and usage are similar to those of INT-label.
