import random
from src.models.data_models import SchoolSystemModel, ClaseItem

class ScheduleGenerator:
    def __init__(self, model: SchoolSystemModel):
        self.model = model

    def set_datos_escuela(self, nombre, ciclo):
        self.model.nombre_escuela = nombre
        self.model.ciclo_escolar = ciclo

    def set_configuracion_global(self, dias, horas, indices_recreo):
        self.model.dias = dias
        self.model.horas = horas
        self.model.indices_recreo = indices_recreo

    def registrar_grupo(self, nombre_grupo, lista_materias_config):
        # Validar horas máximas
        horas_pedidas = sum(int(cfg.get('horas', 0)) for cfg in lista_materias_config if cfg.get('modo') == 'auto')
        horas_fijas = sum(len(cfg.get('fijos', [])) for cfg in lista_materias_config if cfg.get('modo') == 'manual')
        total_horas_clase = len(self.model.dias) * (len(self.model.horas) - len(self.model.indices_recreo))
        
        if (horas_pedidas + horas_fijas) > total_horas_clase:
            return False, f"El grupo {nombre_grupo} requiere {horas_pedidas + horas_fijas} horas, pero solo hay {total_horas_clase} disponibles."
            
        self.model.grupos[nombre_grupo] = lista_materias_config
        self.model.horarios[nombre_grupo] = {}
        return True, "Grupo registrado"

    def generar_automaticamente(self):
        # Validar capacidad de maestros antes de iniciar
        horas_por_docente = {}
        for g, configs in self.model.grupos.items():
            for c in configs:
                doc = c['docente']
                hrs = int(c.get('horas', 0)) if c.get('modo') == 'auto' else len(c.get('fijos', []))
                horas_por_docente[doc] = horas_por_docente.get(doc, 0) + hrs

        for doc, hrs in horas_por_docente.items():
            if doc in self.model.disponibilidad_docentes:
                dias_trabajo = len(self.model.disponibilidad_docentes[doc])
                horas_dia = len(self.model.horas) - len(self.model.indices_recreo)
                max_hrs = dias_trabajo * horas_dia
                if hrs > max_hrs:
                    return False, f"El maestro {doc} tiene {hrs} horas asignadas, pero sus días laborales solo permiten {max_hrs} horas."

        self.model.bloqueos_docentes.clear()
        self.model.horarios = {g: {} for g in self.model.grupos}

        # FASE 1: FIJOS
        for nombre_grupo, lista_configs in self.model.grupos.items():
            for config in lista_configs:
                if config.get('modo') == 'manual' and config.get('fijos'): 
                    for (d_idx, h_idx) in config['fijos']:
                        if h_idx in self.model.indices_recreo: continue
                        clave = (d_idx, h_idx, config['docente'])
                        clase = ClaseItem(config['materia'], config['docente'], nombre_grupo, color_bg="#2980b9")
                        self.model.horarios[nombre_grupo][(d_idx, h_idx)] = clase
                        self.model.bloqueos_docentes[clave] = nombre_grupo

        # FASE 2: AUTOMÁTICOS
        for nombre_grupo, lista_configs in self.model.grupos.items():
            bolsa = []
            for config in lista_configs:
                if config.get('modo') == 'auto':
                    for _ in range(int(config['horas'])):
                        bolsa.append(ClaseItem(config['materia'], config['docente'], nombre_grupo))
            
            random.shuffle(bolsa)
            
            for clase in bolsa:
                colocado = False
                celdas = [(d, h) for d in range(len(self.model.dias)) for h in range(len(self.model.horas))]
                random.shuffle(celdas)
                
                for d, h in celdas:
                    if h in self.model.indices_recreo: continue
                    
                    # Respetar disponibilidad del maestro
                    dia_nombre = self.model.dias[d]
                    if clase.docente in self.model.disponibilidad_docentes:
                        if dia_nombre not in self.model.disponibilidad_docentes[clase.docente]:
                            continue
                            
                    if (d, h) not in self.model.horarios[nombre_grupo]:
                        if (d, h, clase.docente) not in self.model.bloqueos_docentes:
                            self.model.horarios[nombre_grupo][(d, h)] = clase
                            self.model.bloqueos_docentes[(d, h, clase.docente)] = nombre_grupo
                            colocado = True
                            break
                if not colocado:
                    print(f"Alerta: Sin espacio para {clase.materia} en {nombre_grupo}")

        return True, "Horarios generados."

    def mover_clase(self, grupo, origen, destino):
        if destino[1] in self.model.indices_recreo: return False, "¡Es hora de Recreo!"

        horario = self.model.horarios[grupo]
        if origen not in horario: return False, "Vacío"
        
        clase = horario[origen]
        
        # Validar disponibilidad de días
        dia_nombre = self.model.dias[destino[0]]
        if clase.docente in self.model.disponibilidad_docentes:
            if dia_nombre not in self.model.disponibilidad_docentes[clase.docente]:
                return False, f"El maestro {clase.docente} no labora los {dia_nombre}."

        c_orig = (origen[0], origen[1], clase.docente)
        c_dest = (destino[0], destino[1], clase.docente)
        
        if c_orig in self.model.bloqueos_docentes: 
            del self.model.bloqueos_docentes[c_orig]
        
        ocupante = horario.get(destino)
        
        if not ocupante and c_dest in self.model.bloqueos_docentes:
            self.model.bloqueos_docentes[c_orig] = grupo 
            return False, f"Docente ocupado en el grupo {self.model.bloqueos_docentes[c_dest]}"
            
        del horario[origen]
        horario[destino] = clase
        self.model.bloqueos_docentes[c_dest] = grupo
        
        if ocupante:
            horario[origen] = ocupante
            old_dest_lock = (destino[0], destino[1], ocupante.docente)
            new_orig_lock = (origen[0], origen[1], ocupante.docente)
            if old_dest_lock in self.model.bloqueos_docentes: del self.model.bloqueos_docentes[old_dest_lock]
            self.model.bloqueos_docentes[new_orig_lock] = grupo
            
        return True, "Ok"
