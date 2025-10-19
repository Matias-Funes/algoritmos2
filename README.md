# 🚀 Comandos Git Bash para trabajar en el proyecto de Algoritmos 2

# 1. Entrar a la carpeta del proyecto (si ya está clonado)
cd /c/Users/Matias-Funes/ProyectoAlgoritmos2

# 2. Clonar el repositorio (solo la primera vez)
git clone https://github.com/Matias-Funes/algoritmos2.git
cd algoritmos2

# 3. Ver en qué rama estás
git branch

# 4. Crear una nueva rama para trabajar
git checkout -b tu-nombre-descripcion
# Ejemplo:
# git checkout -b juan-funcion-movimiento
# 4. Entrar a tu rama (si ya existe y querés trabajar en ella)
git checkout tu-nombre-descripcion
# Ejemplo:
# git checkout juan-funcion-movimiento


# 5. Activar el entorno virtual (si aún no existe)
python -m venv .venv
source .venv/Scripts/activate

# 6. Instalar las dependencias necesarias
pip install -r requirements.txt

# 7. Verificar los cambios realizados
git status

# 8. Agregar los cambios al área de preparación
git add .

# 9. Guardar los cambios con un mensaje descriptivo
git commit -m "Descripción corta de lo que hiciste"

# 10. Subir los cambios a tu rama en GitHub
git push origin tu-nombre-descripcion
# Ejemplo:
# git push origin juan-funcion-movimiento

# 11. Actualizar tu rama con los cambios del grupo (antes de subir algo nuevo)
git pull origin main

# 12. Cambiar de rama (si necesitás ir a otra)
git checkout nombre-de-rama

# 13. Ver todas las ramas disponibles
git branch -a

# 14. Borrar una rama local que ya no uses
git branch -d nombre-de-rama

# 15. Borrar una rama remota (si ya fue mergeada)
git push origin --delete nombre-de-rama
