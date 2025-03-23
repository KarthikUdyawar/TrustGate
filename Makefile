# Variables
SCRIPTS_DIR=./scripts

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
.PHONY: migrate
migrate:
	@if [ -z "$(m)" ]; then \
		echo "❌ Error: Please provide a commit message using 'make migrate -m \"your message\"'"; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(m)"
	alembic upgrade head
	@echo "✅ Migration completed successfully!"

# Rollback last migration (downgrade by 1 step)
.PHONY: rollback
rollback:
	alembic downgrade -1
	@echo "✅ Rolled back the last migration!"

# Downgrade to a specific revision
.PHONY: downgrade
downgrade:
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

# Show migration history
.PHONY: history
history:
	alembic history

# Show the current database version
.PHONY: current
current:
	alembic current
