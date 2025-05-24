# Variables
include .env
SCRIPTS_DIR=./scripts
BACKUP_DIR=./backups
DB_CONTAINER_NAME=db
TIMESTAMP=$(shell date +%Y%m%d_%H%M%S)

# Run main server
.PHONY: dev
dev:
	poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Run pre-commit checks
.PHONY: precommit
precommit:
	pre-commit run --all-files

# Default target (runs the full setup)
.PHONY: setup-vault
setup-vault: generate-cnf generate-hcl init-vault

# Generate the Vault SAN configuration file
.PHONY: generate-cnf
generate-cnf:
	@echo "🔹 Generating Vault SAN configuration..."
	@$(SCRIPTS_DIR)/generate-cnf.sh
	@echo "✅ Vault SAN configuration generated successfully!"

# Generate the Vault HCL configuration file
.PHONY: generate-hcl
generate-hcl:
	@echo "🔹 Generating Vault HCL configuration..."
	@$(SCRIPTS_DIR)/generate-hcl-config.sh
	@echo "✅ Vault HCL configuration generated successfully!"

# Setup and start Vault
.PHONY: init-vault
init-vault:
	@echo "🔹 Setting up Vault..."
	@$(SCRIPTS_DIR)/setup-vault.sh -f docker-compose.yaml
	@echo "✅ Vault setup completed successfully!"

.PHONY: init-db
init-db:
	docker compose --profile db up -d
	alembic init alembic || true  # Avoid error if Alembic is already initialized
	alembic revision --autogenerate -m "Initial migration"
	alembic upgrade head
	@echo "✅ Database initialized and migrated successfully!"

# Run Alembic migration with a user-provided commit message
.PHONY: migrate-db
migrate-db:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: Please provide a commit message using 'make migrate-db MSG=\"your message\"'"; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(MSG)"
	alembic upgrade head
	@echo "✅ Migration completed successfully!"

# Rollback last migration (downgrade by 1 step)
.PHONY: rollback-db
rollback-db:
	alembic downgrade -1
	@echo "✅ Rolled back the last migration!"

# Downgrade to a specific revision
.PHONY: downgrade-db
downgrade-db:
	@if [ -z "$(r)" ]; then \
		echo "❌ Error: Please provide a revision using 'make downgrade -r <revision>'"; \
		exit 1; \
	fi
	alembic downgrade $(r)
	@echo "✅ Downgraded to revision $(r)!"

# Reset the database (downgrade to base and upgrade to latest)
.PHONY: reset-db
reset-db:
	alembic downgrade base
	alembic upgrade head
	@echo "✅ Database reset to the latest state!"


# Backup the database to a .sql file
.PHONY: backup-db
backup-db:
	@echo "Creating encrypted backup..."
	$(shell mkdir -p $(BACKUP_DIR))
	docker exec -i $(DB_CONTAINER_NAME) pg_dump -U $(DB_USER) -d $(DB_NAME) | \
		gpg --yes --batch --passphrase "$(DB_BACKUP_PASSPHRASE)" --symmetric --cipher-algo AES256 \
		-o $(BACKUP_DIR)/$(DB_NAME)_$(TIMESTAMP).sql.gpg
	@chmod 600 $(BACKUP_DIR)/$(DB_NAME)_$(TIMESTAMP).sql.gpg
	@echo "Encrypted backup saved to $(BACKUP_DIR)/$(DB_NAME)_$(TIMESTAMP).sql.gpg"

# Restore the database from a .sql file
.PHONY: restore-db
restore-db:
	@echo "Restoring encrypted backup..."
	@read -p "Enter the encrypted backup file name to restore (located in $(BACKUP_DIR)): " file && \
	gpg --quiet --batch --yes --passphrase "$(DB_BACKUP_PASSPHRASE)" --decrypt $(BACKUP_DIR)/$$file | \
	docker exec -i $(DB_CONTAINER_NAME) psql -U $(DB_USER) -d $(DB_NAME)
	@echo "Restore completed."

# List all backups
.PHONY: list-backups-db
list-backups-db:
	@echo "Available backups:"
	@ls $(BACKUP_DIR)

# Clean all backups
.PHONY: clean-backups-db
clean-backups-db:
	@echo "Cleaning all backups..."
	rm -rf $(BACKUP_DIR)/*.sql
	@echo "All backups deleted."

# Drop the database
.PHONY: drop-db
drop-db:
	@echo "❌ Dropping database $(DB_NAME)..."
	docker exec -i $(DB_CONTAINER_NAME) psql -U $(DB_USER) -d postgres -c "DROP DATABASE IF EXISTS $(DB_NAME);"
	docker exec -i $(DB_CONTAINER_NAME) psql -U $(DB_USER) -d postgres -c "CREATE DATABASE $(DB_NAME);"
	@echo "✅ Database $(DB_NAME) dropped and recreated."
