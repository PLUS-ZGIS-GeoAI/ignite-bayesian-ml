# create feature layers
python -m scripts.create_farmyard_density_layer
Write-Host "create_farmyard_density_layer completed"

python -m scripts.create_topographical_layers
Write-Host "create_topographical_layers completed"

python -m scripts.create_population_layers
Write-Host "create_population_layers completed"

python -m scripts.create_forest_type_layer
Write-Host "create_forest_type_layer completed"

python -m scripts.create_road_density_layer
Write-Host "create_road_density_layer completed"

# test if all feature layers have same specifications as reference layer
python -m tests.test_feature_layer_specifications
Write-Host "test_feature_layer_specifications completed"
