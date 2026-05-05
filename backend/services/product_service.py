"""Service logic for Walmart product identifier extraction."""

import re


WALMART_ID = re.compile(r"/ip/[^/]+/(\d+)")


class ProductService:
    """Provides product-related application logic."""

    def extract_product_id(self, url: str) -> str:
        """Extract the numeric Walmart product ID from a product URL."""

        match = WALMART_ID.search(url or "")
        if not match:
            raise ValueError("Could not extract product ID")
        return match.group(1)
