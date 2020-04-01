# Description

A python command line tool to read an ECG SCP file and print structure information

# SCP Support

Currently following SCP section can be read with this tool

- Section0
- Section1
- Section3
- Section5 (partly)
- Section6 (partly)

# Command line usage

    python scpinfo.py ecgfile.scp


# Example output

```
--ScpRec--     		----
CRC            		1643
RecLen         		34144
--Section0--   		----
--Header--     		----
CRC            		21978
Id:            		0
Len            		136
VerNr          		20
ProNr          		20
               		----
Pointer Count  		12
Pointers       		0(136), 1(168), 2(18), 3(126), 4(22), 5(3342), 6(30084), 7(242), 8(0), 9(0), 10(0), 11(0)

--Section1--   		----
--Header--     		----
CRC            		24375
Id:            		1
Len            		168
VerNr          		20
ProNr          		20
               		----
Res            		
Tags           		12
FirstName      		
LastName       		Clark
Pat Id         		SBJ-123
LastName(2)    		
Age            		
DateOfBirth    		1953/5/8
Sex            		Male
Race           		Caucasian
Sys (mmHg)     		
Dia (mmHg)     		
MachineID      		----
InstNr         		0
DepNr          		11
DevId          		0
DevType        		0
Model          		LI250
               		----
Acq.Institution		
Date of Acquis.		2002/11/22
Time of Acquis.		09:10:00
Baseline Filter		0
LowPass Filter 		0
Text           		
Ecg Seq.       		
Med. History   		

--Section3--   		----
--Header--     		----
CRC            		45638
Id:            		3
Len            		126
VerNr          		20
ProNr          		20
               		----
RefBeatSet     		False
Sim-rec Leads  		12
LeadCount      		12
Leads          		I, II, V1, V2, V3, V4, V5, V6, III, aVR, aVL, aVF
SampleCount    		I (5000), II (5000), V1 (5000), V2 (5000), V3 (5000), V4 (5000), V5 (5000), V6 (5000), III (5000), aVR (5000), aVL (5000), aVF (5000)

--Section5--   		----
--Header--     		----
CRC            		43502
Id:            		5
Len            		3342
VerNr          		20
ProNr          		20
               		----
AVM (nV)       		2500
SampleTime (ms)		2000
Sample Enc     		2

--Section6--   		----
--Header--     		----
CRC            		61490
Id:            		6
Len            		30084
VerNr          		20
ProNr          		20
               		----
```



