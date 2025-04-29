#!/bin/bash

# Set current directory
CD_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$CD_DIR/aniTA_web"

echo "Starting Docker containers..."
docker-compose down
docker-compose up -d

# Wait for ArangoDB to be ready
echo "Waiting for ArangoDB to start..."
sleep 10

# Run migrations
echo "Running Django migrations..."
docker-compose exec web python manage.py migrate

# Generate network data
echo "Generating network data..."
docker-compose exec web python manage.py shell -c "from network_simulation.generate_data import generate_data, save_data_as_csv, save_data_as_json, save_user_credentials_csv; data = generate_data(); save_data_as_csv(data, 'csv_data'); save_data_as_json(data, 'network_data.json'); save_user_credentials_csv(data, 'csv_data')"

# Import to Django models
echo "Importing to Django models..."
docker-compose exec web python manage.py shell -c "from network_simulation.import_data import import_from_json; import_from_json('network_data.json')"

# Import to ArangoDB
echo "Importing to ArangoDB..."
docker-compose exec web python manage.py import_network_to_arango --json network_data.json --csv-dir csv_data

# Generate assignments with Claude API
echo "Generating assignments with Claude API..."
docker-compose exec web python manage.py generate_assignments --courses 2 --students 3 --delay 5

echo "Done! You can access the web interface at http://localhost:8000"
echo "To view the network simulation, go to http://localhost:8000/network/"
echo "To view source materials, go to http://localhost:8000/network/source-materials/"
echo "To shut down containers, run: cd $CD_DIR/aniTA_web && docker-compose down"