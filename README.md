# Trabajo Grupo 01 - Agente Conversacional Chef Zero Waste

Proyecto adaptado al esquema de la practica `CA1_ConversationalAgent`.

## Ficheros principales

- `Chat.py`: bucle general del chat.
- `BoWChat.py`: vectorizacion Bag of Words.
- `BowChatChefZeroWaste.py`: categorias, normalizacion y entidades.
- `BowChatChefZeroWaste_E1_Agente.py`: agente que imprime instrucciones y retorna resultados.
- `BowChatChefZeroWaste_E2_STM.py`: memoria a corto plazo para operadores con parametros.
- `BowChatChefZeroWaste_E3_EmbeddingsImagen.py`: embedding de imagen colocado antes de la BoW.
- `ImageActionEmbedder.py`: calcula el embedding simple de la imagen.
- `main_chef_zero_waste.py`: punto de entrada.

## Operadores

- `instrucciones()` - aridad 0.
- `anadir_ingredientes(ingredientes...)` - aridad variable.
- `recomendar_receta(ingrediente, tiempo, raciones)` - aridad 3.
- `sustituir_ingrediente(ingrediente, restriccion)` - aridad 2.
- `ajustar_raciones(raciones)` - aridad 1.
- `lista_compra()` - aridad 0.

## Ejecucion

En PowerShell:

```powershell
cd "C:\Users\Control Lunar\Desktop\TRABAJO 1\Trabajo_Grupo_01_Agente_Conversacional_ChefZeroWaste"
python main_chef_zero_waste.py
```

Cuando pregunte:

```text
Es correcta? (Si por defecto / No):
```

pulsa `Enter`.

## Flujo completo de prueba

```text
instrucciones
tengo tomate y queso
tengo arroz imagenes_acciones/anadir_ingredientes.png
receta en 15 minutos para 2 raciones
sustituye queso sin lactosa
ajusta a 4 raciones
que tengo que comprar
receta imagenes_acciones/recomendar_receta.png
queso sin lactosa imagenes_acciones/sustituir_ingrediente.png
4 raciones imagenes_acciones/ajustar_raciones.png
imagen imagenes_acciones/lista_compra.png
salir
```

## Salidas esperadas clave

Imagen para `anadir_ingredientes`:

```text
Embedding imagen -> [0.0, 5.0, 0.0, 0.0, 0.0, 0.0]
Categoria detectada: anadir_ingredientes
```

Recomendacion usando memoria a corto plazo:

```text
STM usada: ingrediente anterior
```

Ajuste de raciones:

```text
Receta ajustada a 4 raciones.
Multiplicar cantidades por 2.00
```

Imagen para `recomendar_receta`:

```text
Embedding imagen -> [0.0, 0.0, 5.0, 0.0, 0.0, 0.0]
Categoria detectada: recomendar_receta
```

El vector completo siempre se construye asi:

```text
[embedding_imagen] + [descripcion_BoW]
```

Las imagenes ayudan a detectar la accion, no los parametros. Los parametros salen del texto de la frase y de la memoria a corto plazo.
