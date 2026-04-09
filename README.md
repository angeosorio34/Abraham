# Sistema de Gestión - Buffet de Abogados

## Cómo instalar este sistema en otra computadora (Windows)

Si deseas llevar este sistema a otra computadora (de un colega o una nueva laptop), sigue estos pasos cuidadosamente:

### Paso 1: Copiar los archivos (En tu PC actual)
Copia toda la carpeta del proyecto (la carpeta **ABRHAM**) en un pendrive, o envíala por correo (como un archivo `.zip`). 
> **Nota Importante:** Puedes excluir la carpeta oculta `.venv` al copiar, ya que los entornos de Python no suelen funcionar bien si se copian directamente de una PC a otra. Si quieres llevarte los datos que ya registraste, asegúrate de llevar contigo también el archivo `database.db`.

### Paso 2: Instalar Python (En la nueva PC)
1. Ve a la página oficial de Python: https://www.python.org/downloads/
2. Descarga la última versión para Windows.
3. Al ejecutar el instalador, **ES MUY IMPORTANTE** que marques la casilla que dice **"Add Python to PATH"** en la parte inferior de la ventana, antes de hacer clic en "Install Now".

### Paso 3: Preparar el Sistema (En la nueva PC)
1. Pega la carpeta **ABRHAM** (la que copiaste en el Paso 1) en el Escritorio o Documentos de la nueva computadora.
2. Abre la carpeta.
3. Haz clic derecho en el fondo de la ventana (donde no hay archivos), o asegúrate de no estar tocando ningún archivo y selecciona "Abrir en Terminal" (Open in Terminal).
4. En esa terminal, escribe los siguientes tres comandos uno a la vez esperando a que terminen:

```powershell
Sustituir el entorno virtual (Si no copiaste la carpeta .venv, crea una nueva):
python -m venv .venv

Activar el entorno:
.\.venv\Scripts\activate

Instalar las herramientas del sistema:
pip install -r requirements.txt
```

### Paso 4: ¡Correr el sistema!
Una vez que termine la instalación, simplemente levantas el programa escribiendo:
```powershell
python app.py
```
Y entras en el navegador web (Google Chrome, Edge, etc.) a `http://127.0.0.1:5000`.
