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
