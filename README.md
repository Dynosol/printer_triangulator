# Printer Triangulator

A Python package for scanning and triangulating network printers.

## Installation

```bash
pip install git+https://github.com/yourusername/printer_triangulator.git
```

## Usage

As a command-line tool:
```bash
printer-triangulator --num-pings 3 --duration 60
```

As a Python package:
```python
from printer_triangulator import get_network_data

# Get network data
data = get_network_data()
print(data)
```

## Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
4. Install development dependencies: `pip install -e .`