from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_homepage_contains_battery_capacity_before_battery_level_in_predefined_and_custom_sections():
    response = client.get("/")
    assert response.status_code == 200

    html = response.text

    predefined_capacity = '<strong>Battery Capacity:</strong>'
    predefined_level = '<strong>Battery Level:</strong>'
    custom_capacity = '<strong>Battery Capacity (kWh)</strong>'
    custom_level = '<strong>Battery Level (%)</strong>'

    assert predefined_capacity in html
    assert predefined_level in html
    assert custom_capacity in html
    assert custom_level in html

    assert html.index(predefined_capacity) < html.index(predefined_level)
    assert html.index(custom_capacity) < html.index(custom_level)


def test_homepage_contains_battery_value_targets():
    response = client.get("/")
    assert response.status_code == 200

    html = response.text

    assert 'id="val-battery-max"' in html
    assert 'id="val-battery-pct"' in html