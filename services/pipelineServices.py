
"""
El pipeline es otra cosa completamente distinta.

NO ejecuta algoritmos. Coordina procesos.

Por ejemplo:

pipeline = ScreeningPipeline()
pipeline.run(study)

Internamente hace algo parecido a esto:

study
↓
AnalysisService.run("NormalClassifier")
↓
P(normal)=0.998
↓
Decision
↓
¿Enviar al radiólogo?
↓
Sí / No
↓
Si NO
↓
SamplingEngine
↓
¿Seleccionado para auditoría?
↓
Sí
↓
Enviar igualmente al radiólogo
↓
Guardar resultado


Pipeline NO conoce PyTorch, TensorFlow, ni Docker.

Sólo coordina pasos.

Cuando necesita ejecutar una IA, llama a AnalysisService.

## Un ejemplo real con tu proyecto

Supongamos que mañana quieres hacer el pipeline de screening.
El código podría ser literalmente:

'''
study = repository.load(uid)

probability = analysis.run(
    "NormalClassifier",
    study
)

if probability > 0.99:
    if sampler.select(study):
        send_to_radiologist(study)
    else:
        archive(study)
else:
    send_to_radiologist(study)
'''

¿Quién ha ejecutado la IA? AnalysisService.
¿Quién ha tomado la decisión? El pipeline.
"""