from cgi import parse_multipart, parse_header
from io import BytesIO
from base64 import b64decode
from ibm_watson import SpeechToTextV1, ApiException, NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator
import json, os


def main(args):

    # Parse incoming request headers
    _c_type, p_dict = parse_header(
        args['__ow_headers']['content-type']
    )
    
    # Decode body (base64)
    decoded_string = b64decode(args['__ow_body'])

    # Set Headers for multipart_data parsing
    p_dict['boundary'] = bytes(p_dict['boundary'], "utf-8")
    p_dict['CONTENT-LENGTH'] = len(decoded_string)
    
    # Parse incoming request data
    multipart_data = parse_multipart(
        BytesIO(decoded_string), p_dict
    )

    carro = ''
    if 'car' in multipart_data:
        carro = multipart_data.get('car')[0]

    retorno = {
        'recommendation': ''
    }

    texto_audio = ''

    if 'audio' in multipart_data:
        # Build flac file from stream of bytes
        fo = open("audio_sample.flac", 'wb')
        fo.write(multipart_data.get('audio')[0])
        fo.close()

    

        # Basic Authentication with Watson STT API
        stt_authenticator = BasicAuthenticator(
            'apikey',
            'qa8K2ibwTd2CoJAvrUfhSNaZL2nlrIjaafpjTxslF30C'
        )

        # Construct a Watson STT client with the authentication object
        stt = SpeechToTextV1(
            authenticator=stt_authenticator
        )

        # Set the URL endpoint for your Watson STT client
        stt.set_service_url(
            'https://api.us-south.speech-to-text.watson.cloud.ibm.com'
        )

        # Read audio file and call Watson STT API:
        with open(
            os.path.join(
                os.path.dirname(__file__), './.',
                'audio_sample.flac'
            ), 'rb'
        ) as audio_file:
            # Transcribe the audio.flac with Watson STT
            # Recognize method API reference: 
            # https://cloud.ibm.com/apidocs/speech-to-text?code=python#recognize
            stt_result = stt.recognize(
                audio=audio_file,
                content_type='audio/flac',
                model='pt-BR_BroadbandModel'
            ).get_result()

        # Print STT API call results
        print(json.dumps(stt_result, indent=2))
        texto_audio = stt_result['results'][0]['alternatives'][0]['transcript']

    # pega o texto da mensagem
    texto_forms = 'Sem texto'
    if('text' in multipart_data):
        texto_forms = multipart_data.get('text')[0]


    # Return a dictionary with the transcribed text
    return {
        "car": carro,
        "transcript": texto_audio,
        "texto": texto_forms
    }
