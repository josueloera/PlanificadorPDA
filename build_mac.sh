#!/bin/bash
echo "Preparando compilación para macOS..."

# Verificar si pip3 está instalado
if ! command -v pip3 &> /dev/null
then
    echo "pip3 no fue encontrado. Por favor, instala Python 3 desde python.org"
    exit
fi

# Instalar dependencias
echo "Instalando dependencias necesarias..."
pip3 install pyinstaller customtkinter fpdf openpyxl Pillow

# Compilar usando PyInstaller
echo "Compilando la aplicación (creando el archivo .app)..."
python3 -m PyInstaller --name PlanificadorPDA --windowed --noconsole \
    --add-data "$(python3 -c 'import customtkinter; import os; print(os.path.dirname(customtkinter.__file__))'):customtkinter/" \
    src/main.py

echo "=========================================="
echo "¡Compilación Exitosa!"
echo "Tu aplicación para Mac se encuentra en la carpeta 'dist/' bajo el nombre 'PlanificadorPDA.app'."
echo "Puedes arrastrar 'PlanificadorPDA.app' a tu carpeta de Aplicaciones."
echo "=========================================="
