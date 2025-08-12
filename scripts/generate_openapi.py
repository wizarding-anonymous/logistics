import os
import json
import importlib.util
from pathlib import Path

def generate_openapi_specs():
    """
    Dynamically imports each service's FastAPI app and generates its
    OpenAPI JSON schema.
    """
    services_dir = Path("apps/backend/services")
    output_dir = Path("docs/api")
    output_dir.mkdir(exist_ok=True)

    # List of services to process
    service_names = [
        "auth", "orgs", "rfq", "orders",
        "payments", "catalog", "admin", "chat", "docs", "search"
    ]

    for service_name in service_names:
        try:
            print(f"Processing service: {service_name}...")

            # Dynamically import the 'app' from each service's 'main.py'
            module_name = f"apps.backend.services.{service_name}.main"
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                print(f"  Could not find module for {service_name}. Skipping.")
                continue

            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)

            app = getattr(main_module, 'app', None)
            if app is None:
                print(f"  'app' not found in main.py for {service_name}. Skipping.")
                continue

            # Generate the OpenAPI schema
            openapi_schema = app.openapi()

            # Write the schema to a file
            output_path = output_dir / f"{service_name}.openapi.json"
            with open(output_path, "w") as f:
                json.dump(openapi_schema, f, indent=2)

            print(f"  Successfully generated OpenAPI spec at {output_path}")

        except Exception as e:
            print(f"  Failed to process {service_name}: {e}")

if __name__ == "__main__":
    generate_openapi_specs()
