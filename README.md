# Description

A python command line tool to read an SCP-ECG (https://en.wikipedia.org/wiki/SCP-ECG) file and print structure information about ECG traces and metadata.

# SCP-ECG Support

Currently following SCP section can be read with this tool

- Section0
- Section1
- Section2 (partly)
- Section3
- Section5 (partly)
- Section6 (partly)
- Section7 (partly)
- Section8 (partly)

Section2 is not interpreted currently, so if section2 is available  section5 and section6 samples would need recalculation using Huffman tables from section2.

# Command line usage

	usage: scpinfo.py [-h] [--csv section_id] scpfile

	positional arguments:
	  scpfile           input SCP file

	optional arguments:
	  -h, --help        show this help message and exit
	  --csv section_id  print leads in CSV format for section 5 or 6, specify here
						a section id


# Example output

	python scpinfo.py example/example.scp

```
--ScpRec--                     ----
CRC                            1643
RecLen                         34144
--Section0--                   ----
--SectionHeader--              ----
CRC                            21978
Id:                            0
Length                         136
VersionNr                      20
ProtocolNr                     20
Reserved                       SCPECG
----                           ----
Pointer Count                  12
Pointers                       0(136), 1(168), 2(18), 3(126), 4(22), 5(3342), 6(30084), 7(242), 8(0), 9(0), 10(0), 11(0)

--Section1--                   ----
--SectionHeader--              ----
CRC                            24375
Id:                            1
Length                         168
VersionNr                      20
ProtocolNr                     20
Reserved                       
----                           ----
Res                            
Tags                           12
LastName                       Clark
FirstName                      
Pat Id                         SBJ-123
Second LastName                
Age                            
DateOfBirth                    1953/5/8
Height                         
Weight                         
Sex                            Male
Race                           Caucasian
Sys (mmHg)                     
Dia (mmHg)                     
Acq. Device MachineID          ----
InstNr                         0
DepNr                          11
DevId                          0
DevType                        0
Model                          LI250
                               ----
Acq. Institution Desc          
Acq. Institution Desc          
Acq. Department Desc           
Anal. Department Desc          
Referring Physician            
Latest Confirm. Phys           
Technician Physician           
Room Description               
Stat Code                      
Date of Acquis.                2002/11/22
Time of Acquis.                09:10:00
Baseline Filter                0
LowPass Filter                 0
Other Filters                  
Ecg Seq.                       

--Section2--                   ----
--SectionHeader--              ----
CRC                            22179
Id:                            2
Length                         18
VersionNr                      20
ProtocolNr                     20
Reserved                       
----                           ----

--Section3--                   ----
--SectionHeader--              ----
CRC                            -19898
Id:                            3
Length                         126
VersionNr                      20
ProtocolNr                     20
Reserved                       
----                           ----
RefBeatSet                     False
Sim-rec Leads                  12
LeadCount                      12
Leads                          I, II, V1, V2, V3, V4, V5, V6, III, aVR, aVL, aVF
SampleCount                    I (5000), II (5000), V1 (5000), V2 (5000), V3 (5000), V4 (5000), V5 (5000), V6 (5000), III (5000), aVR (5000), aVL (5000), aVF (5000)

--Section4--                   ----
--SectionHeader--              ----
CRC                            4777
Id:                            4
Length                         22
VersionNr                      20
ProtocolNr                     20
Reserved                       
----                           ----

--Section5--                   ----
--SectionHeader--              ----
CRC                            -22034
Id:                            5
Length                         3342
VersionNr                      20
ProtocolNr                     20
Reserved                       
----                           ----
AVM (nV)                       2500
SampleTime (µs)                2000
Sample Encoding                Second difference
RefBeat 0, Bytes               272, 270, 258, 282, 266, 270, 260, 276, 322, 242, 288, 290

--Section6--                   ----
--SectionHeader--              ----
CRC                            -4046
Id:                            6
Length                         30084
VersionNr                      20
ProtocolNr                     20
Reserved                       
----                           ----
AVM (nV)                       2500
SampleTime (µs)                2000
Sample Encoding                Second difference
Bimodal compression            False
Lead Samples, Bytes            2510, 2426, 2354, 2468, 2412, 2356, 2450, 2634, 3002, 2162, 2668, 2596

--Section7--                   ----
--SectionHeader--              ----
CRC                            26535
Id:                            7
Length                         242
VersionNr                      20
ProtocolNr                     20
Reserved                       
----                           ----


```

# CSV output

	python scpinfo.py --csv 6 example/example.scp | head
	

```
      I     II     V1     V2     V3     V4     V5     V6    III    aVR    aVL    aVF
  11229     -2 -29953 -29185 -29953 -30721 -31233 -16897  -2821 -15629 -20080   -515
 -27845  28480  -7425  -7169  -7617  -7873  -7681 -23553  -6515 -22956  -4764  19237
 -27977  13979  25265 -17327  -4222  -9791 -14734   7543  -1545   9590  18382 -13345
  -8387  -6161 -26641 -28022 -14789  22981  -5134  26312 -17545  -9242  -1571  30587
 -19694   4974  15163  -8985 -18067  -9177   1591 -10096  -3905  11541  26469  -8452
 -25271  22905  23490  -6514  15955 -17305   7029 -18795  -1195 -27291 -26267  15329
  -9838  30646 -14314  -3722  15843   1775 -28789 -16525  20374  21798  28334  19941
  19666  28307  19422 -27796  26564  14199  10617  -8402  21630  22238  29415  -7109
  13033  22946  19062  14947 -26199  21013  15219  -2101   7927  25326 -25143 -11028	
```
