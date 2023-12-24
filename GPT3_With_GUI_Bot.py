import GPT3_Core
import os
import cv2
import azure.cognitiveservices.speech as speechsdk
from pykakasi import kakasi
import json

speech_config = speechsdk.SpeechConfig(subscription=open('azspeech.key','r').readline(), region='japaneast')
# Note: the voice setting will not overwrite the voice element in input SSML.
speech_config.speech_synthesis_voice_name = "ja-JP-MayuNeural"
# use the default speaker as audio output.
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

jsonparam = json.load(open('gpt4token.key', 'r'))
myGPT3_A = GPT3_Core.theGPT3(apiKey=jsonparam['key'], endpoint=jsonparam['endpoint'], name='Sakura')
myGPT3_B = GPT3_Core.theGPT3(apiKey=jsonparam['key'], endpoint=jsonparam['endpoint'], name='Nagisa')

def show_simliar_figure(description, txtoutput, name):
    allfigures = os.listdir('figs')
    maxsimliar = 0
    selectedfigure = None
    for i in allfigures:
        simliar = 0
        for j in description:
            if j in i:
                simliar += 1
        if simliar > maxsimliar:
            maxsimliar = simliar
            selectedfigure = i
    print('Selected Figure: ' + selectedfigure)
    img = cv2.imread('figs/' + selectedfigure)
    #txtPos = (int(img.shape[0] * 0.1), int(img.shape[1] * 0.8))
    #cv2.putText(img, txtoutput, txtPos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (128, 128, 255), 2)
    cv2.imshow(name, img)
    # make sure the window is on top
    cv2.setWindowProperty(name, cv2.WND_PROP_TOPMOST, 1)
    cv2.waitKey(1)

kakasi_instance = kakasi()

def kakasi_conv(txt):
    txtproc = kakasi_instance.convert(txt)
    #print(txtproc)
    txtHiragana = ''
    for i in txtproc:
        txtHiragana += i['hira']
    return txtHiragana

def talk_with_gui(txtinput, username, theGPT):
    txtHiragana = kakasi_conv(txtinput)
    #print('Input Hiragana: ' + txtHiragana)
    res = theGPT.interactive(txtHiragana, username)
    #print(res)
    Emotional = res[0]
    Action = res[1]
    TxtOutput = res[2]
    if '<br>' in TxtOutput:
        TxtOutput = TxtOutput.replace('<br>', '\n')
    DesiredFigFile = Emotional.split(' ')[0] + '_' + Action.split(' ')[0] + '.png'
    #print('Emotional: ' + Emotional)
    #print('Action: ' + Action)
    #print('Founding Figure: ' + FigFile)
    show_simliar_figure(DesiredFigFile, TxtOutput, theGPT.name)
    #print('TxtOutput: ' + TxtOutput)
    print(theGPT.name + ': ' + TxtOutput)
    txtHiragana = kakasi_conv(TxtOutput)
    #print('Output Hiragana: ' + txtHiragana)
    print(theGPT.name + ': ' + txtHiragana)
    result = speech_synthesizer.speak_text_async(TxtOutput).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    return TxtOutput


while True:
    txtinput = input('Type something: ')
    if txtinput == '':
        continue
    break

GPTA_Response = talk_with_gui(txtinput, 'Seitaku', myGPT3_A)
myGPT3_B.just_add_chat_history(txtinput, 'Seitaku') # Let the GPT3_B know what the user said.

while True:
    GPTB_Response = talk_with_gui(GPTA_Response, myGPT3_A.name, myGPT3_B)
    GPTA_Response = talk_with_gui(GPTB_Response, myGPT3_B.name, myGPT3_A)