from pathlib import Path

import aspose.tasks as tasks

root = Path(__file__).resolve().parents[1]
source = root / "output" / "Plan_Maestro_Clinica_Reina_del_Cisne.xml"
target = root / "output" / "Plan_Maestro_Clinica_Reina_del_Cisne.mpp"

project = tasks.Project(str(source))
project.save(str(target), tasks.saving.SaveFileFormat.MPP)

if not target.exists() or target.stat().st_size < 1024:
    raise RuntimeError("No se generó un archivo MPP válido.")

print(f"{target}|bytes={target.stat().st_size}")
