#!/usr/bin/python
import time

#script_param_mark#

##BEGIN
##name=test-task
##description=this is a test task
##custom=test
##level=50
##interruptible=false
##nodeunit=1
##nodelimit=20
##nodeblacklimit=3
##properties=
##requirements=
##constraints=
##frequencytime=
##frequencycount=
##	JOBS           	 G_JOB_ID     		start		end
##		"job1"		754		774
##		"job2"		775		794
##		"job3"		795		814
##		"job4"		815		834
##		"job5"		835		854
##		"job6"		855		874
##		"job7"		875		894
##		"job8"		895		914
##		"job9"		915		934
##		"job10"		935		954
##		"job11"		955		974
##		"job12"		975		994
##		"job13"		995		1014
##		"job14"		1015		1034
##		"job15"		1035		1054
##		"job16"		1055		1074
##		"job17"		1075		1094
##		"job18"		1095		1114
##		"job19"		1115		1134
##		"job20"		1135		1154
##		"job21"		1155		1174
##		"job22"		1175		1194
##		"job23"		1195		1214
##		"job24"		1215		1234
##		"job25"		1235		1254
##		"job26"		1255		1274
##		"job27"		1275		1294
##		"job28"		1295		1314
##		"job29"		1315		1334
##		"job30"		1335		1354
##		"job31"		1355		1374
##		"job32"		1375		1394
##		"job33"		1395		1414
##		"job34"		1415		1434
##		"job35"		1435		1454
##		"job36"		1455		1474
##		"job37"		1475		1494
##		"job38"		1495		1514
##		"job39"		1515		1534
##		"job40"		1535		1554
##		"job41"		1555		1574
##		"job42"		1575		1594
##		"job43"		1595		1614
##		"job44"		1615		1634
##		"job45"		1635		1654
##		"job46"		1655		1674
##		"job47"		1675		1694
##		"job48"		1695		1714
##		"job49"		1715		1734
##		"job50"		1735		1754
##		"job51"		1755		1774
##		"job52"		1775		1794
##		"job53"		1795		1814
##		"job54"		1815		1834
##		"job55"		1835		1854
##		"job56"		1855		1874
##		"job57"		1875		1894
##		"job58"		1895		1914
##		"job59"		1915		1934
##		"job60"		1935		1954
##		"job61"		1955		1974
##		"job62"		1975		1994
##		"job63"		1995		2014
##		"job64"		2015		2034
##		"job65"		2035		2054
##		"job66"		2055		2074
##		"job67"		2075		2094
##		"job68"		2095		2114
##		"job69"		2115		2134
##		"job70"		2135		2154
##		"job71"		2155		2174
##		"job72"		2175		2194
##		"job73"		2195		2214
##		"job74"		2215		2234
##		"job75"		2235		2254
##		"job76"		2255		2274
##		"job77"		2275		2294
##		"job78"		2295		2314
##		"job79"		2315		2334
##		"job80"		2335		2354
##		"job81"		2355		2374
##		"job82"		2375		2394
##		"job83"		2395		2414
##		"job84"		2415		2434
##		"job85"		2435		2454
##		"job86"		2455		2474
##		"job87"		2475		2494
##		"job88"		2495		2514
##		"job89"		2515		2534
##		"job90"		2535		2554
##		"job91"		2555		2574
##		"job92"		2575		2594
##		"job93"		2595		2614
##		"job94"		2615		2634
##		"job95"		2635		2654
##		"job96"		2655		2674
##		"job97"		2675		2694
##		"job98"		2695		2714
##		"job99"		2715		2734
##		"job100"		2735		2754
##		"job101"		2755		2774
##		"job102"		2775		2794
##		"job103"		2795		2814
##		"job104"		2815		2834
##		"job105"		2835		2854
##		"job106"		2855		2874
##		"job107"		2875		2894
##		"job108"		2895		2914
##		"job109"		2915		2934
##		"job110"		2935		2954
##		"job111"		2955		2974
##		"job112"		2975		2994
##		"job113"		2995		3014
##		"job114"		3015		3034
##		"job115"		3035		3054
##		"job116"		3055		3074
##		"job117"		3075		3094
##		"job118"		3095		3114
##		"job119"		3115		3134
##		"job120"		3135		3154
##		"job121"		3155		3174
##		"job122"		3175		3194
##		"job123"		3195		3214
##		"job124"		3215		3234
##		"job125"		3235		3254
##		"job126"		3255		3274
##		"job127"		3275		3294
##		"job128"		3295		3314
##		"job129"		3315		3334
##		"job130"		3335		3354
##		"job131"		3355		3374
##		"job132"		3375		3394
##		"job133"		3395		3414
##		"job134"		3415		3434
##		"job135"		3435		3454
##		"job136"		3455		3474
##		"job137"		3475		3494
##		"job138"		3495		3514
##		"job139"		3515		3534
##		"job140"		3535		3554
##		"job141"		3555		3574
##		"job142"		3575		3594
##		"job143"		3595		3614
##		"job144"		3615		3634
##		"job145"		3635		3654
##		"job146"		3655		3674
##		"job147"		3675		3694
##		"job148"		3695		3714
##		"job149"		3715		3734
##		"job150"		3735		3754
##		"job151"		3755		3774
##		"job152"		3775		3794
##		"job153"		3795		3814
##		"job154"		3815		3834
##		"job155"		3835		3854
##		"job156"		3855		3874
##		"job157"		3875		3894
##		"job158"		3895		3914
##		"job159"		3915		3934
##		"job160"		3935		3954
##		"job161"		3955		3974
##		"job162"		3975		3994
##		"job163"		3995		4014
##		"job164"		4015		4034
##		"job165"		4035		4054
##		"job166"		4055		4074
##		"job167"		4075		4094
##		"job168"		4095		4114
##		"job169"		4115		4134
##		"job170"		4135		4154
##		"job171"		4155		4174
##		"job172"		4175		4194
##		"job173"		4195		4214
##		"job174"		4215		4234
##		"job175"		4235		4254
##		"job176"		4255		4274
##		"job177"		4275		4294
##		"job178"		4295		4314
##		"job179"		4315		4334
##		"job180"		4335		4354
##		"job181"		4355		4374
##		"job182"		4375		4394
##		"job183"		4395		4414
##		"job184"		4415		4434
##		"job185"		4435		4454
##		"job186"		4455		4474
##		"job187"		4475		4494
##		"job188"		4495		4514
##		"job189"		4515		4534
##		"job190"		4535		4554
##		"job191"		4555		4574
##		"job192"		4575		4594
##		"job193"		4595		4614
##		"job194"		4615		4634
##		"job195"		4635		4654
##		"job196"		4655		4674
##		"job197"		4675		4694
##		"job198"		4695		4714
##		"job199"		4715		4734
##		"job200"		4735		4754
##		"job201"		4755		4774
##		"job202"		4775		4794
##		"job203"		4795		4814
##		"job204"		4815		4834
##		"job205"		4835		4854
##		"job206"		4855		4874
##		"job207"		4875		4894
##		"job208"		4895		4914
##		"job209"		4915		4934
##		"job210"		4935		4954
##		"job211"		4955		4974
##		"job212"		4975		4994
##		"job213"		4995		5014
##		"job214"		5015		5034
##		"job215"		5035		5054
##		"job216"		5055		5074
##		"job217"		5075		5094
##		"job218"		5095		5114
##		"job219"		5115		5134
##		"job220"		5135		5154
##		"job221"		5155		5174
##		"job222"		5175		5194
##		"job223"		5195		5214
##		"job224"		5215		5234
##		"job225"		5235		5254
##		"job226"		5255		5274
##		"job227"		5275		5294
##		"job228"		5295		5314
##		"job229"		5315		5334
##		"job230"		5335		5354
##		"job231"		5355		5374
##		"job232"		5375		5394
##		"job233"		5395		5414
##		"job234"		5415		5434
##		"job235"		5435		5454
##		"job236"		5455		5474
##		"job237"		5475		5494
##		"job238"		5495		5514
##		"job239"		5515		5534
##		"job240"		5535		5554
##		"job241"		5555		5574
##		"job242"		5575		5594
##		"job243"		5595		5614
##		"job244"		5615		5634
##		"job245"		5635		5654
##		"job246"		5655		5674
##		"job247"		5675		5694
##		"job248"		5695		5700

