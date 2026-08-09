import json
import boto3
import base64
import urllib.parse

polly = boto3.client('polly')

PIN_SECRETO = "EdgarCloud2026"

PAGINA_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo Cloud: Texto a Audio - EOGB</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background-color: #f4f7f6; color: #333; }
        .contenedor { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #232f3e; border-bottom: 2px solid #ff9900; padding-bottom: 10px; }
        textarea, input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { background-color: #ff9900; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; width: 100%; font-weight: bold; }
        button:hover { background-color: #e38800; }
        .audio-player { margin-top: 20px; width: 100%; }
        .error { color: red; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="contenedor">
        <h1>Servicio Text-to-Speech Cloud</h1>
        <p>Arquitectura Serverless con AWS Lambda y Amazon Polly. Demostración técnica.</p>
        
        <form method="POST">
            <label><strong>1. Ingresa tu texto (Max 500 caracteres):</strong></label>
            <textarea name="texto" rows="4" maxlength="500" required placeholder="Escribe algo aquí..."></textarea>
            
            <label><strong>2. PIN de Seguridad (Evita costos no deseados):</strong></label>
            <input type="password" name="pin" required placeholder="Ingresa el PIN proporcionado por Edgar">
            
            <button type="submit">Convertir a Audio con Inteligencia Artificial</button>
        </form>
    </div>
</body>
</html>
"""

def lambda_handler(event, context):
    try:

        if event['requestContext']['http']['method'] == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': PAGINA_HTML
            }
            

        elif event['requestContext']['http']['method'] == 'POST':

            cuerpo_base64 = event['body']
            

            if event.get('isBase64Encoded', False):
                cuerpo = base64.b64decode(cuerpo_base64).decode('utf-8')
            else:
                cuerpo = cuerpo_base64
                

            datos_formulario = urllib.parse.parse_qs(cuerpo)
            
            texto_ingresado = datos_formulario.get('texto', [''])[0]
            pin_ingresado = datos_formulario.get('pin', [''])[0]
            

            if pin_ingresado != PIN_SECRETO:
                html_error = PAGINA_HTML.replace('</form>', '<p class="error">❌ Acceso denegado: PIN incorrecto.</p></form>')
                return {
                    'statusCode': 403,
                    'headers': {'Content-Type': 'text/html'},
                    'body': html_error
                }
                
            respuesta_polly = polly.synthesize_speech(
                Text=texto_ingresado,
                OutputFormat='mp3',
                VoiceId='Lupe'
            )
            
            if "AudioStream" in respuesta_polly:
                audio_bytes = respuesta_polly['AudioStream'].read()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                html_exito = PAGINA_HTML.replace(
                    '</form>', 
                    f'</form><hr><p><strong>Resultado:</strong></p><audio class="audio-player" controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
                )
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'text/html'},
                    'body': html_exito
                }
                
    except Exception as e:
        print(f"Error: {str(e)}")
        html_error = PAGINA_HTML.replace('</form>', f'<p class="error">❌ Error del servidor: {str(e)}</p></form>')
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': html_error
        }