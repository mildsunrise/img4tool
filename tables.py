component_names = dict(
	# (components in iSCPreboot)
	lpol='Local boot policy',
	sepi='SEP firmware',

	# (components inside <vuid>/boot/<nsih>/usr/standalone/firmware)
	isys='Root hash',
    xsys='x86 root hash',
	csys='Base system root hash',
	dtre='Embedded device tree',
	ibot='iBoot (stage 2)',
	ibdt='iBoot (stage 2) data',
	anef='ANE firmware',
	aopf='AOP firmware',
	avef='AVE firmware',
	dcp2='DCP2 firmware',
	gfxf='GFX firmware',
	ipdf='Input device firmware',
	ispf='ISP firmware',
	mtpf='MTP firmware',
	mtfw='Multitouch firmware',
	pmpf='PMP firmware',
	siof='SmartIO firmware',
	trst='Static trust cache',
    xstc='x86 static trust cache',
	bstc='Base system trust cache',
    xbtc='x86 base system trust cache',

	# (components signed by APticket that are not in the previous section) <-- no longer true
	msys='mtree',
    xmtr='x86 mtree',
	bsys='recoveryOS rootfs ramdisk',
	ibec='iBEC DFU firmware',
    ibss='iBSS DFU firmware',
	krnl='Kernelcache',
	rdsk='ramdisk?',
	rkrn='recovery kernelcache?',
	rdtr='recovery device tree?',
	rlgo=None,
	rosi=None,
	rtsc='recovery trust cache',
    xrtc='x86 recovery trust cache',
    cssy='cryptex(?) root hash',
    trcs='cryptex(?) trust cache',
    casy='something(?) root hash',
	trca='something(?) trust cache',

	# (other firmware blobs)
    illb='iBoot Low Level Bootloader (aka stage 1)',
    ibd1='iBoot (stage 1) data',
    ciof='CIO firmware',
    tmuf='TMU firmware',
    ansf='ANS firmware',
    dcpf='DCP firmware',
    dven='related to display calibration',

	# (embedded images)
    logo='applelogo embedded image',
    recm='recoverymode embedded image',
    glyP='glphyplugin embedded image',
    chg0='batterycharging0 embedded image',
    chg1='batterycharging1 embedded image',
    batF='batteryfull embedded image',
    bat0='batterylow0 embedded image',
    bat1='batterylow1 embedded image',
    rlg0='recoveryoslogo0 embedded image',
    rlg1='recoveryoslogo1 embedded image',

    trbb='Bootability trust cache',
    fuos='fully untrusted OS',
)

payload_tags = dict(
	hrlp=(bool, 'Is "normal local boot policy"'),
	rolp=(bool, 'Is "recoveryOS local boot policy"'),

	# (from bputil)

	lpnh=(bytes, 'Local Policy Nonce Hash'),
	rpnh=(bytes, 'Remote Policy Nonce Hash'),
	ronh=(bytes, 'Recovery OS Policy Nonce Hash'),

	ECID=(int, 'Unique Chip ID'),
	BORD=(int, 'Board ID'),
	CHIP=(int, 'Chip ID'),
	CEPO=(int, 'Certificate Epoch'),
	SDOM=(int, 'Security Domain'),
	CPRO=(bool, 'Production Status'),
	CSEC=(bool, 'Security Mode'),
	lobo=(bool, 'Local Boot'),
	love=(bytes, 'OS Version'),
	vuid=(bytes, 'Volume Group UUID'),
	kuid=(bytes, 'KEK Group UUID'),
	nsih=(bytes, 'Next Stage Image4 Hash'),
	spih=(bytes, 'Cryptex1 Image4 Hash'),
	stng=(int, 'Cryptex1 Generation'),
	auxp=(None, 'User Authorized Kext List Hash'),
	auxi=(None, 'Auxiliary Kernel Cache Image4 Hash'),
	auxr=(None, 'Kext Receipt Hash'),
	coih=(None, 'CustomKC or fuOS Image4 Hash'),
	smb0=(bool, 'Boot Policy Security lowered to Reduced'),
	smb1=(bool, 'Boot Policy Security lowered to Permissive'),
	smb2=(bool, '3rd Party Kexts Status'),
	smb3=(bool, 'User-allowed MDM Control'),
	smb4=(bool, 'DEP-allowed MDM Control'),
	sip0=(bool, 'SIP Status'),
	sip1=(bool, 'Signed System Volume Status'),
	sip2=(bool, 'Kernel CTRR Status'),
	sip3=(bool, 'Boot Args Filtering Status'),

	# (apticket inspection)

	augs=(int, None),
	prtp=(bytes, 'Device ID'),
	sdkp=(bytes, 'OS identifier?'),
	srvn=(bytes, None),
	tagt=(bytes, 'Product part ID'),
	tatp=(bytes, 'Product ID'),
	uidm=(bool, None),

	# (ECID-specific APtickets)

	BNCH=(bytes, None),
	esdm=(int, None),
	snon=(bytes, None),
	snuf=(bytes, None),

    vnum=(bytes, "Version number"),
)

payp_tags = dict(
    kcep=(int, 'Kernelcache entry point (virtual address)'),
    kclo=(int, 'Kernelcache lowest virtual address'),
)