##ENDJOBS
##END

def RBcmd(cmdStr, continueOnErr = False, myShell = False):
    print cmdStr 
    cmdp = subprocess.Popen(cmdStr,stdin = subprocess.PIPE,stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = myShell)
    cmdp.stdin.write('3/n')
    cmdp.stdin.write('4/n')
    exitcode = 0
    while cmdp.poll() is None:
        resultLine = cmdp.stdout.readline().strip()
        
        if resultLine != '':
            print resultLine                
    resultStr = cmdp.stdout.read()
    resultCode = cmdp.returncode   
    
    if exitcode == -1:
        sys.exit(-1)

    if not continueOnErr:
        if resultCode != 0:
            sys.exit(resultCode)
    return resultStr

for j in range(3):
    if subprocess.call("net use * /delete /y"):
        print "clean mapping network failed."
        time.sleep(5)
        print "Wait 5 seconds..."
    else:
        print "clean mapping network successfully."
        break


for j in range(3):
    if subprocess.call("net use X: //172.21.0.3/d/inputdata5/100000500/100000959/X"):
        print " mapping network failed   net use X: //172.21.0.3/d/inputdata5/100000500/100000959/X ."
        time.sleep(5)
        print "Wait 5 seconds..."
    else:
        print "mapping network successfully."
        break
os.system(r'wmic process where name="rlm_redshift.exe" delete')
os.system(r'start C:/redshift_rlm_server_win64/rlm_redshift.exe')

REDSHIFT_LOCALDATAPATH = r"C:/temp/REDSHIFT/CACHE"
os.environ['REDSHIFT_LOCALDATAPATH'] = REDSHIFT_LOCALDATAPATH
os.environ['LOCALAPPDATA'] = REDSHIFT_LOCALDATAPATH
os.environ['REDSHIFT_LICENSE'] = "5059@127.0.0.1"
os.environ['REDSHIFT_LICENSEPATH'] = r"C:/redshift_rlm_server_win64/redshift-core2.lic"

cmdStr = '"C:/Program Files/Autodesk/maya2017/bin/render.exe" -s %s  -e %s -b 1 -proj "X:" -rd "//172.21.0.9/d/outputdata5/100000500/100000959" -cam "renderCam_v02:renderCamShape" -r redshift -logLevel 1 -gpu {0,1}   "X:/cloud/Uber/UBR_010_0010_light_vtol_wings_A_v011.ma"'  % (start ,end)
for line  in  RBcmd(cmdStr):
    print line



