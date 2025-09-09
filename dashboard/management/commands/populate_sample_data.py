from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.utils import timezone
from decimal import Decimal
import io

from products.models import Category, Brand, Product, ProductImage, Inventory
from dashboard.models import Banner

try:
	from PIL import Image
except Exception:
	Image = None


class Command(BaseCommand):
	help = "Populate sample data for Everest Beauty (categories, brands, products, banners)"

	def handle(self, *args, **options):
		self.stdout.write(self.style.MIGRATE_HEADING("Seeding sample data..."))

		# Categories
		categories = [
			("Skincare", "Gentle and effective skincare essentials"),
			("Makeup", "Modern, playful makeup for every look"),
			("Haircare", "Healthy hair from root to tip"),
			("Fragrance", "Soft, elegant scents"),
			("Tools & Brushes", "Tools for pro-level finishes"),
		]
		category_objs = []
		for name, desc in categories:
			obj, _ = Category.objects.get_or_create(
				name=name,
				defaults={
					"slug": slugify(name),
					"description": desc,
					"is_active": True,
				}
			)
			category_objs.append(obj)

		# Brands
		brands = [
			("Himalaya Glow", True),
			("Koshi Beauty", True),
			("Rare Bliss", False),
		]
		brand_objs = []
		for name, is_nepali in brands:
			obj, _ = Brand.objects.get_or_create(
				name=name,
				defaults={
					"slug": slugify(name),
					"description": f"{name} curated beauty.",
					"is_nepali_brand": is_nepali,
					"is_active": True,
				}
			)
			brand_objs.append(obj)

		# Helper to create a placeholder image file
		def generate_image_bytes(color=(230, 235, 255)):
			if Image is None:
				return None
			img = Image.new("RGB", (800, 600), color)
			buf = io.BytesIO()
			img.save(buf, format="JPEG")
			return buf.getvalue()

		# Products
		products_seed = [
			{
				"name": "Hydra Dew Moisturizer",
				"brand": brand_objs[0],
				"category": category_objs[0],
				"product_type": "skincare",
				"price": Decimal("1499.00"),
				"sale_price": Decimal("1299.00"),
				"is_featured": True,
				"is_bestseller": True,
				"is_new_arrival": False,
			},
			{
				"name": "Velvet Lip Tint",
				"brand": brand_objs[2],
				"category": category_objs[1],
				"product_type": "makeup",
				"price": Decimal("999.00"),
				"sale_price": None,
				"is_featured": True,
				"is_bestseller": False,
				"is_new_arrival": True,
			},
			{
				"name": "Silk Repair Shampoo",
				"brand": brand_objs[1],
				"category": category_objs[2],
				"product_type": "haircare",
				"price": Decimal("1199.00"),
				"sale_price": Decimal("1099.00"),
				"is_featured": False,
				"is_bestseller": True,
				"is_new_arrival": False,
			},
		]

		for idx, data in enumerate(products_seed, start=1):
			sku = f"EB-P-{idx:04d}"
			slug = slugify(data["name"]) + f"-{idx}"
			product, created = Product.objects.get_or_create(
				sku=sku,
				defaults=dict(
					name=data["name"],
					slug=slug,
					brand=data["brand"],
					category=data["category"],
					product_type=data["product_type"],
					description=f"{data['name']} — premium quality beauty essential.",
					short_description="Clean, gentle, effective.",
					ingredients="Aqua, Glycerin, Vitamin E",
					how_to_use="Apply as directed.",
					price=data["price"],
					sale_price=data["sale_price"],
					is_featured=data["is_featured"],
					is_bestseller=data["is_bestseller"],
					is_new_arrival=data["is_new_arrival"],
					is_active=True,
				),
			)
			# Ensure inventory
			Inventory.objects.get_or_create(product=product, defaults={"stock_quantity": 50})

			# One placeholder image per product
			if Image is not None and not product.images.exists():
				content = generate_image_bytes()
				if content:
					img_file = ContentFile(content, name=f"{slug}.jpg")
					ProductImage.objects.create(product=product, image=img_file, is_primary=True, order=0)

		# Banners
		if not Banner.objects.filter(banner_type="hero").exists():
			# Create up to 2 hero banners with generated images
			for i in range(1, 3):
				banner = Banner(
					title="Everest Beauty",
					subtitle="Discover authentic beauty from Nepal",
					banner_type="hero",
					is_active=True,
					order=i,
					start_date=timezone.now() - timezone.timedelta(days=1),
					end_date=timezone.now() + timezone.timedelta(days=30),
				)
				if Image is not None:
					content = generate_image_bytes(color=(240, 220, 255) if i == 1 else (220, 240, 255))
					if content:
						banner.image.save(f"hero_{i}.jpg", ContentFile(content), save=False)
				banner.save()

		self.stdout.write(self.style.SUCCESS("Sample data populated successfully."))
