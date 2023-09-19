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

    texto_audio = ''

    if 'audio' in multipart_data:
        # Build flac file from stream of bytes
        fo = open("audio_sample.flac", 'wb')
        fo.write(multipart_data.get('audio')[0])
        fo.close()

    

        # Basic Authentication with Watson STT API
        stt_authenticator = BasicAuthenticator(
            'apikey',
            'xxx'
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
        #print(json.dumps(stt_result, indent=2))
        texto_audio = stt_result['results'][0]['alternatives'][0]['transcript']

    # pega o texto da mensagem
    texto_forms = ''
    if('text' in multipart_data):
        texto_forms = multipart_data.get('text')[0]

    texto = texto_audio + texto_forms

    # prepara resposta padrao
    resposta = {
        'recommendation': '',
        'entities': [],
        #'texto_forms': texto_forms,
        #'texto_audio': texto_audio,
        #'texto_concat': texto,
        #'car': carro
    }

    if(len(texto) > 12):
        # Basic Authentication with Watson NLU API
        nlu_authenticator = BasicAuthenticator(
            'apikey',
            'xxxx'
        )

        # Construct a Watson NLU client with the authentication object
        nlu = NaturalLanguageUnderstandingV1(
            version='2020-08-01',
            authenticator=nlu_authenticator
        )

        # Set the URL endpoint for your Watson STT client
        nlu.set_service_url(
            'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com'
        )

        # call Watson API
        nlu_result = nlu.analyze(
                text=texto,
                features=Features(entities=EntitiesOptions(sentiment=True,limit=5, model='fb03b324-e9d9-4e85-b705-ac6ef603c22a'))
            ).get_result()


        # Print NLU API call results
        #print(json.dumps(nlu_result, indent=2))

        entidades = nlu_result['entities']

        # primeiro criar um rank das entidades, e a parte entitys da resposta
        rank_entidades = dict()
        result_entidades = []
        modelo = ''

        for entidade in entidades:
            ent = entidade['type']
            sent = entidade['sentiment']['score']
            mention = entidade['text']
            if (ent != 'MODELO'):
                if ent in rank_entidades:
                    if sent < rank_entidades[ent]:
                        rank_entidades[ent] = sent
                else:
                    rank_entidades[ent] = sent
            else:
                modelo = mention
                    
            result_entidades.append({'entity': ent, 
                                    'sentiment': sent, 
                                   'mention': mention})

        # Definicao de prioridade das reclamacoes e lista de carros a sugerir 
        # (coloquei tres na sugestao pois entendi que tinha que evita o modelo em 'car' e talvez um modelo no texto
        prioridades = {
            'SEGURANCA': 1,
            'CONSUMO': 2,
            'DESEMPENHO': 3,
            'MANUTENCAO': 4,
            'CONFORTO': 5,
            'DESIGN': 6,
            'ACESSORIOS': 7
            }

        sugestoes = {
            'SEGURANCA': ['FIAT 500','DUCATO', 'RENEGADE'],
            'CONSUMO': ['ARGO', 'TORO', 'DUCATO'],
            'DESEMPENHO': ['ARGO', 'CRONOS', 'MAREA'],
            'MANUTENCAO': ['FIORINO', 'CRONOS', 'ARGO'],
            'CONFORTO': ['ARGO', 'CRONOS', 'TORO'],
            'DESIGN': ['FIAT 500', 'ARGO', 'RENEGADE'],
            'ACESSORIOS': ['RENEGADE', 'ARGO', 'TORO']    
            }


        # acha a menor nota
        menor = rank_entidades[min(rank_entidades, key=rank_entidades.get)]
        if menor < 0:
            # separa os que tem nota até 0.1 próxima com as prioridades
            most_negatives = {k: prioridades[k] for k, v in rank_entidades.items() if abs(v - menor) < 0.1}

            # pega lista de recomendacoes do que tem a menor prioridade
            recomendado = sugestoes[min(most_negatives, key = most_negatives.get)]
            if(recomendado[0] not in [carro, modelo]):
                resposta['recommendation'] = recomendado[0]
            elif(recomendado[1] not in [carro, modelo]):
                resposta['recommendation'] = recomendado[1]
            else:
                resposta['recommendation'] = recomendado[2]

        #resposta['menor'] = menor
        resposta['entities'] = result_entidades


    # Return a dictionary with the transcribed text
    return(resposta)
