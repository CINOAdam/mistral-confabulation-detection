#!/bin/bash
# Verify all scenarios are correctly structured

echo "=== SCENARIO VERIFICATION ==="
echo ""

# Check index
echo "1. Checking index.json..."
if python3 -m json.tool static/scenarios/index.json > /dev/null 2>&1; then
    echo "   ✓ index.json is valid JSON"
    TOTAL=$(cat static/scenarios/index.json | grep -c '"id"')
    echo "   ✓ Contains $TOTAL scenario entries"
else
    echo "   ✗ index.json is invalid"
fi
echo ""

# Check featured scenarios
echo "2. Featured Scenarios:"
for scenario in honest fabrication denial; do
    FILE="static/scenarios/${scenario}.json"
    if [ -f "$FILE" ]; then
        TITLE=$(python3 -c "import json; print(json.load(open('$FILE'))['title'])" 2>/dev/null)
        REGIME=$(python3 -c "import json; print(json.load(open('$FILE'))['expected_regime'])" 2>/dev/null)
        DISCOVERY=$(python3 -c "import json; print(json.load(open('$FILE'))['discovery'])" 2>/dev/null)
        echo "   ✓ $scenario.json - $REGIME - $DISCOVERY"
    else
        echo "   ✗ $scenario.json not found"
    fi
done
echo ""

# Check each category
echo "3. Category Breakdown:"

echo "   Strategic Deception:"
for file in static/scenarios/deception/*.json; do
    if [ -f "$file" ]; then
        ID=$(python3 -c "import json; print(json.load(open('$file'))['id'])" 2>/dev/null)
        echo "      ✓ $(basename $file) - $ID"
    fi
done

echo "   Goal Preservation:"
for file in static/scenarios/goal/*.json; do
    if [ -f "$file" ]; then
        ID=$(python3 -c "import json; print(json.load(open('$file'))['id'])" 2>/dev/null)
        echo "      ✓ $(basename $file) - $ID"
    fi
done

echo "   Bimodal Processing:"
for file in static/scenarios/bimodal/*.json; do
    if [ -f "$file" ]; then
        ID=$(python3 -c "import json; print(json.load(open('$file'))['id'])" 2>/dev/null)
        echo "      ✓ $(basename $file) - $ID"
    fi
done
echo ""

# Count by expected regime
echo "4. Expected Regime Distribution:"
HONEST_COUNT=$(grep -r '"expected_regime": "HONEST"' static/scenarios/ | wc -l)
DECEPTIVE_COUNT=$(grep -r '"expected_regime": "DECEPTIVE"' static/scenarios/ | wc -l)
echo "   HONEST: $HONEST_COUNT scenarios"
echo "   DECEPTIVE: $DECEPTIVE_COUNT scenarios"
echo ""

# Check TypeScript files
echo "5. Integration Files:"
if [ -f "src/lib/scenarios.ts" ]; then
    echo "   ✓ scenarios.ts loader utility"
fi
if [ -f "src/lib/components/ScenarioSelector.svelte" ]; then
    echo "   ✓ ScenarioSelector.svelte component"
fi
if [ -f "SCENARIOS.md" ]; then
    echo "   ✓ SCENARIOS.md documentation"
fi
echo ""

echo "=== VERIFICATION COMPLETE ==="
