# Test Suite

This folder contains the automated tests added for the project.

## What is covered

- Pure utility functions in `reports.views`
- CSV/XLSX export helpers in `reports.exporters`
- Math template filters in `reports.templatetags.math_filters`
- Payment visibility logic in `payments.views`
- Log tail helper in `reports.views`

## Current status

- 17 automated tests
- 5+ tests verify internal logic and helper algorithms

## Run

```bash
cd /Users/andrei_necsulea/Desktop/FoodDeliveryMS
source .venv/bin/activate
pytest -q "Software Development/tests"
```

For coverage:

```bash
pytest --cov=reports --cov=payments --cov-report=term-missing "Software Development/tests"
```
