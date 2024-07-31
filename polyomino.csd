<CsoundSynthesizer>
<CsOptions>
-odac1 ;-b128 -B256 
;-b16384 -B65536
;-otests/csds/resonator_visco_concat.wav
;-otest2.wav
;-b16384 -B65536
;-b256 -B1024
</CsOptions>
<CsInstruments>

sr  = 44100
ksmps = 64
nchnls  = 2
0dbfs   = 1

;; Global Variable definitions
;; OscHandle & Morph_factor & Volume
  gihandle OSCinit 8000
  gk_morph init 0
  gk_volume init 0.5


;;________OSC_SCHEDULER_____________________________________________
;; 			receives OSC FREQ and schedules instrument allocation and 
;;			frequency. 
instr 1
    kf11 init 0 ; note name
    kf12 init 0 ; 5 limit just intonation frequency
    kf13 init 0 ; 12 TET frequency
    kf21 init 0 
    kf22 init 0
    kf31 init 0
    kf32 init 0
    kf41 init 0
    kf42 init 0
    k_note_name init 0
    
    ;kMorph  OSClisten gihandle, "/morphfactor", "ff", kf11, kf12
    
nxtmsg:
	kk1  OSClisten gihandle, "/instrument", "ff", kf11, kf12
	kk2  OSClisten gihandle, "/instrument_12tet", "ff", kf11, kf13
   
	if (kk1 == 0) kgoto ex

    	k_note_name = kf11/100 + 2 ; used to get fractional note names (e.g. kf = 12 -> 2.12, where .12 is the "tag"))

    	kcountactive active k_note_name ; check numactive instances of instrument/note
    	;printks "nxtmsg \n", 0.01
    	;k_eval_1 = (kf12!=0.000000)
    	;print "Evaluate %b: %n", k_eval_1
    	
    	;if (kf12!=0.000000) kgoto _field_active ; use this out how to turn off single note
    	if (kf12!=0.000000) kgoto _activate_note
    	
    	
    	if (kf12==0.000000) kgoto _deactivate_note
    	
    	goto ex
    	
    		
_deactivate_note:
			;printks "DN \n", 0.01
			turnoff2 k_note_name, 0, 1
			;event "i", k_note_name, 0, 0, kf12 
			;event "i", k_note_name, 0, 0, kf12 ; duration of 0 stops note
			goto _end_section
    	
_activate_note:
			;printks "AN \n", 0.01
   			event "i", k_note_name, 0, -1, kf12, kf13
   			goto _end_section
    	
    	
_end_section:
		;printks "END \n", 0.01
 		ktemp = 1+1 ; placeholder
    	kgoto nxtmsg  
ex:
	prints "."
endin

;;________OSC_Morph & Volume________________________________________
instr 11
	kk_morph  OSClisten gihandle, "/morph_factor", "f", gk_morph  
	kk_volume  OSClisten gihandle, "/volume", "f", gk_volume
endin
  
;;________INSTRUMENTS_______________________________________________


gaRvbSend    init      0 ; global audio variable initialized to zero

instr 2
	xtratim 3
	i_freq_5lim = p4 	; either 0 or a specific frequency in 5lim. 
	i_freq_12tet = p5	; either 0 or a specific frequency in 12tet.
	k_morph init 0 ; Morph-factor. Scales between 5-limit just intonation and 12 TET.
	k_volume init 0.5 ; Volume-factor. Scales between 0 and 1.


	; Attack time.
	iattack = 1
	; Decay time.
	idecay = 1
	; Sustain level.
	isustain = 0.6
	; Release time.
	irelease = 2
	aenv madsr iattack, idecay, isustain, irelease
	;kenv	linsegr	0, 0.5, 0.1, 3, 0
	;asig oscils 0.1, i_freq, 0, 2

	iRvbSendAmt  =         0.1  
	
	;;Assign Values + Smoothing
	k_morph portk gk_morph, 0.05
	k_freq = (1-k_morph) * i_freq_5lim + k_morph * i_freq_12tet
	k_vol portk gk_volume, 0.05


	kModsigLeft oscil 0.002, 0.101
	kModsigRight oscil 0.002, 0.11

	asigLeft vco2 1, k_freq*(1+kModsigLeft), 2, 0.5
	asigRight vco2 1, k_freq*(1+kModsigRight), 2, 0.5

	; Lowpass Filter
	asigLeft    moogladder   asigLeft, kcf, 0.9 ; filter audio signal
	asigRight    moogladder   asigRight, kcf, 0.9 ; filter audio signal

	outs k_vol*(asigLeft*aenv*0.1)*(1-iRvbSendAmt), k_vol*(asigRight*aenv*0.1)*(1-iRvbSendAmt)
	gaRvbSend    =         gaRvbSend + k_vol*((asigLeft+asigLeft)*0.5 * iRvbSendAmt)


endin




instr 99 ; reverb - always on
kroomsize    init      0.7          ; room size (range 0 to 1)
kHFDamp      init      0.3           ; high freq. damping (range 0 to 1)
; create reverberated version of input signal (note stereo input and output)
aRvbL,aRvbR  freeverb  gaRvbSend, gaRvbSend,kroomsize,kHFDamp
             outs      0.5* aRvbL, 0.5*aRvbR ; send audio to outputs
             clear     gaRvbSend    ; clear global audio variable
endin


</CsInstruments>
<CsScore> 
; Test tone 
i2 0 1 200 202

; OSC Voice handling
i1 0 3600 
; OSC Morph and Volume
i11 0 3600
; Reverb
i99 0 3600

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
