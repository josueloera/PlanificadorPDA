import json
import os
from typing import Dict, List, Tuple

# --- CONFIGURACIÓN GLOBAL INICIAL ---
HORAS_DEFAULT = ["08:00", "09:00", "10:00", "10:30", "11:00", "12:00", "13:00"]
DIAS_DEFAULT = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

class ClaseItem:
    def __init__(self, materia: str, docente: str, grupo_id: str, color_bg: str = "#3498db"):
        self.materia = materia
        self.docente = docente
        self.grupo_id = grupo_id
        self.color_bg = color_bg 

    def to_dict(self):
        return {
            "materia": self.materia,
            "docente": self.docente,
            "grupo_id": self.grupo_id,
            "color_bg": self.color_bg
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["materia"], data["docente"], data["grupo_id"], data.get("color_bg", "#3498db"))

    def __repr__(self):
        return f"{self.materia}\n({self.docente})"


class SchoolSystemModel:
    def __init__(self):
        self.nombre_escuela = "Escuela Sin Nombre"
        self.ciclo_escolar = "2024-2025"
        self.grupos = {}  # { nombre_grupo: [ {materia, docente, horas, fijos, modo}, ... ] }
        self.horarios = {} # { nombre_grupo: { "(dia_idx, hora_idx)": ClaseItem } }
        self.bloqueos_docentes = {} # { "(dia_idx, hora_idx, docente)": nombre_grupo }
        self.disponibilidad_docentes = {} # { docente: [dia1, dia2, ...] }
        self.horas_contrato_docentes = {} # { docente: horas_int }
        self.materias_docentes = {} # { docente: [materia1, materia2, ...] }
        self.dias = DIAS_DEFAULT.copy()
        self.horas = HORAS_DEFAULT.copy()
        self.indices_recreo = []

    def to_dict(self):
        # Convert dictionary keys (tuples) to strings for JSON serialization
        horarios_str = {}
        for grupo, schedule in self.horarios.items():
            horarios_str[grupo] = {f"{k[0]},{k[1]}": v.to_dict() for k, v in schedule.items()}
            
        bloqueos_str = {f"{k[0]},{k[1]},{k[2]}": v for k, v in self.bloqueos_docentes.items()}

        return {
            "nombre_escuela": self.nombre_escuela,
            "ciclo_escolar": self.ciclo_escolar,
            "grupos": self.grupos,
            "horarios": horarios_str,
            "bloqueos_docentes": bloqueos_str,
            "disponibilidad_docentes": self.disponibilidad_docentes,
            "horas_contrato_docentes": self.horas_contrato_docentes,
            "materias_docentes": self.materias_docentes,
            "dias": self.dias,
            "horas": self.horas,
            "indices_recreo": self.indices_recreo
        }

    def from_dict(self, data):
        self.nombre_escuela = data.get("nombre_escuela", "Escuela Sin Nombre")
        self.ciclo_escolar = data.get("ciclo_escolar", "2024-2025")
        self.grupos = data.get("grupos", {})
        self.disponibilidad_docentes = data.get("disponibilidad_docentes", {})
        self.horas_contrato_docentes = data.get("horas_contrato_docentes", {})
        self.materias_docentes = data.get("materias_docentes", {})
        self.dias = data.get("dias", DIAS_DEFAULT.copy())
        self.horas = data.get("horas", HORAS_DEFAULT.copy())
        self.indices_recreo = data.get("indices_recreo", [])
        
        # Restore tuples
        horarios_str = data.get("horarios", {})
        self.horarios = {}
        for grupo, schedule in horarios_str.items():
            self.horarios[grupo] = {}
            for k_str, v_dict in schedule.items():
                parts = k_str.split(",")
                self.horarios[grupo][(int(parts[0]), int(parts[1]))] = ClaseItem.from_dict(v_dict)
                
        bloqueos_str = data.get("bloqueos_docentes", {})
        self.bloqueos_docentes = {}
        for k_str, v in bloqueos_str.items():
            parts = k_str.split(",")
            self.bloqueos_docentes[(int(parts[0]), int(parts[1]), parts[2])] = v

    def save_to_file(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)

    def load_from_file(self, filepath: str):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.from_dict(data)
