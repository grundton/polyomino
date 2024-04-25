<CsoundSynthesizer>
<CsOptions>
-odac1 -b128 -B256 
;-b16384 -B65536
;-otests/csds/resonator_visco_concat.wav
;-otest2.wav
;-b16384 -B65536
</CsOptions>
<CsInstruments>

sr  = 44100
ksmps = 2048
nchnls  = 2
0dbfs   = 1

  gihandle OSCinit 8000


;;________OSC_SCHEDULER_____________________________________________
;; 			receives OSC FREQ and schedules instrument allocation and 
;;			frequency. 
instr 1
    kf11 init 0
    kf12 init 0
    kf21 init 0
    kf22 init 0
    kf31 init 0
    kf32 init 0
    kf41 init 0
    kf42 init 0
    k_note_name init 0
    
    
nxtmsg:
	kk1  OSClisten gihandle, "/instrument", "ff", kf11, kf12
   
	if (kk1 == 0) kgoto ex

    	k_note_name = kf11/100 + 2 ; used to get fractional note names (e.g. kf = 12 -> 2.12, where .12 is the "tag"))

    	kcountactive active k_note_name ; check numactive instances of instrument/note
    	printks "nxtmsg \n", 0.01
    	;k_eval_1 = (kf12!=0.000000)
    	;print "Evaluate %b: %n", k_eval_1
    	
    	;if (kf12!=0.000000) kgoto _field_active ; use this out how to turn off single note
    	if (kf12!=0.000000) kgoto _activate_note
    	
    	
    	if (kf12==0.000000) kgoto _deactivate_note
    	
    	goto ex
    	
    	
    	
;_field_active:   
	; if second OSC value kf12 != 0, the field is active.
	; if a note is already playing, it should not start a new note
	; if there is no note playing, it should start a new one 	
;    		;printks "field_active", 0.01
;    		if(kcountactive==0) kgoto _note_playing_false
;    		kgoto _note_playing_true
    		
;_note_playing_true:
;			;printks "NPT \n", 0.01
;			ktemp = 1+1 ; placeholder
;			goto _end_section

;_note_playing_false:
;			;printks "NPF \n", 0.01
;			event "i", k_note_name, 0, -1, kf12 
;			goto _end_section
    		
    		
_deactivate_note:
			;printks "DN \n", 0.01
			turnoff2 k_note_name, 0, 1
			;event "i", k_note_name, 0, 0, kf12 
			;event "i", k_note_name, 0, 0, kf12 ; duration of 0 stops note
			goto _end_section
    	
_activate_note:
			;printks "AN \n", 0.01
   			event "i", k_note_name, 0, -1, kf12
   			goto _end_section
    	
    	
_end_section:
		;printks "END \n", 0.01
 		ktemp = 1+1 ; placeholder
    	kgoto nxtmsg  
ex:
	prints "."
endin
  
;;________INSTRUMENTS_______________________________________________


gaRvbSend    init      0 ; global audio variable initialized to zero

instr 2
	xtratim 3
	i_freq = p4 	; either 0 or a specific frequency. 
	
	; Attack time.
	iattack = 1
	; Decay time.
	idecay = 1
	; Sustain level.
	isustain = 0.6
	; Release time.
	irelease = 5
	aenv madsr iattack, idecay, isustain, irelease
	;kenv	linsegr	0, 0.5, 0.1, 3, 0
	;asig oscils 0.1, i_freq, 0, 2

	iRvbSendAmt  =         0.3  
	
	kModsigLeft oscil 0.002, 0.101
	kModsigRight oscil 0.002, 0.11
	asigLeft vco2 1, i_freq*(1+kModsigLeft)
	asigRight vco2 1, i_freq*(1+kModsigRight)


	outs (asigLeft*aenv*0.1)*(1-iRvbSendAmt), (asigRight*aenv*0.1)*(1-iRvbSendAmt)
	gaRvbSend    =         gaRvbSend + ((asigLeft+asigLeft)*0.5 * iRvbSendAmt)

endin

instr 3
	kFadout   init      1
	krel      release   ;returns "1" if last k-cycletu
	if krel == 1 && p3 > 0 then ;if so, and negative p3:
		xtratim   2      
		kFadout   linsegr    1, 2, 0 ;and make fade out
	endif
	
	i_freq = p4 	; either 0 or a specific frequency. 
	
	;
	;kenv	linsegr	0, 0.5, 0.1, 3, 0
	;asig oscils 0.1, i_freq, 0, 2
	asig vco2 1, i_freq

	outs asig*0.1*kFadout, asig*0.1*kFadout

endin


instr 5 ; reverb - always on
kroomsize    init      0.9          ; room size (range 0 to 1)
kHFDamp      init      0.3           ; high freq. damping (range 0 to 1)
; create reverberated version of input signal (note stereo input and output)
aRvbL,aRvbR  freeverb  gaRvbSend, gaRvbSend,kroomsize,kHFDamp
             outs      aRvbL, aRvbR ; send audio to outputs
             clear     gaRvbSend    ; clear global audio variable
  endin




</CsInstruments>
<CsScore>
 
i2 0 1 200 
;i2 0.2 0.8 400 
;i2 0.4 0.6 600 
;i2 0.6 0.4 800 

i1 1 3600 

</CsScore>
</CsoundSynthesizer>



	










<bsbPanel>
 <label>Widgets</label>
 <objectName/>
 <x>0</x>
 <y>0</y>
 <width>0</width>
 <height>0</height>
 <visible>true</visible>
 <uuid/>
 <bgcolor mode="background">
  <r>240</r>
  <g>240</g>
  <b>240</b>
 </bgcolor>
</bsbPanel>
<bsbPresets>
</bsbPresets>
