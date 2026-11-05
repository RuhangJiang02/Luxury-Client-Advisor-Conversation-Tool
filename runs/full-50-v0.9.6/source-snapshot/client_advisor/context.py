import hashlib
import json

from .config import ROOT

CATALOGUE = json.loads((ROOT / "data/catalogue.json").read_text())
PRODUCTS = CATALOGUE["products"]
BRAND_RULES = (ROOT / "docs/brand-and-rules.md").read_text()
RULES_HASH = hashlib.sha256(BRAND_RULES.encode()).hexdigest()
CATALOGUE_HASH = hashlib.sha256(json.dumps(CATALOGUE, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def resolved_products(ids):
    return [PRODUCTS[p] for p in ids if p in PRODUCTS]
