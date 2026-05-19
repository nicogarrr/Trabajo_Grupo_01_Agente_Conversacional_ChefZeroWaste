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
- `crear_embedding_gesto.py`: genera un `.emb.vec` medio desde varias fotos del gesto.
- `gestos/*.emb.vec`: embeddings de gesto para probar entrada visual ya calculada.
- `main_chef_zero_waste.py`: punto de entrada.

## Operadores

- `instrucciones()` - aridad 0.
- `anadir_ingredientes(ingredientes...)` - aridad variable.
- `recomendar_receta(ingrediente, tiempo, raciones)` - aridad 3.
- `sustituir_ingrediente(ingrediente, restriccion)` - aridad 2.
- `ajustar_raciones(raciones)` - aridad 1.
- `lista_compra()` - aridad 0.
- `planificar_menu(dias)` - aridad 1.
- `calcular_caducidad(ingrediente, dias)` - aridad 2.
- `conservar_ingrediente(ingrediente)` - aridad 1.

<!-- DEFENSA: Explicacion preparada para entregar. -->
## Operador Alumno 1: conservar ingrediente

He creado la operacion `conservar_ingrediente(ingrediente)`, cuya finalidad es recomendar una forma de conservacion para un ingrediente concreto. Esta operacion ayuda al objetivo del agente Chef Zero Waste porque permite reducir desperdicio indicando como guardar mejor los alimentos.

El parametro principal es `ingrediente`. Por ejemplo, si el usuario escribe `como conservo el tomate`, el sistema detecta la operacion `conservar_ingrediente` y extrae `tomate` como entidad.

Reglas STM:

- Si el usuario no indica ingrediente, se usa el ultimo ingrediente principal guardado en `STMingredientePrincipal`.
- Si no hay ingrediente principal, se usa el primer ingrediente de la lista `STMingredientes`.
- Cuando se ejecuta la operacion, el ingrediente consultado se guarda como `STMingredientePrincipal`.

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

<!-- DEFENSA: El flujo incluye prompts de prueba para conservar_ingrediente. -->
```text
instrucciones
tengo tomate y queso
tengo arroz imagenes_acciones/anadir_ingredientes.png
receta en 15 minutos para 2 raciones
planifica menu para 3 dias
otro menu
queso 5 dias
lleva dias
sustituye queso sin lactosa
ajusta a 4 raciones
que tengo que comprar
como conservo el tomate
como lo conservo
gestos/planificar_menu.emb.vec
3 dias gestos/planificar_menu.emb.vec
5 dias gestos/calcular_caducidad.emb.vec
gestos/gesto_grupo.emb.vec
caducidad queso 5 dias gestos/gesto_grupo.emb.vec
receta imagenes_acciones/recomendar_receta.png
queso sin lactosa imagenes_acciones/sustituir_ingrediente.png
4 raciones imagenes_acciones/ajustar_raciones.png
imagen imagenes_acciones/lista_compra.png
salir
```

## Salidas esperadas clave

Imagen para `anadir_ingredientes`:

```text
Embedding imagen -> [0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
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
Embedding imagen -> [0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
Categoria detectada: recomendar_receta
```

El vector completo siempre se construye asi:

```text
[embedding_gesto] + [embedding_imagen] + [descripcion_BoW]
```

Las imagenes y los embeddings de gesto ayudan a detectar la accion, no los parametros. Los parametros salen del texto de la frase y de la memoria a corto plazo.

## Ejercicio Imagen

Para la rama `imagen`, el agente acepta tambien un embedding ya calculado de gesto con extension `.emb.vec`, `.embedding.vec` o `.gesto.vec`.

El fichero `gestos/gesto_grupo.emb.vec` se ha creado a partir de las fotos guardadas en `imagenes_acciones/gesto`:

```powershell
python crear_embedding_gesto.py imagenes_acciones/gesto gestos/gesto_grupo.emb.vec
```

Ejemplos:

```text
gestos/planificar_menu.emb.vec
3 dias gestos/planificar_menu.emb.vec
5 dias gestos/calcular_caducidad.emb.vec
gestos/gesto_grupo.emb.vec
caducidad queso 5 dias gestos/gesto_grupo.emb.vec
```

El gesto se concatena antes del embedding de imagen que ya existia. El embedding real `gestos/gesto_grupo.emb.vec` activa las dos operaciones nuevas `planificar_menu` y `calcular_caducidad`; si el texto esta vacio, el entrenamiento lo clasifica como `planificar_menu`, y si el texto menciona caducidad lo lleva a `calcular_caducidad`.
