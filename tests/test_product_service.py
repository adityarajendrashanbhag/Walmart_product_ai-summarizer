import pytest

from backend.services.product_service import ProductService


def test_extract_product_id_from_valid_walmart_url():
    service = ProductService()
    url = (
        "https://www.walmart.com/ip/"
        "Apple-AirPods-Pro-2-Wireless-Earbuds/5689919121"
        "?classType=VARIANT&athbdg=L1102"
    )

    product_id = service.extract_product_id(url)

    assert product_id == "5689919121"


def test_extract_product_id_raises_for_invalid_url():
    service = ProductService()

    with pytest.raises(ValueError, match="Could not extract product ID"):
        service.extract_product_id("https://www.example.com/product/123")
