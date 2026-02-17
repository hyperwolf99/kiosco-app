# Kiosco Manager

Sistema de gestión de ventas para kioscos 24 horas. Aplicación de escritorio offline, simple y eficiente.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## 🎯 Características Principales

- ✅ **100% Offline** - Funciona sin internet
- ✅ **Sin login** - Abierta y lista para usar
- ✅ **4 formas de pago** - Efectivo 💵, Transferencia 📱, Débito 💳, Crédito 💎
- ✅ **Control de fiados** - Sistema completo con pagos parciales
- ✅ **Reportes automáticos** - Diarios, mensuales y anuales
- ✅ **Exportación de datos** - Backup en JSON
- ✅ **Interfaz intuitiva** - Diseñada para adultos mayores

## 📸 Screenshots

*(Próximamente)*

## 🚀 Instalación Rápida

### Opción 1: Descargar Ejecutable (Recomendado)

1. Ve a la sección [Releases](../../releases/latest)
2. Descarga `KioscoManager.exe`
3. Ejecuta el archivo en tu PC
4. ¡Listo! La base de datos se creará automáticamente

### Opción 2: Ejecutar con Python

```bash
# Clonar repositorio
git clone https://github.com/hyperwolf99/kiosco-app.git
cd kiosco-manager

# Requisitos: Python 3.8 o superior
python main.py
```

## 📖 Guía Rápida

### Registrar una Venta
1. Escribe el monto
2. Selecciona la forma de pago
3. Presiona **Enter** o clic en "Guardar"

### Registrar un Fiado
1. Ve a la pestaña "Fiados"
2. Selecciona o crea un cliente
3. Ingresa el monto
4. Guarda

### Ver Reportes
- **F2** - Reportes del día
- **F3** - Reportes mensuales
- **F5** - Actualizar datos

## 🛠️ Tecnologías

- **Python 3.8+** - Lenguaje principal
- **Tkinter** - Interfaz gráfica
- **SQLite** - Base de datos local
- **PyInstaller** - Compilación a ejecutable

## 📁 Estructura del Proyecto

```
kiosco-manager/
├── 📄 main.py              # Aplicación principal
├── 🗄️ database.py          # Capa de base de datos
├── 🧪 test_completo.py     # Tests automatizados
├── 📋 requirements.txt     # Dependencias
├── 📖 README.md           # Este archivo
├── 📄 LICENSE             # Licencia MIT
└── 📂 dist/               # Ejecutables compilados
```

## 💾 Base de Datos

Los datos se guardan localmente:
- **Windows**: `%LOCALAPPDATA%\KioscoManager\kiosco.db`
- **Linux/Mac**: `~/.kiosco-manager/kiosco.db`

### Backup
Simplemente copia el archivo `kiosco.db` para hacer backup.

## 🧪 Testing

```bash
python test_completo.py
```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas:
1. Haz fork del proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios
4. Push y abre un Pull Request

## 📧 Contacto

- Issues: [GitHub Issues](../../issues)

---

⭐ **Si te gusta este proyecto, dale una estrella!**
