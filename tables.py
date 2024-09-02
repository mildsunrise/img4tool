component_names = dict(
	# (components in iSCPreboot)
	lpol='Local boot policy',
	sepi='SEP firmware',

	# (components inside <vuid>/boot/<nsih>/usr/standalone/firmware)
	isys='Root hash',
	csys='Base system root hash',
	dtre='Embedded device trees',
	ibot='iBoot (stage 2)',
	ibdt='iBoot data',
	anef='ANE firmware',
	aopf='AOP firmware',
	avef='AVE firmware',
	dcp2='DCP firmware (v2?)',
	gfxf='GFX firmware',
	ipdf='Input device firmware',
	ispf='ISP firmware',
	mtpf='MTP firmware',
	mtfw='Multitouch firmware',
	pmpf='PMP firmware',
	siof='SmartIO firmware',
	trst='Static trust cache',
	bstc='Base system trust cache',

	# (components signed by APticket that are not in the previous section)
	msys=None,
	bsys='recoveryOS rootfs ramdisk',
	ibec=None,
	krnl='Kernelcache',
	rdsk='ramdisk?',
	rkrn='recovery kernelcache?',
	rdtr='recovery device tree?',
	rlgo=None,
	rosi=None,
	rtsc=None,
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
	smb0=(bool, 'Boot Policy Security Mode'),
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
)
