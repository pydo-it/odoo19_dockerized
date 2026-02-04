# ==========================
# Variables
# ==========================
COMPOSE = docker compose
PROJECT = odoo19
ODOO_CONTAINER = odoo19-app
ODOO_PORT = ${ODOO_PORT}

# ==========================
# Main Targets
# ==========================

# Build the image
build:
	COMPOSE_BAKE=true $(COMPOSE) build

# Start everything in the background
up:
	COMPOSE_BAKE=true $(COMPOSE) up -d

# Stop everything
down:
	$(COMPOSE) down

# Rebuild everything from scratch
rebuild:
	$(COMPOSE) down
	COMPOSE_BAKE=true $(COMPOSE) build --no-cache
	COMPOSE_BAKE=true $(COMPOSE) up -d

# Show Odoo logs
logs:
	$(COMPOSE) logs -f odoo

# Enter the Odoo container
shell-odoo:
	$(COMPOSE) exec odoo bash

# Enter the Postgres container
shell-db:
	$(COMPOSE) exec db bash

# Restart only Odoo (without touching DB)
restart-odoo:
	$(COMPOSE) restart odoo

# Clean containers, volumes, and images of the project
clean:
	$(COMPOSE) down -v --remove-orphans

# Reset everything from scratch (FULL RESET)
reset:
	$(COMPOSE) down -v --remove-orphans
	COMPOSE_BAKE=true $(COMPOSE) build --no-cache
	COMPOSE_BAKE=true $(COMPOSE) up -d

# Reload all modules in a database
reload-db:
	@if [ -z "$(DB)" ]; then \
		echo "ERROR: You must provide the database name. Example:"; \
		echo "  make reload-db DB=my_database"; \
		exit 1; \
	fi
	docker exec -it $(ODOO_CONTAINER) /usr/bin/odoo -c /etc/odoo/odoo.conf -d $(DB) -u all --stop-after-init

# Reload a specific module
reload-module:
	@if [ -z "$(DB)" ] || [ -z "$(MODULE)" ]; then \
		echo "ERROR: You must provide the database and module. Example:"; \
		echo "  make reload-module DB=my_database MODULE=my_module"; \
		exit 1; \
	fi
	docker exec -it $(ODOO_CONTAINER) /usr/bin/odoo -c /etc/odoo/odoo.conf -d $(DB) -u $(MODULE) --stop-after-init

# Reload translations
reload-translations:
	@if [ -z "$(DB)" ]; then \
		echo "ERROR: You must provide the database name. Example:"; \
		echo "  make reload-translations DB=my_database"; \
		exit 1; \
	fi
	docker exec -it $(ODOO_CONTAINER) /usr/bin/odoo -c /etc/odoo/odoo.conf -d $(DB) -p $(ODOO_PORT) --no-http --load-language=es_MX --stop-after-init
