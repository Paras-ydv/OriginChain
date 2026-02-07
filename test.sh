#!/bin/bash

echo "🧪 Testing OriginChain Pipeline..."

# Test backend
echo "1. Testing backend API..."
cd backend
python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath('.'))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath('.'))), 'graphs'))

import importlib.util
spec = importlib.util.spec_from_file_location(
    'buildingrelations',
    '../graphs/buildingrelations.py'
)
buildingrelations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(buildingrelations)

# Test relationship generation
test_data = {
    'events': [
        {'title': 'Event 1', 'timestamp': '2024-01-01T00:00:00Z', 'source': 'Source1', 'event_type': 'initial_claim'},
        {'title': 'Event 2', 'timestamp': '2024-01-02T00:00:00Z', 'source': 'Source2', 'event_type': 'amplification'}
    ],
    'root_origin': {'title': 'Root', 'source': 'RootSource'}
}

result = buildingrelations.generate_relationships(test_data)
print(f'✅ Generated {len(result[\"relationships\"])} relationships')
" && echo "✅ Backend OK" || echo "❌ Backend failed"

cd ..

echo ""
echo "2. Start services:"
echo "   Terminal 1: cd backend && python3 api.py"
echo "   Terminal 2: cd frontend && npm run dev"
echo ""
echo "3. Visit: http://localhost:3000"
