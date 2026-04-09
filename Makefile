# Todo-Crud — developer Makefile
#
# Test Impact Analysis (TIA) gives fast local feedback by running only the
# tests related to files you've changed. CI (CI=true) always falls back to
# running the full suite — the "Safety Latch" — so nothing escapes to main.

.PHONY: test test-tia test-backend test-frontend

# Full suite (what CI runs)
test: test-backend test-frontend

test-backend:
	cd backend && pytest

test-frontend:
	cd frontend && npx vitest run

# Test Impact Analysis — fast local feedback on what you changed.
# On CI, runs the full suite instead (Safety Latch).
test-tia:
	@if [ "$$CI" = "true" ]; then \
		echo "CI Safety Latch: running full suite"; \
		$(MAKE) test; \
	else \
		CHANGED=$$(git diff --name-only origin/main...HEAD 2>/dev/null; git diff --name-only HEAD 2>/dev/null) ; \
		BACKEND_CHANGED=$$(echo "$$CHANGED" | grep -E '^backend/.*\.py$$' || true) ; \
		FRONTEND_CHANGED=$$(echo "$$CHANGED" | grep -E '^frontend/src/.*\.ts$$' || true) ; \
		if [ -n "$$BACKEND_CHANGED" ]; then \
			echo "TIA: backend files changed, running backend suite"; \
			cd backend && pytest ; \
		else \
			echo "TIA: no backend source changes, skipping backend tests"; \
		fi ; \
		if [ -n "$$FRONTEND_CHANGED" ]; then \
			echo "TIA: frontend files changed, running affected vitest"; \
			cd frontend && npx vitest run --changed origin/main ; \
		else \
			echo "TIA: no frontend source changes, skipping frontend tests"; \
		fi ; \
	fi
