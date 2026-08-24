$ErrorActionPreference = 'Stop'

$workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$outputDir = Join-Path $workspace 'output'
$outputFile = Join-Path $outputDir 'Plan_Maestro_Clinica_Reina_del_Cisne.mpp'
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

$projectApp = $null
try {
    try {
        $projectApp = New-Object -ComObject MSProject.Application
    }
    catch {
        $winproj = 'C:\Program Files\Microsoft Office\root\Office16\WINPROJ.EXE'
        if (-not (Test-Path -LiteralPath $winproj)) { throw }
        Start-Process -FilePath $winproj -WindowStyle Hidden
        Start-Sleep -Seconds 5
        $projectApp = New-Object -ComObject MSProject.Application
    }
    $projectApp.Visible = $false
    $projectApp.DisplayAlerts = $false
    $projectApp.FileNew()
    $project = $projectApp.ActiveProject
    $project.Title = 'Plan Maestro - Clínica Reina del Cisne'
    $project.Subject = 'Desarrollo, validación, despliegue y mantenimiento del sistema clínico'
    $project.Author = 'Clínica Reina del Cisne'
    $project.Company = 'Clínica Reina del Cisne'
    $project.Comments = 'Cronograma maestro generado a partir de la estructura y funcionalidades verificadas del proyecto Django.'
    $project.ProjectStart = [datetime]'2026-07-01 08:00:00'

    $resources = @{}
    foreach ($resourceName in @(
        'Jefe de proyecto',
        'Desarrollador Full Stack',
        'Diseñador UI/UX',
        'Administrador de clínica',
        'Recepcionista',
        'Médico validador',
        'QA / Pruebas',
        'DevOps / Infraestructura'
    )) {
        $resource = $project.Resources.Add($resourceName)
        $resources[$resourceName] = $resource
    }

    $taskIds = @{}
    function Add-PlanTask {
        param(
            [string]$Code,
            [string]$Name,
            [string]$Duration,
            [string[]]$Owners,
            [int]$Percent = 0,
            [string[]]$PredecessorCodes = @(),
            [bool]$IsChild = $true,
            [string]$Notes = ''
        )
        $task = $project.Tasks.Add($Name)
        $task.Manual = $false
        $task.Duration = $Duration
        if ($PredecessorCodes.Count -gt 0) {
            $predIds = foreach ($predCode in $PredecessorCodes) { $taskIds[$predCode] }
            $task.Predecessors = ($predIds -join ',')
        }
        if ($Percent -gt 0) { $task.PercentComplete = $Percent }
        if ($Notes) { $task.Notes = $Notes }
        $taskIds[$Code] = $task.ID
        if ($IsChild) {
            $projectApp.SelectRow($task.ID, $false)
            $projectApp.OutlineIndent()
        }
        foreach ($owner in $Owners) {
            if ($resources.ContainsKey($owner)) {
                [void]$task.Assignments.Add($task.ID, $resources[$owner].ID)
            }
        }
        return $task
    }

    function Add-Phase {
        param([string]$Code, [string]$Name)
        $task = $project.Tasks.Add($Name)
        $task.Manual = $false
        $taskIds[$Code] = $task.ID
        return $task
    }

    Add-Phase 'P1' '1. Inicio y definición del proyecto' | Out-Null
    Add-PlanTask '1.1' 'Definir objetivos, alcance y usuarios del sistema' '2d' @('Jefe de proyecto','Administrador de clínica') 100 @() $true 'Incluye paciente, médico, recepcionista y administrador.' | Out-Null
    Add-PlanTask '1.2' 'Levantar reglas de citas, pagos e historial clínico' '3d' @('Jefe de proyecto','Administrador de clínica','Médico validador') 100 @('1.1') | Out-Null
    Add-PlanTask '1.3' 'Priorizar módulos y criterios de aceptación' '2d' @('Jefe de proyecto','QA / Pruebas') 100 @('1.2') | Out-Null
    Add-PlanTask '1.4' 'Hito: alcance aprobado' '0d' @('Jefe de proyecto') 100 @('1.3') | Out-Null

    Add-Phase 'P2' '2. Arquitectura y configuración técnica' | Out-Null
    Add-PlanTask '2.1' 'Crear proyecto Django y estructura modular' '2d' @('Desarrollador Full Stack') 100 @('1.4') | Out-Null
    Add-PlanTask '2.2' 'Configurar aplicaciones, rutas y plantillas' '3d' @('Desarrollador Full Stack') 100 @('2.1') | Out-Null
    Add-PlanTask '2.3' 'Configurar base de datos y migraciones' '3d' @('Desarrollador Full Stack') 100 @('2.1') | Out-Null
    Add-PlanTask '2.4' 'Configurar variables de entorno y seguridad base' '2d' @('Desarrollador Full Stack','DevOps / Infraestructura') 100 @('2.2','2.3') | Out-Null
    Add-PlanTask '2.5' 'Preparar despliegue y dependencias' '2d' @('DevOps / Infraestructura') 90 @('2.4') | Out-Null
    Add-PlanTask '2.6' 'Hito: arquitectura funcional' '0d' @('Jefe de proyecto') 100 @('2.5') | Out-Null

    Add-Phase 'P3' '3. Identidad, usuarios y permisos' | Out-Null
    Add-PlanTask '3.1' 'Implementar registro de pacientes' '3d' @('Desarrollador Full Stack') 100 @('2.6') | Out-Null
    Add-PlanTask '3.2' 'Implementar ingreso con correo y contraseña' '2d' @('Desarrollador Full Stack') 100 @('3.1') | Out-Null
    Add-PlanTask '3.3' 'Integrar ingreso con Google' '3d' @('Desarrollador Full Stack') 100 @('3.2') | Out-Null
    Add-PlanTask '3.4' 'Implementar recuperación segura de contraseña' '3d' @('Desarrollador Full Stack') 100 @('3.2') | Out-Null
    Add-PlanTask '3.5' 'Crear roles y restricciones de acceso' '4d' @('Desarrollador Full Stack','QA / Pruebas') 100 @('3.1') | Out-Null
    Add-PlanTask '3.6' 'Crear gestión administrativa de usuarios' '4d' @('Desarrollador Full Stack','Administrador de clínica') 100 @('3.5') | Out-Null
    Add-PlanTask '3.7' 'Hito: identidad y permisos aprobados' '0d' @('Jefe de proyecto') 100 @('3.3','3.4','3.6') | Out-Null

    Add-Phase 'P4' '4. Sitio público e identidad visual' | Out-Null
    Add-PlanTask '4.1' 'Diseñar sistema visual, paleta y componentes' '4d' @('Diseñador UI/UX','Desarrollador Full Stack') 100 @('2.6') | Out-Null
    Add-PlanTask '4.2' 'Construir navegación y pie de página responsivos' '3d' @('Diseñador UI/UX','Desarrollador Full Stack') 100 @('4.1') | Out-Null
    Add-PlanTask '4.3' 'Construir página de inicio' '3d' @('Diseñador UI/UX','Desarrollador Full Stack') 100 @('4.2') | Out-Null
    Add-PlanTask '4.4' 'Construir Nosotros con imagen institucional' '2d' @('Diseñador UI/UX','Desarrollador Full Stack') 100 @('4.2') | Out-Null
    Add-PlanTask '4.5' 'Construir Especialidades y Servicios' '3d' @('Desarrollador Full Stack') 100 @('4.2') | Out-Null
    Add-PlanTask '4.6' 'Construir directorio de médicos con fotos y datos' '4d' @('Desarrollador Full Stack','Administrador de clínica') 100 @('4.2') | Out-Null
    Add-PlanTask '4.7' 'Construir página de contacto y aviso de emergencias' '3d' @('Desarrollador Full Stack','Administrador de clínica') 100 @('4.2') | Out-Null
    Add-PlanTask '4.8' 'Optimizar responsividad, sombras y microinteracciones' '4d' @('Diseñador UI/UX','Desarrollador Full Stack') 100 @('4.3','4.4','4.5','4.6','4.7') | Out-Null
    Add-PlanTask '4.9' 'Hito: sitio público aprobado' '0d' @('Jefe de proyecto') 100 @('4.8') | Out-Null

    Add-Phase 'P5' '5. Médicos y especialidades' | Out-Null
    Add-PlanTask '5.1' 'Modelar especialidades médicas' '2d' @('Desarrollador Full Stack') 100 @('2.6') | Out-Null
    Add-PlanTask '5.2' 'Crear altas, edición, activación e imágenes de especialidades' '4d' @('Desarrollador Full Stack','Administrador de clínica') 100 @('5.1') | Out-Null
    Add-PlanTask '5.3' 'Modelar médicos y datos profesionales' '3d' @('Desarrollador Full Stack') 100 @('5.1') | Out-Null
    Add-PlanTask '5.4' 'Crear y editar médicos desde administración' '4d' @('Desarrollador Full Stack','Administrador de clínica') 100 @('5.3') | Out-Null
    Add-PlanTask '5.5' 'Gestionar carga y visualización de fotografías' '3d' @('Desarrollador Full Stack','QA / Pruebas') 100 @('5.4') | Out-Null
    Add-PlanTask '5.6' 'Hito: catálogo médico operativo' '0d' @('Jefe de proyecto') 100 @('5.2','5.5') | Out-Null

    Add-Phase 'P6' '6. Citas, recepción y pagos' | Out-Null
    Add-PlanTask '6.1' 'Modelar citas, estados y disponibilidad' '4d' @('Desarrollador Full Stack') 100 @('3.7','5.6') | Out-Null
    Add-PlanTask '6.2' 'Crear formulario de agendamiento del paciente' '4d' @('Desarrollador Full Stack','Diseñador UI/UX') 100 @('6.1') | Out-Null
    Add-PlanTask '6.3' 'Agregar términos y condiciones obligatorios' '3d' @('Desarrollador Full Stack','Administrador de clínica') 100 @('6.2') | Out-Null
    Add-PlanTask '6.4' 'Configurar bancos, transferencias y códigos QR' '4d' @('Desarrollador Full Stack','Administrador de clínica') 100 @('6.1') | Out-Null
    Add-PlanTask '6.5' 'Implementar subida y revisión de comprobantes' '4d' @('Desarrollador Full Stack','Recepcionista') 100 @('6.4') | Out-Null
    Add-PlanTask '6.6' 'Construir panel concreto de recepción' '4d' @('Diseñador UI/UX','Desarrollador Full Stack','Recepcionista') 100 @('6.1') | Out-Null
    Add-PlanTask '6.7' 'Agregar confirmar, cancelar y reagendar citas' '4d' @('Desarrollador Full Stack','Recepcionista') 100 @('6.6') | Out-Null
    Add-PlanTask '6.8' 'Implementar avisos y recordatorios por correo' '3d' @('Desarrollador Full Stack') 100 @('6.7') | Out-Null
    Add-PlanTask '6.9' 'Hito: ciclo de citas y pagos operativo' '0d' @('Jefe de proyecto') 100 @('6.3','6.5','6.7','6.8') | Out-Null

    Add-Phase 'P7' '7. Atención clínica, historiales y recetas' | Out-Null
    Add-PlanTask '7.1' 'Crear atención médica y borradores' '4d' @('Desarrollador Full Stack','Médico validador') 100 @('6.9') | Out-Null
    Add-PlanTask '7.2' 'Crear historial clínico por paciente' '4d' @('Desarrollador Full Stack','Médico validador') 100 @('7.1') | Out-Null
    Add-PlanTask '7.3' 'Agregar radiografías y archivos al historial' '4d' @('Desarrollador Full Stack','Médico validador') 100 @('7.2') | Out-Null
    Add-PlanTask '7.4' 'Aplicar permisos de lectura y eliminación de archivos' '3d' @('Desarrollador Full Stack','QA / Pruebas') 100 @('7.3') | Out-Null
    Add-PlanTask '7.5' 'Crear emisión y descarga de recetas PDF' '4d' @('Desarrollador Full Stack','Médico validador') 100 @('7.2') | Out-Null
    Add-PlanTask '7.6' 'Agregar verificación pública de recetas' '2d' @('Desarrollador Full Stack') 100 @('7.5') | Out-Null
    Add-PlanTask '7.7' 'Hito: flujo clínico operativo' '0d' @('Jefe de proyecto') 100 @('7.4','7.6') | Out-Null

    Add-Phase 'P8' '8. Paneles, configuración y reportes' | Out-Null
    Add-PlanTask '8.1' 'Construir panel de paciente' '3d' @('Desarrollador Full Stack','Diseñador UI/UX') 100 @('3.7') | Out-Null
    Add-PlanTask '8.2' 'Construir panel de médico' '3d' @('Desarrollador Full Stack','Diseñador UI/UX') 100 @('7.7') | Out-Null
    Add-PlanTask '8.3' 'Construir panel administrativo' '4d' @('Desarrollador Full Stack','Administrador de clínica') 100 @('3.7') | Out-Null
    Add-PlanTask '8.4' 'Habilitar configuración de emergencias y contacto' '3d' @('Desarrollador Full Stack','Administrador de clínica') 100 @('8.3') | Out-Null
    Add-PlanTask '8.5' 'Crear dashboard y reportes con datos reales' '5d' @('Desarrollador Full Stack','Administrador de clínica','Recepcionista') 100 @('6.9','8.3') | Out-Null
    Add-PlanTask '8.6' 'Mejorar tablas, indicadores y detalle del período' '3d' @('Diseñador UI/UX','Desarrollador Full Stack') 100 @('8.5') | Out-Null
    Add-PlanTask '8.7' 'Hito: paneles y reportes aprobados' '0d' @('Jefe de proyecto') 100 @('8.1','8.2','8.4','8.6') | Out-Null

    Add-Phase 'P9' '9. Calidad, documentación y estabilización' | Out-Null
    Add-PlanTask '9.1' 'Crear pruebas de usuarios y permisos' '3d' @('QA / Pruebas','Desarrollador Full Stack') 100 @('3.7') | Out-Null
    Add-PlanTask '9.2' 'Crear pruebas de citas, pagos y recepción' '4d' @('QA / Pruebas','Desarrollador Full Stack') 100 @('6.9') | Out-Null
    Add-PlanTask '9.3' 'Crear pruebas de historial y recetas' '3d' @('QA / Pruebas','Desarrollador Full Stack') 100 @('7.7') | Out-Null
    Add-PlanTask '9.4' 'Crear pruebas de configuración y reportes' '2d' @('QA / Pruebas','Desarrollador Full Stack') 100 @('8.7') | Out-Null
    Add-PlanTask '9.5' 'Ejecutar suite completa de 63 pruebas' '1d' @('QA / Pruebas') 100 @('9.1','9.2','9.3','9.4') 'true' 'Resultado verificado: 63 pruebas aprobadas.' | Out-Null
    Add-PlanTask '9.6' 'Limpiar cachés y revisar archivos sin uso' '1d' @('Desarrollador Full Stack') 100 @('9.5') | Out-Null
    Add-PlanTask '9.7' 'Elaborar informes funcional y técnico' '3d' @('Jefe de proyecto','Desarrollador Full Stack') 100 @('9.5') | Out-Null
    Add-PlanTask '9.8' 'Hito: versión funcional estabilizada' '0d' @('Jefe de proyecto') 100 @('9.6','9.7') | Out-Null

    Add-Phase 'P10' '10. Preparación para producción' | Out-Null
    Add-PlanTask '10.1' 'Definir límites y política de archivos clínicos' '2d' @('Administrador de clínica','Médico validador','DevOps / Infraestructura') 0 @('9.8') | Out-Null
    Add-PlanTask '10.2' 'Configurar almacenamiento privado y respaldos' '4d' @('DevOps / Infraestructura') 0 @('10.1') | Out-Null
    Add-PlanTask '10.3' 'Revisar HTTPS, cookies, secretos y cabeceras' '3d' @('DevOps / Infraestructura','Desarrollador Full Stack') 0 @('9.8') | Out-Null
    Add-PlanTask '10.4' 'Configurar dominio, correo y autenticación Google' '3d' @('DevOps / Infraestructura') 0 @('10.3') | Out-Null
    Add-PlanTask '10.5' 'Migrar y validar base de datos de producción' '3d' @('DevOps / Infraestructura','Desarrollador Full Stack') 0 @('10.2','10.4') | Out-Null
    Add-PlanTask '10.6' 'Pruebas de aceptación con cada rol' '4d' @('QA / Pruebas','Administrador de clínica','Recepcionista','Médico validador') 0 @('10.5') | Out-Null
    Add-PlanTask '10.7' 'Corregir hallazgos de aceptación' '4d' @('Desarrollador Full Stack','Diseñador UI/UX') 0 @('10.6') | Out-Null
    Add-PlanTask '10.8' 'Capacitar administrador, recepción y médicos' '2d' @('Jefe de proyecto','Administrador de clínica') 0 @('10.7') | Out-Null
    Add-PlanTask '10.9' 'Hito: autorización de salida a producción' '0d' @('Jefe de proyecto','Administrador de clínica') 0 @('10.8') | Out-Null

    Add-Phase 'P11' '11. Lanzamiento y operación continua' | Out-Null
    Add-PlanTask '11.1' 'Publicar versión de producción' '1d' @('DevOps / Infraestructura','Desarrollador Full Stack') 0 @('10.9') | Out-Null
    Add-PlanTask '11.2' 'Verificar flujos críticos después del despliegue' '1d' @('QA / Pruebas','Recepcionista','Médico validador') 0 @('11.1') | Out-Null
    Add-PlanTask '11.3' 'Monitorear errores, correo, pagos y almacenamiento' '10d' @('DevOps / Infraestructura','Desarrollador Full Stack') 0 @('11.2') | Out-Null
    Add-PlanTask '11.4' 'Revisar copias de seguridad y recuperación' '2d' @('DevOps / Infraestructura') 0 @('11.3') | Out-Null
    Add-PlanTask '11.5' 'Planificar mejoras de API, auditoría y horarios' '3d' @('Jefe de proyecto','Desarrollador Full Stack','Administrador de clínica') 0 @('11.3') | Out-Null
    Add-PlanTask '11.6' 'Hito: cierre de lanzamiento' '0d' @('Jefe de proyecto') 0 @('11.4','11.5') | Out-Null

    $projectApp.FileSaveAs($outputFile)
    $projectApp.FileCloseAll(0)
    Write-Output $outputFile
}
finally {
    if ($projectApp -ne $null) {
        try { $projectApp.Quit() } catch {}
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($projectApp)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
